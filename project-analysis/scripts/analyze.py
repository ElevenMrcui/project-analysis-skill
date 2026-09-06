import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SECTIONS = (
    "scope", "architecture", "features", "frontend", "api", "data", "chains",
    "jobs", "configuration", "security", "testing", "delivery", "operations",
    "dependencies", "risks", "coverage",
)
KINDS = (
    "feature", "page", "api", "symbol", "table", "column", "view", "routine",
    "trigger", "index", "constraint", "sequence", "partition", "enum", "store",
    "job", "event", "config", "flag", "integration", "component", "test",
    "deployment", "dependency", "risk", "asset", "other",
)
STATES = ("verified", "inferred", "unknown", "not-applicable")
EXPLANATION_KINDS = ("feature", "api", "table", "job")
DIAGRAM_TYPES = ("architecture", "function-flow", "detail-flow", "sequence", "dataflow", "er", "lifecycle")
REQUIRED_DETAILS = {
    "feature": ("actors", "trigger", "rules", "inputs", "outputs", "errors", "permissions", "sideEffects", "tests"),
    "page": ("route", "actions", "states", "permissions"),
    "api": ("protocol", "operation", "request", "response", "errors", "authorization", "consumers"),
    "table": ("qualifiedName", "columns", "keys", "indexes", "lifecycle", "readers", "writers"),
    "column": ("parent", "dataType", "nullable", "default", "constraints", "sensitivity", "lineage"),
    "job": ("trigger", "inputs", "outputs", "retry", "idempotency", "failure"),
    "event": ("channel", "schema", "producers", "consumers", "delivery", "failure"),
}
PRUNED = {".git": "Git internal metadata", "node_modules": "Installed dependencies; inspect lockfile and vendored patches separately", ".venv": "Installed Python environment", "venv": "Possible Python environment; verify exclusion"}
LANGUAGES = {
    "JavaScript/TypeScript": ".js .jsx .mjs .cjs .ts .tsx .vue .svelte",
    "Python": ".py .pyi .ipynb", "Java/Kotlin/Scala": ".java .kt .kts .scala",
    ".NET": ".cs .fs .vb .csproj .fsproj .sln .razor", "Go": ".go",
    "Rust": ".rs", "C/C++": ".c .h .cc .cpp .hpp .cxx", "PHP": ".php",
    "Ruby": ".rb .rake .gemspec", "Swift/Objective-C": ".swift .m .mm",
    "Dart": ".dart", "SQL": ".sql .ddl", "R": ".r .rmd",
    "Shell/PowerShell": ".sh .bash .zsh .ps1", "Elixir/Erlang": ".ex .exs .erl .hrl",
    "Lua": ".lua", "Haskell": ".hs .lhs", "Clojure": ".clj .cljs .cljc",
    "Web": ".html .css .scss .less", "Configuration": ".json .yaml .yml .toml .xml .ini .tf .hcl .proto .graphql .gql",
    "Documentation": ".md .txt .rst .adoc",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def write_atomic(path, content):
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".analysis-", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_json(path, value):
    write_atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def git_value(root, *arguments):
    try:
        result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, timeout=15, check=False)
        return result.stdout.decode("utf-8", errors="replace").strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def language_for(path):
    suffix = Path(path).suffix.lower()
    return next((name for name, extensions in LANGUAGES.items() if suffix in extensions.split()), "Other/unknown")


