import copy
import json
import re
import tempfile
import unittest
from pathlib import Path

from analyze import SECTIONS, initialize, inventory, render, safe_payload, validate


class AnalysisTests(unittest.TestCase):
    def fixture(self):
        manifest = {"root": {"id": "app", "name": "app", "revision": "fixture", "dirty": False}, "scanErrors": [], "files": [{"id": "app:main.ts", "repo": "app", "path": "main.ts", "kind": "file", "sha256": "fixture", "status": "pending", "reason": "", "entities": []}]}
        data = initialize([manifest], "Test fixture")
        data["files"][0] = dict(data["files"][0], status="reviewed", reason="Reviewed all registered entry points")
        data["evidence"] = [{"id": "EV1", "file": "app:main.ts", "startLine": 1, "endLine": 3, "method": "source inspection", "snapshot": "fixture"}]
        data["entities"] = [{"id": "ENTRY", "kind": "symbol", "repo": "app", "name": "entry", "summary": "Fixture entry", "status": "verified", "evidence": ["EV1"], "details": {"signature": "entry()"}}]
        data["diagrams"] = [{"id": "ARCH", "type": "architecture", "name": "Fixture architecture", "summary": "One component fixture", "status": "verified", "evidence": ["EV1"], "features": [], "nodes": [{"id": "ENTRY", "entity": "ENTRY", "label": "Entry"}], "edges": []}]
        data["sections"] = [{"id": section, "title": section, "summary": "Fixture scope", "status": "not-applicable", "reason": "No such domain in this unit fixture", "entities": [], "evidence": []} for section in SECTIONS]
        data["discoveries"] = [{"id": "D1", "scope": "app:main.ts", "method": "fixture parser", "reason": "Matched exact entry", "disposition": "mapped", "entities": ["ENTRY"], "evidence": ["EV1"]}]
        data["checks"] = [{"id": "C1", "scope": "app", "status": "passed", "result": "1 of 1 entry points reconciled", "evidence": ["EV1"]}]
        data["gaps"] = []
        return data, manifest

    def test_reconciled_fixture(self):
        data, manifest = self.fixture()
        self.assertEqual(validate(data, [manifest])["issues"], [])

    def test_omission_cannot_pass(self):
        data, manifest = self.fixture()
        data["files"] = []
        self.assertIn("OMITTED_FILE", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_duplicate_and_dangling(self):
        data, manifest = self.fixture()
        data["entities"].append(copy.deepcopy(data["entities"][0]))
        data["entities"][0]["evidence"] = ["missing"]
        data["entities"][1]["evidence"] = ["missing"]
        codes = {item["code"] for item in validate(data, [manifest])["issues"]}
        self.assertTrue({"DUPLICATE", "DANGLING"}.issubset(codes))

    def test_missing_manifest_is_not_complete(self):
        data, unused = self.fixture()
        self.assertEqual(validate(data)["status"], "incomplete")

    def test_snapshot_change(self):
        data, manifest = self.fixture()
        data["files"][0]["sha256"] = "changed"
        self.assertIn("SNAPSHOT", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_broken_chain(self):
        data, manifest = self.fixture()
        data["entities"].append(dict(data["entities"][0], id="OTHER"))
        data["chains"] = [{"id": "CHAIN", "status": "verified", "steps": ["ENTRY", "OTHER"], "relations": [], "evidence": ["EV1"], "trigger": "entry", "outcome": "done", "alternatives": []}]
        self.assertIn("BROKEN_CHAIN", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_column_accounting(self):
        data, manifest = self.fixture()
        data["entities"].append({"id": "TABLE", "kind": "table", "repo": "app", "name": "rows", "summary": "Fixture table", "status": "verified", "evidence": ["EV1"], "details": {"columns": ["MISSING"]}})
        codes = {item["code"] for item in validate(data, [manifest])["issues"]}
        self.assertTrue({"DANGLING", "DETAIL_FIELD", "COLUMN_PARENT"}.issubset(codes))

    def test_zero_denominator_is_not_100(self):
        data = initialize([], "Empty")
        self.assertIsNone(validate(data)["metrics"]["fileReviewPercent"])

    def test_payload_cannot_close_script(self):
        value = safe_payload({"text": "</script><img onerror=alert(1)>", "unicode": "\u2028"})
        self.assertNotIn("<", value)
        self.assertIn("\\u003c", value)

    def test_inventory_hidden_files_secrets_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".hidden.ts").write_text("export const enabled = true;", encoding="utf-8")
            (root / ".env").write_text("SECRET=fixture", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "link").symlink_to(root)
            result = inventory(root, "app")
            records = {item["path"]: item for item in result["files"]}
            self.assertIn(".hidden.ts", records)
            self.assertEqual(records[".env"]["status"], "excluded")
            self.assertNotIn("sha256", records[".env"])
            self.assertEqual(records["link"]["status"], "blocked")
            self.assertEqual(records["node_modules"]["kind"], "directory")

    def test_multi_root_same_path(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for directory in (first, second):
                (Path(directory) / "main.ts").write_text("export {};", encoding="utf-8")
            data = initialize([inventory(first, "ui"), inventory(second, "api")], "Combined")
            self.assertEqual({item["id"] for item in data["files"]}, {"ui:main.ts", "api:main.ts"})

    def test_invalid_record_does_not_crash(self):
        data, manifest = self.fixture()
        data["entities"].append(None)
        self.assertIn("ID", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_missing_architecture_cannot_pass(self):
        data, manifest = self.fixture()
        data["diagrams"] = []
        self.assertIn("DIAGRAM_COVERAGE", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_diagram_dangling_endpoint(self):
        data, manifest = self.fixture()
        data["diagrams"][0]["edges"] = [{"from": "ENTRY", "to": "MISSING", "label": "bad"}]
        self.assertIn("DIAGRAM_EDGE", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_explanation_is_required(self):
        data, manifest = self.fixture()
        record = data["entities"][0]
        record["kind"] = "api"
        codes = {item["code"] for item in validate(data, [manifest])["issues"]}
        self.assertIn("EXPLANATION", codes)
        record["explanation"] = {"purpose": "Fixture purpose", "howItWorks": ["Fixture step"], "example": "Illustrative example", "failure": "Fixture failure", "boundaries": "Fixture only", "terms": [], "evidence": ["EV1"]}
        self.assertNotIn("EXPLANATION", {item["code"] for item in validate(data, [manifest])["issues"]})
        record["explanation"]["howItWorks"] = [" "]
        self.assertIn("EXPLANATION", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_example_diagrams_fields_and_explanations(self):
        from make_example import example
        data, manifest = example()
        self.assertEqual({item["code"] for item in validate(data, [manifest])["issues"]}, {"OPEN_GAP", "UNVERIFIED"})
        self.assertEqual(len(data["diagrams"]), 7)
        self.assertEqual(sum(record["kind"] == "column" for record in data["entities"]), 7)

    def test_er_columns_must_belong_to_endpoint_table(self):
        from make_example import example
        data, manifest = example()
        diagram = next(record for record in data["diagrams"] if record["type"] == "er")
        diagram["edges"][0]["sourceColumns"] = ["COL-ID"]
        self.assertIn("ER_COLUMN", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_equal_counts_cannot_hide_different_candidates(self):
        data, manifest = self.fixture()
        data["checks"][0].update(expectedIds=["ENTRY"], observedIds=["OTHER"], paginationComplete=False)
        codes = {item["code"] for item in validate(data, [manifest])["issues"]}
        self.assertTrue({"CANDIDATE_SET", "CHECK_INCOMPLETE"}.issubset(codes))
        data["checks"][0].update(observedIds=["ENTRY"], paginationComplete=True)
        self.assertEqual(validate(data, [manifest])["issues"], [])

    def test_complete_safe_offline_render(self):
        data, manifest = self.fixture()
        data["project"]["title"] = '</script><img src=x onerror="alert(1)">'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "docs" / "report.html"
            receipt = render(data, [manifest], output)
            text = output.read_text(encoding="utf-8")
            self.assertEqual(receipt["issues"], [])
            for marker in ("__ANALYSIS_PAYLOAD__", "__MERMAID_BUNDLE__", "__DIAGRAM_VIEWER__", "__EDITORIAL_STYLES__"):
                self.assertNotIn(marker, text)
            payload = re.search(r'<script id="analysis-data" type="application/json">(.*?)</script>', text, re.DOTALL).group(1)
            self.assertNotIn("<", payload)
            restored = json.loads(payload)
            self.assertEqual(restored["entities"], data["entities"])
            self.assertEqual(restored["project"]["title"], data["project"]["title"])

    def integration_fixture(self):
        data, frontend = self.fixture()
        backend = {"root": {"id": "backend", "name": "backend", "revision": "fixture-backend", "dirty": False}, "scanErrors": [], "files": [{"id": "backend:main.py", "repo": "backend", "path": "main.py", "kind": "file", "sha256": "fixture-backend", "status": "pending", "reason": "", "entities": []}]}
        data["roots"].append(backend["root"])
        data["files"].append(dict(backend["files"][0], status="reviewed", reason="Fixture consumer inspected"))
        data["evidence"].append({"id": "EV2", "file": "backend:main.py", "startLine": 1, "endLine": 3, "method": "fixture source inspection", "snapshot": "fixture-backend"})
        data["entities"].append(dict(data["entities"][0], id="BACKEND-ENTRY", repo="backend", evidence=["EV2"]))
        observations = {
            "identity": ("POST /api/v1/orders", "POST /api/v1/orders"),
            "payload": ("amountMinor integer; currency string", "amountMinor integer; currency string"),
            "authorization": ("Bearer credential with orders:create", "requires orders:create"),
            "outcome": ("expects 201 and orderId string", "returns 201 and orderId string"),
            "failure": ("handles 400/409 without automatic retry", "returns 400/409 before committing"),
            "consistency": ("treats 201 as committed", "sends 201 after transaction commit"),
        }
        contract = {"environment": "isolated test fixture", "versionContext": "frontend fixture + backend fixture-backend", "producerEvidence": ["EV1"], "consumerEvidence": ["EV2"], "dimensions": {aspect: {"producer": producer, "consumer": consumer, "status": "compatible", "reason": "Paired authored fixture observations agree", "evidence": ["EV1", "EV2"]} for aspect, (producer, consumer) in observations.items()}}
        data["relations"] = [{"id": "BOUNDARY", "from": "ENTRY", "to": "BACKEND-ENTRY", "kind": "HTTP_CALLS", "label": "Fixture order request", "status": "verified", "evidence": ["EV1", "EV2"], "contract": contract}]
        return data, [frontend, backend]

    def test_cross_repo_relation_requires_contract(self):
        data, manifests = self.integration_fixture()
        del data["relations"][0]["contract"]
        self.assertIn("INTEGRATION_CONTRACT", {item["code"] for item in validate(data, manifests)["issues"]})

    def test_paired_cross_language_contract_reconciles(self):
        data, manifests = self.integration_fixture()
        self.assertEqual(validate(data, manifests)["issues"], [])

    def test_contract_unit_mismatch_and_unknown_are_not_complete(self):
        data, manifests = self.integration_fixture()
        dimensions = data["relations"][0]["contract"]["dimensions"]
        dimensions["payload"].update(consumer="amount major currency units", status="mismatch", reason="No unit conversion found")
        dimensions["consistency"]["status"] = "unknown"
        codes = {item["code"] for item in validate(data, manifests)["issues"]}
        self.assertTrue({"INTEGRATION_MISMATCH", "INTEGRATION_UNVERIFIED"}.issubset(codes))

    def test_contract_cannot_use_caller_evidence_for_consumer(self):
        data, manifests = self.integration_fixture()
        data["relations"][0]["contract"]["consumerEvidence"] = ["EV1"]
        self.assertIn("INTEGRATION_EVIDENCE", {item["code"] for item in validate(data, manifests)["issues"]})

    def test_contract_missing_dimension_or_evidence(self):
        data, manifests = self.integration_fixture()
        contract = data["relations"][0]["contract"]
        del contract["dimensions"]["failure"]
        contract["producerEvidence"] = []
        codes = {item["code"] for item in validate(data, manifests)["issues"]}
        self.assertTrue({"INTEGRATION_DIMENSION", "MISSING_REFERENCE"}.issubset(codes))

    def test_same_repo_explicit_boundary_requires_contract(self):
        data, manifest = self.fixture()
        data["entities"].append(dict(data["entities"][0], id="OTHER"))
        data["relations"] = [{"id": "BOUNDARY", "from": "ENTRY", "to": "OTHER", "kind": "PUBLISHES", "label": "Local event boundary", "status": "verified", "evidence": ["EV1"], "boundary": True}]
        self.assertIn("INTEGRATION_CONTRACT", {item["code"] for item in validate(data, [manifest])["issues"]})

    def test_documented_incompatibility_is_not_analysis_failure(self):
        data, manifests = self.integration_fixture()
        data["entities"].append({"id": "UNIT-RISK", "kind": "risk", "repo": "backend", "name": "Amount unit incompatibility", "summary": "Fixture uses different currency units", "status": "verified", "evidence": ["EV1", "EV2"], "details": {"businessImpact": "Amount is interpreted at a different scale"}})
        data["relations"][0]["contract"]["dimensions"]["payload"].update(status="mismatch", consumer="amount major currency units", finding="UNIT-RISK", reason="Unit conversion absent in fixture")
        receipt = validate(data, manifests)
        self.assertEqual(receipt["issues"], [])
        self.assertTrue(any(item["subject"] == "UNIT-RISK" for item in receipt["limitations"]))

    def test_mismatch_cannot_be_closed_with_unverified_finding(self):
        data, manifests = self.integration_fixture()
        data["relations"][0]["contract"]["dimensions"]["payload"].update(status="mismatch", finding="ENTRY")
        self.assertIn("INTEGRATION_MISMATCH", {item["code"] for item in validate(data, manifests)["issues"]})


if __name__ == "__main__":
    unittest.main()