def inventory(root, repo):
    source = Path(root).resolve(strict=True)
    if not source.is_dir():
        raise ValueError("Source root must be a directory")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", repo):
        raise ValueError("Repository alias must use letters, digits, underscore or hyphen")
    records, errors = [], []

    def walk(directory):
        try:
            children = sorted(directory.iterdir())
        except OSError as error:
            errors.append({"path": directory.relative_to(source).as_posix(), "error": str(error)})
            return
        for child in children:
            relative = child.relative_to(source).as_posix()
            record = {"id": repo + ":" + relative, "repo": repo, "path": relative, "status": "pending", "reason": "", "entities": [], "language": language_for(relative)}
            try:
                if child.is_symlink():
                    record.update(kind="symlink", status="blocked", reason="Symlink not followed; review target scope explicitly")
                elif child.is_dir():
                    if child.name in PRUNED or relative == "docs/project-analysis":
                        record.update(kind="directory", status="excluded", reason=PRUNED.get(child.name, "Generated analysis artifacts"))
                    else:
                        walk(child)
                        continue
                elif child.is_file():
                    record.update(kind="file", bytes=child.stat().st_size)
                    sensitive = child.name.startswith(".env") or child.suffix.lower() in (".pem", ".key", ".p12", ".pfx") or child.name in ("id_rsa", "id_ed25519")
                    if sensitive:
                        record.update(status="excluded", reason="Potential secrets: content not read or hashed")
                    elif relative == "docs/project-analysis.html":
                        record.update(status="excluded", reason="Generated analysis report")
                    else:
                        digest = hashlib.sha256()
                        with child.open("rb") as stream:
                            while True:
                                chunk = stream.read(1024 * 1024)
                                if not chunk:
                                    break
                                digest.update(chunk)
                        record["sha256"] = digest.hexdigest()
                else:
                    record.update(kind="special", status="blocked", reason="Special filesystem entry not read")
            except OSError as error:
                record.update(kind=record.get("kind", "unknown"), status="blocked", reason=str(error))
            records.append(record)

    walk(source)
    revision = git_value(source, "rev-parse", "HEAD")
    worktree = git_value(source, "status", "--porcelain", "--untracked-files=normal")
    return {"schemaVersion": 1, "generatedAt": now(), "root": {"id": repo, "name": source.name, "revision": revision or "unavailable", "dirty": bool(worktree) if worktree is not None else None}, "files": records, "scanErrors": errors}


def initialize(manifests, title):
    aliases = [manifest["root"]["id"] for manifest in manifests]
    if len(set(aliases)) != len(aliases):
        raise ValueError("Duplicate repository aliases")
    return {
        "schemaVersion": 1,
        "project": {"title": title, "description": "Analysis in progress", "locale": "zh-CN", "generatedAt": now(), "example": False},
        "roots": [manifest["root"] for manifest in manifests],
        "files": [record for manifest in manifests for record in manifest["files"]],
        "entities": [], "relations": [], "chains": [], "diagrams": [], "evidence": [], "discoveries": [], "checks": [],
        "sections": [{"id": section, "title": section.title(), "status": "unknown", "summary": "Not analyzed", "entities": [], "evidence": []} for section in SECTIONS],
        "gaps": [{"id": "G-SCOPE", "status": "open", "summary": "Semantic discovery and independent reconciliation have not been performed", "nextAction": "Complete all discovery scopes and record evidence"}],
    }


def validate(data, manifests=()):
    issues, limitations = [], []

    def issue(code, subject, message):
        issues.append({"code": code, "subject": subject, "message": message})

    if not isinstance(data, dict) or data.get("schemaVersion") != 1:
        return {"status": "incomplete", "issues": [{"code": "SCHEMA", "subject": "root", "message": "Expected schemaVersion 1 object"}], "limitations": [], "metrics": {}}
    if not isinstance(data.get("project"), dict) or not data["project"].get("title"):
        issue("PROJECT", "project", "Project title is required")
    collections = {}
    for name in ("roots", "files", "entities", "relations", "chains", "diagrams", "evidence", "discoveries", "checks", "sections", "gaps"):
        records = data.get(name)
        if not isinstance(records, list):
            issue("SCHEMA", name, "Expected an array")
            records = []
        lookup = {}
        for index, record in enumerate(records):
            if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
                issue("ID", name + ":" + str(index), "Every record needs a nonempty string ID")
                continue
            identifier = record["id"]
            if identifier in lookup:
                issue("DUPLICATE", name + ":" + identifier, "Duplicate ID")
            lookup[identifier] = record
        collections[name] = lookup

    def refs(record, field, collection, required=False):
        values = record.get(field, [])
        if not isinstance(values, list):
            issue("REFERENCE_TYPE", record["id"], field + " must be an array")
            return
        if required and not values:
            issue("MISSING_REFERENCE", record["id"], field + " must not be empty")
        for value in values:
            if not isinstance(value, str) or value not in collections[collection]:
                issue("DANGLING", record["id"], field + " references missing " + str(value))

    roots = collections["roots"]
    if not roots:
        issue("ROOTS", "roots", "At least one declared source root is required")
    if not manifests:
        issue("NO_MANIFEST", "files", "Independent inventories were not supplied")
    expected_files, expected_roots = {}, set()
    for manifest in manifests:
        alias = manifest["root"]["id"]
        if alias in expected_roots:
            issue("DUPLICATE_ROOT", alias, "Duplicate independent inventory")
        expected_roots.add(alias)
        if roots.get(alias) != manifest["root"]:
            issue("SNAPSHOT", alias, "Root metadata differs from independent inventory")
        for error in manifest.get("scanErrors", []):
            issue("SCAN_ERROR", alias, str(error))
        for record in manifest["files"]:
            if record["id"] in expected_files:
                issue("DUPLICATE_FILE", record["id"], "Repeated manifest entry")
            expected_files[record["id"]] = record
    for alias in set(roots) - expected_roots:
        issue("MISSING_INVENTORY", alias, "No independent manifest for declared root")
    for identifier in sorted(set(expected_files) - set(collections["files"])):
        issue("OMITTED_FILE", identifier, "Manifest entry missing from report")
    if manifests:
        for identifier in sorted(set(collections["files"]) - set(expected_files)):
            issue("EXTRA_FILE", identifier, "Report entry not in independent manifest")
    for record in collections["files"].values():
        baseline = expected_files.get(record["id"])
        if baseline and any(record.get(field) != baseline.get(field) for field in ("repo", "path", "kind", "sha256")):
            issue("SNAPSHOT", record["id"], "File identity or digest differs from manifest")
        if record.get("repo") not in roots:
            issue("REPO", record["id"], "Unknown repository")
        if record.get("status") not in ("reviewed", "excluded", "blocked", "pending"):
            issue("FILE_STATUS", record["id"], "Invalid file disposition")
        if record.get("status") in ("pending", "blocked"):
            issue("UNREVIEWED", record["id"], record.get("reason") or "File not reviewed")
        if record.get("status") in ("reviewed", "excluded") and not record.get("reason"):
            issue("FILE_REASON", record["id"], "Review or exclusion rationale required")
        if record.get("status") == "excluded":
            limitations.append({"subject": record["id"], "message": record.get("reason", "Excluded")})
        refs(record, "entities", "entities")

    for record in collections["evidence"].values():
        file_id = record.get("file")
        if file_id:
            if file_id not in collections["files"]:
                issue("EVIDENCE_FILE", record["id"], "Evidence file is not inventoried")
            if not isinstance(record.get("startLine"), int) or not isinstance(record.get("endLine"), int) or record.get("startLine", 0) < 1 or record.get("endLine", 0) < record.get("startLine", 1):
                issue("EVIDENCE_RANGE", record["id"], "Valid 1-based line range required")
        elif not record.get("artifact") or not record.get("locator"):
            issue("EVIDENCE_LOCATOR", record["id"], "File/range or artifact/locator required")
        if not record.get("method") or not record.get("snapshot"):
            issue("EVIDENCE_METHOD", record["id"], "Verification method and snapshot required")

    for name in ("entities", "relations", "chains", "diagrams", "sections"):
        for record in collections[name].values():
            if record.get("status") not in STATES:
                issue("STATUS", record["id"], "Invalid evidence status")
            if record.get("status") in ("inferred", "unknown"):
                issue("UNVERIFIED", record["id"], "Unverified claim")
            refs(record, "evidence", "evidence", required=record.get("status") == "verified")
            if record.get("status") == "not-applicable" and not record.get("reason"):
                issue("NA_REASON", record["id"], "Not-applicable rationale required")
    for record in collections["entities"].values():
        if record.get("kind") not in KINDS or not record.get("name") or not record.get("summary"):
            issue("ENTITY", record["id"], "Known kind, name and summary required")
        if record.get("repo") not in roots:
            issue("REPO", record["id"], "Entity repository is unknown")
        if record.get("kind") in EXPLANATION_KINDS and record.get("status") != "not-applicable":
            explanation = record.get("explanation")
            if not isinstance(explanation, dict):
                issue("EXPLANATION", record["id"], "缺少通俗讲解：用途、步骤、说明性示例、失败后果及适用边界")
            else:
                for field in ("purpose", "example", "failure", "boundaries"):
                    if not isinstance(explanation.get(field), str) or not explanation[field].strip():
                        issue("EXPLANATION", record["id"], "通俗讲解字段缺失或为空：" + field)
                steps = explanation.get("howItWorks")
                if not isinstance(steps, list) or not steps or any(not isinstance(step, str) or not step.strip() for step in steps):
                    issue("EXPLANATION", record["id"], "需要非空的中文操作步骤列表 howItWorks")
                terms = explanation.get("terms")
                if not isinstance(terms, list) or any(not isinstance(term, dict) or not isinstance(term.get("term"), str) or not term["term"].strip() or not isinstance(term.get("meaning"), str) or not term["meaning"].strip() for term in terms):
                    issue("EXPLANATION", record["id"], "术语表必须是含 term 和 meaning 的对象列表")
                refs({"id": record["id"], "evidence": explanation.get("evidence", [])}, "evidence", "evidence", record.get("status") == "verified")
        details = record.get("details")
        if not isinstance(details, dict) or not details:
            issue("DETAILS", record["id"], "Nonempty structured details required")
        else:
            for field in REQUIRED_DETAILS.get(record.get("kind"), ()):
                if field not in details or details[field] is None or details[field] == "":
                    issue("DETAIL_FIELD", record["id"], "Missing detailed field: " + field)
        if record.get("kind") == "table" and isinstance(details, dict):
            refs({"id": record["id"], "columns": details.get("columns", [])}, "columns", "entities", required=True)
            for column_id in details.get("columns", []) if isinstance(details.get("columns"), list) else []:
                column = collections["entities"].get(str(column_id), {})
                if column.get("kind") != "column" or column.get("details", {}).get("parent") != record["id"]:
                    issue("COLUMN_PARENT", record["id"], "Column ownership mismatch: " + str(column_id))
        if record.get("kind") == "column" and isinstance(details, dict):
            parent = collections["entities"].get(str(details.get("parent")), {})
            if parent.get("kind") != "table" or record["id"] not in parent.get("details", {}).get("columns", []):
                issue("TABLE_COLUMN", record["id"], "Parent table does not list this column")
    for record in collections["relations"].values():
        for field in ("from", "to"):
            refs({"id": record["id"], field: [record.get(field)]}, field, "entities", True)
        if not record.get("kind") or not record.get("label"):
            issue("RELATION", record["id"], "Relationship kind and label required")
        source = collections["entities"].get(str(record.get("from")), {})
        target = collections["entities"].get(str(record.get("to")), {})
        cross_repo = source.get("repo") and target.get("repo") and source["repo"] != target["repo"]
        if cross_repo or record.get("boundary") is True or "contract" in record:
            contract = record.get("contract")
            if not isinstance(contract, dict):
                issue("INTEGRATION_CONTRACT", record["id"], "跨仓库或显式系统边界缺少双方契约核对记录")
                continue
            for field in ("environment", "versionContext"):
                if not isinstance(contract.get(field), str) or not contract[field].strip():
                    issue("INTEGRATION_CONTEXT", record["id"], "缺少环境或版本适用范围：" + field)
            for field, endpoint in (("producerEvidence", source), ("consumerEvidence", target)):
                refs({"id": record["id"], field: contract.get(field, [])}, field, "evidence", True)
                evidence_ids = contract.get(field, [])
                if isinstance(evidence_ids, list):
                    for evidence_id in evidence_ids:
                        evidence = collections["evidence"].get(str(evidence_id), {})
                        evidence_file = collections["files"].get(str(evidence.get("file")), {})
                        if evidence_file and evidence_file.get("repo") != endpoint.get("repo"):
                            issue("INTEGRATION_EVIDENCE", record["id"], field + " 的源码证据不属于对应端仓库")
            dimensions = contract.get("dimensions")
            if not isinstance(dimensions, dict):
                issue("INTEGRATION_DIMENSION", record["id"], "需要逐项核对身份、字段、授权、结果、错误和一致性")
                continue
            for aspect in ("identity", "payload", "authorization", "outcome", "failure", "consistency"):
                comparison = dimensions.get(aspect)
                if not isinstance(comparison, dict):
                    issue("INTEGRATION_DIMENSION", record["id"], "缺少契约核对维度：" + aspect)
                    continue
                for field in ("producer", "consumer", "reason"):
                    if not isinstance(comparison.get(field), str) or not comparison[field].strip():
                        issue("INTEGRATION_DIMENSION", record["id"], aspect + " 缺少双方观察或判断依据：" + field)
                refs({"id": record["id"], "evidence": comparison.get("evidence", [])}, "evidence", "evidence", True)
                if comparison.get("status") == "mismatch":
                    finding = collections["entities"].get(str(comparison.get("finding")), {})
                    finding_details = finding.get("details")
                    impact = finding_details.get("businessImpact") if isinstance(finding_details, dict) else None
                    if finding.get("kind") == "risk" and finding.get("status") == "verified" and isinstance(impact, str) and impact.strip():
                        limitations.append({"subject": finding["id"], "message": record["id"] + " 的 " + aspect + " 已核实不兼容：" + impact})
                    else:
                        issue("INTEGRATION_MISMATCH", record["id"], "双方契约冲突尚未关联含业务后果的已核实风险：" + aspect)
                elif comparison.get("status") not in ("compatible", "not-applicable"):
                    issue("INTEGRATION_UNVERIFIED", record["id"], "双方契约尚未核实：" + aspect)
    for record in collections["chains"].values():
        refs(record, "steps", "entities", True)
        refs(record, "relations", "relations", True)
        steps = record.get("steps", [])
        if isinstance(steps, list):
            edges = [collections["relations"].get(str(identifier), {}) for identifier in record.get("relations", [])] if isinstance(record.get("relations", []), list) else []
            for source, target in zip(steps, steps[1:]):
                if not any(edge.get("from") == source and edge.get("to") == target for edge in edges):
                    issue("BROKEN_CHAIN", record["id"], str(source) + " -> " + str(target) + " lacks an authored directed relation")
        for field in ("trigger", "outcome", "alternatives"):
            if field not in record:
                issue("CHAIN_DETAIL", record["id"], "Missing " + field)
    diagrams = list(collections["diagrams"].values())
    for record in diagrams:
        if record.get("type") not in DIAGRAM_TYPES or not record.get("name") or not record.get("summary"):
            issue("DIAGRAM", record["id"], "Diagram type, Chinese name and summary required")
        refs(record, "features", "entities")
        nodes = record.get("nodes", [])
        edges = record.get("edges", [])
        if not isinstance(nodes, list) or not nodes or not isinstance(edges, list):
            issue("DIAGRAM_MODEL", record["id"], "Nonempty nodes and an edges array required")
            continue
        identifiers = set()
        for node in nodes:
            if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node.get("label"):
                issue("DIAGRAM_NODE", record["id"], "Node ID and label required")
                continue
            if node["id"] in identifiers:
                issue("DIAGRAM_NODE", record["id"], "Duplicate diagram node: " + node["id"])
            identifiers.add(node["id"])
            if node.get("entity"):
                refs({"id": record["id"], "entities": [node["entity"]]}, "entities", "entities", True)
            if record.get("type") == "er" and collections["entities"].get(str(node.get("entity")), {}).get("kind") != "table":
                issue("ER_TABLE", record["id"], "ER nodes must map to inventoried tables")
        for edge in edges:
            if not isinstance(edge, dict) or not isinstance(edge.get("from"), str) or not isinstance(edge.get("to"), str) or edge.get("from") not in identifiers or edge.get("to") not in identifiers:
                issue("DIAGRAM_EDGE", record["id"], "Diagram edge endpoint is missing")
                continue
            if not edge.get("label"):
                issue("DIAGRAM_EDGE", record["id"], "Edge meaning must be labelled")
            refs({"id": record["id"], "evidence": edge.get("evidence", [])}, "evidence", "evidence", True)
            if record.get("type") == "er":
                if edge.get("relationship") not in ("foreign-key", "logical", "inferred"):
                    issue("ER_RELATION", record["id"], "Declare foreign-key, logical or inferred relationship")
                if edge.get("relationship") == "inferred":
                    issue("UNVERIFIED", record["id"], "Inferred table relationship needs verification")
                if edge.get("sourceCardinality") not in ("one", "zero-or-one", "many", "one-or-many") or edge.get("targetCardinality") not in ("one", "zero-or-one", "many", "one-or-many"):
                    issue("ER_CARDINALITY", record["id"], "Explicit cardinalities required")
                for field in ("sourceColumns", "targetColumns"):
                    refs({"id": record["id"], field: edge.get(field, [])}, field, "entities", True)
                node_entities = {node["id"]: node.get("entity") for node in nodes if isinstance(node, dict) and isinstance(node.get("id"), str)}
                for endpoint, field in (("from", "sourceColumns"), ("to", "targetColumns")):
                    column_ids = edge.get(field, [])
                    if isinstance(column_ids, list):
                        for identifier in column_ids:
                            column = collections["entities"].get(str(identifier), {})
                            details = column.get("details")
                            if column.get("kind") != "column" or not isinstance(details, dict) or details.get("parent") != node_entities.get(edge[endpoint]):
                                issue("ER_COLUMN", record["id"], "关系字段不属于对应数据表：" + str(identifier))
                if isinstance(edge.get("sourceColumns"), list) and isinstance(edge.get("targetColumns"), list) and len(edge["sourceColumns"]) != len(edge["targetColumns"]):
                    issue("ER_COLUMN", record["id"], "关系两端的连接字段数量不一致")
    if collections["entities"] and not any(record.get("type") == "architecture" for record in diagrams):
        issue("DIAGRAM_COVERAGE", "architecture", "Project architecture diagram required")
    for record in collections["entities"].values():
        if record.get("kind") == "feature":
            for diagram_type in ("function-flow", "detail-flow"):
                if not any(diagram.get("type") == diagram_type and record["id"] in diagram.get("features", []) for diagram in diagrams):
                    issue("DIAGRAM_COVERAGE", record["id"], "Feature missing " + diagram_type)
        if record.get("kind") == "table" and not any(diagram.get("type") == "er" and any(isinstance(node, dict) and node.get("entity") == record["id"] for node in diagram.get("nodes", []) if isinstance(diagram.get("nodes"), list)) for diagram in diagrams):
            issue("DIAGRAM_COVERAGE", record["id"], "Table missing from ER diagram register")
    for section in SECTIONS:
        if section not in collections["sections"]:
            issue("MISSING_SECTION", section, "Required analysis domain not accounted for")
    for record in collections["sections"].values():
        refs(record, "entities", "entities")
        if not record.get("summary"):
            issue("SECTION_SUMMARY", record["id"], "Summary required")
    if not collections["discoveries"]:
        issue("DISCOVERY", "discoveries", "Independent semantic discovery ledger required")
    for record in collections["discoveries"].values():
        refs(record, "entities", "entities", record.get("disposition") == "mapped")
        refs(record, "evidence", "evidence", True)
        if record.get("disposition") not in ("mapped", "excluded", "false-positive", "not-applicable"):
            issue("UNRESOLVED_DISCOVERY", record["id"], "Candidate not reconciled")
        if not all(record.get(field) for field in ("scope", "method", "reason")):
            issue("DISCOVERY_PROVENANCE", record["id"], "Scope, method and disposition reason required")
        if record.get("disposition") == "excluded":
            limitations.append({"subject": record["id"], "message": record.get("reason", "Excluded candidate")})
    if not collections["checks"]:
        issue("CHECKS", "checks", "Discovery completeness and review checks required")
    for record in collections["checks"].values():
        refs(record, "evidence", "evidence", True)
        if record.get("status") not in ("passed", "not-applicable"):
            issue("CHECK_INCOMPLETE", record["id"], "Check not passed")
        if not record.get("scope") or not record.get("result"):
            issue("CHECK_RESULT", record["id"], "Scope and measured result required")
        if record.get("paginationComplete") is False:
            issue("CHECK_INCOMPLETE", record["id"], "发现结果未完成分页，不能确认已完整对账")
        if "expectedIds" in record or "observedIds" in record:
            expected, observed = record.get("expectedIds"), record.get("observedIds")
            if not isinstance(expected, list) or not isinstance(observed, list) or any(not isinstance(identifier, str) for identifier in expected + observed):
                issue("CANDIDATE_SET", record["id"], "expectedIds 与 observedIds 必须同时提供字符串列表")
            elif set(expected) != set(observed):
                issue("CANDIDATE_SET", record["id"], "候选 ID 不一致；缺失：" + str(sorted(set(expected) - set(observed))) + "；额外：" + str(sorted(set(observed) - set(expected))))
    for record in collections["gaps"].values():
        if record.get("status") != "resolved":
            issue("OPEN_GAP", record["id"], record.get("summary", "Unresolved gap"))
            if not record.get("nextAction"):
                issue("GAP_ACTION", record["id"], "Resolution action required")
        elif not record.get("resolution"):
            issue("GAP_RESOLUTION", record["id"], "Resolved gap needs resolution evidence description")
    files = list(collections["files"].values())
    eligible = [record for record in files if record.get("status") != "excluded"]
    reviewed = sum(record.get("status") == "reviewed" for record in eligible)
    candidates = list(collections["discoveries"].values())
    mapped = sum(record.get("disposition") == "mapped" for record in candidates)
    if data.get("project", {}).get("example"):
        limitations.append({"subject": "project", "message": "Synthetic demonstration, not a real project analysis"})
    return {"status": "incomplete" if issues else "reconciled-within-scope", "generatedAt": now(), "issues": issues, "limitations": limitations,
            "metrics": {"manifestEntries": len(expected_files), "reportedEntries": len(files), "eligibleFiles": len(eligible), "reviewedFiles": reviewed, "fileReviewPercent": round(100 * reviewed / len(eligible), 2) if eligible else None, "excludedEntries": len(files) - len(eligible), "entities": len(collections["entities"]), "discoveryCandidates": len(candidates), "mappedCandidates": mapped, "chains": len(collections["chains"]), "issues": len(issues)}}


def safe_payload(data):
    return json.dumps(data, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def render(data, manifests, output):
    template = Path(__file__).resolve().parent.parent / "assets" / "report.html"
    report = dict(data)
    report["validation"] = validate(data, manifests)
    bundle = (template.parent / "lucide.min.js").read_text(encoding="utf-8")
    mermaid = (template.parent / "mermaid.min.js").read_text(encoding="utf-8")
    diagram_viewer = (template.parent / "diagrams.js").read_text(encoding="utf-8")
    stylesheet = (template.parent / "editorial.css").read_text(encoding="utf-8")
    content = template.read_text(encoding="utf-8").replace("__EDITORIAL_STYLES__", stylesheet).replace("__LUCIDE_BUNDLE__", bundle).replace("__MERMAID_BUNDLE__", mermaid).replace("__DIAGRAM_VIEWER__", diagram_viewer).replace("__ANALYSIS_PAYLOAD__", safe_payload(report))
    write_atomic(output, content)
    return report["validation"]


def main():
    parser = argparse.ArgumentParser(description="Evidence-backed inventory, reconciliation and offline report tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("inventory")
    scan.add_argument("--root", required=True)
    scan.add_argument("--repo", required=True)
    scan.add_argument("--output", required=True)
    create = subparsers.add_parser("init")
    create.add_argument("--inventory", action="append", required=True)
    create.add_argument("--title", default="Project analysis")
    create.add_argument("--output", required=True)
    for command in ("validate", "render"):
        child = subparsers.add_parser(command)
        child.add_argument("--input", required=True)
        child.add_argument("--inventory", action="append", default=[])
        child.add_argument("--output", required=True)
    arguments = parser.parse_args()
    output = Path(arguments.output).absolute()
    if "docs" not in output.parts:
        parser.error("All generated outputs must be below the target workspace docs directory")
    if arguments.command == "inventory":
        value = inventory(arguments.root, arguments.repo)
        write_json(output, value)
        print(json.dumps({"entries": len(value["files"]), "scanErrors": len(value["scanErrors"])}))
        return 1 if value["scanErrors"] else 0
    manifests = [read_json(path) for path in arguments.inventory]
    if arguments.command == "init":
        if output.exists():
            parser.error("Refusing to overwrite an existing analysis dataset")
        write_json(output, initialize(manifests, arguments.title))
        return 0
    data = read_json(arguments.input)
    if arguments.command == "validate":
        result = validate(data, manifests)
        write_json(output, result)
        print(json.dumps({"status": result["status"], "issues": len(result["issues"])}))
        return 1 if result["issues"] else 0
    result = render(data, manifests, output)
    print(json.dumps({"output": str(output), "coverageStatus": result["status"]}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("Analysis tool error: " + str(error), file=sys.stderr)
        sys.exit(2)