# Analysis Data Contract, Version 1

The tool reads UTF-8 JSON. Preserve full records in `analysis.json`; HTML embeds the entire dataset and recomputes its validation receipt from the supplied independent manifests. All collections below are arrays, even when empty. IDs are nonempty strings, unique within their collection; use namespaced stable IDs, not display names.

## Top-Level Collections

| Key | Required content |
| --- | --- |
| `schemaVersion` | Integer `1` |
| `project` | Chinese `title` and `description`, `locale` default `zh-CN`, `generatedAt`, `example` boolean; original identifiers remain unchanged |
| `roots` | Exact root metadata copied from each independent manifest: `id`, `name`, `revision`, `dirty` |
| `files` | One unchanged identity/digest per manifest entry plus review disposition |
| `entities` | Every feature, interface, symbol, data object/column, task, setting and supporting object |
| `relations` | Directed typed relationships with evidence |
| `chains` | Ordered entity paths with explicit relation IDs and alternative branches |
| `diagrams` | Typed architecture, feature/detail flow, sequence, dataflow, ER and lifecycle models; see [diagram contract](./diagrams-and-data.md) |
| `evidence` | Source/artifact locators and verification metadata |
| `discoveries` | Independent discovery candidates and final mappings/dispositions |
| `checks` | Recorded discovery/reconciliation/quality checks and actual outcomes |
| `sections` | All 16 analysis domains; no silent omission of an inapplicable domain |
| `gaps` | Unknowns, contradictions, access failures and remediation |

`validation` is generated at render time. Do not manually author a passing receipt. Additional top-level metadata remains in JSON export; put reader-facing extensions in entities/sections so they are also visible in the report and print output.

## File Record

```json
{
  "id": "api:src/orders.ts",
  "repo": "api",
  "path": "src/orders.ts",
  "kind": "file",
  "sha256": "digest-from-inventory",
  "language": "JavaScript/TypeScript",
  "status": "reviewed",
  "reason": "Reviewed route registration, validation, service calls and error handlers",
  "entities": ["api:orders:create"]
}
```

File statuses: `pending`, `reviewed`, `excluded`, `blocked`. `reason` is mandatory for reviewed/excluded records. Preserve excluded directory records: one directory record does **not** assert that every file beneath it was analyzed. Hashes establish snapshot identity only, not semantic review. A reviewed business source should link to its documented entities; files without entities need a specific role/explanation.

## Entity Record

```json
{
  "id": "api:orders:create",
  "kind": "api",
  "name": "POST /orders",
  "repo": "api",
  "module": "orders",
  "language": "TypeScript",
  "summary": "Creates an order after authorization and request validation",
  "status": "verified",
  "evidence": ["EV-ORDER-ROUTE"],
  "details": {
    "protocol": "HTTP",
    "operation": "POST /orders",
    "request": {"body": "Expand every property with type, requiredness and validation"},
    "response": {"201": "Expand every response field and semantics"},
    "errors": ["Enumerate actual domain and transport errors"],
    "authorization": "Record the actual policy",
    "consumers": ["web:orders:form"]
  }
}
```

The example is a shape, not evidence. Never paste its business claims into real reports.

It is abbreviated, not a passing full record. Features, APIs, tables and jobs additionally require the `explanation` object from [depth and clarity](./depth-and-clarity.md): Chinese purpose, operational steps, labelled illustrative example, failure consequence, boundaries, terms and evidence. The utility checks presence and references, not whether prose is actually comprehensible or factually true.

Supported `kind`: `feature`, `page`, `api`, `symbol`, `table`, `column`, `view`, `routine`, `trigger`, `index`, `constraint`, `sequence`, `partition`, `enum`, `store`, `job`, `event`, `config`, `flag`, `integration`, `component`, `test`, `deployment`, `dependency`, `risk`, `asset`, `other`. Extend unfamiliar object types via `other` plus `details.subtype`; preserve language-specific facts.

`status`: `verified`, `inferred`, `unknown`, `not-applicable`. Verified means inspected evidence supports this particular claim, not that the product is correct. Unknown/inferred records block the coverage gate but remain renderable. Not-applicable needs `reason`; it must not be used to relabel an inaccessible applicable feature.

### Mandatory Detail Fields

| Kind | Fields |
| --- | --- |
| feature | `actors`, `trigger`, `rules`, `inputs`, `outputs`, `errors`, `permissions`, `sideEffects`, `tests` |
| page | `route`, `actions`, `states`, `permissions` |
| api | `protocol`, `operation`, `request`, `response`, `errors`, `authorization`, `consumers` |
| table | `qualifiedName`, `columns` (column entity IDs), `keys`, `indexes`, `lifecycle`, `readers`, `writers` |
| column | `parent` (table ID), `dataType`, `nullable`, `default`, `constraints`, `sensitivity`, `lineage` |
| job | `trigger`, `inputs`, `outputs`, `retry`, `idempotency`, `failure` |
| event | `channel`, `schema`, `producers`, `consumers`, `delivery`, `failure` |

These are minimum fields, not a content ceiling. Also follow the playbook for flags, transaction/consistency boundaries, environment, error branches, operational behavior and complete data object attributes. Empty lists mean verified absence only; add a reason. For genuinely absent defaults use `"none"`; for unknown use `"unknown"` and mark the entity `unknown` with a gap. A string saying "unknown" inside a verified record cannot turn it into verified knowledge, even if a mechanical field-presence check accepts it.

Nested objects/arrays are rendered recursively. Do not substitute an unstructured blob for field-level metadata. Use strings for SQL/DDL snippets and plain paragraphs; the baseline renderer deliberately does not execute HTML or Markdown embedded in source text.

## Evidence

```json
{
  "id": "EV-ORDER-ROUTE",
  "file": "api:src/orders.ts",
  "startLine": 18,
  "endLine": 47,
  "method": "Source read and framework route registry comparison",
  "snapshot": "revision plus file digest",
  "note": "Specific assertion supported by this range"
}
```

Alternatively use `artifact` and `locator` for sanitized schema dumps, JSON pointers, diagram receipts, command logs or screenshots, with `method` and `snapshot`. `sourceUrl` is optional and must point to an existing verified source location, preferably pinned to a commit. Avoid tokenized URLs and credentials. The validator checks locator shape and references; it does not fetch URLs, inspect actual source lines or verify that the prose follows from them. The agent must perform those checks.

## Relations and Chains

```json
{
  "id": "REL-FORM-API",
  "from": "web:orders:form",
  "to": "api:orders:create",
  "kind": "HTTP_CALLS",
  "label": "POST /orders, authenticated JSON",
  "status": "verified",
  "evidence": ["EV-FORM-CLIENT", "EV-ORDER-ROUTE"]
}
```

Use exact relationships such as CALLS, HTTP_CALLS, PRODUCES, CONSUMES, READS, WRITES, TRANSFORMS, AUTHORIZES, DEPLOYS, CONFIGURES, TESTS or BELONGS_TO. Do not present logical/assumed relationships as physical foreign keys or runtime traffic.

```json
{
  "id": "CHAIN-CREATE-ORDER",
  "name": "Create order: accepted request",
  "status": "verified",
  "trigger": "Authorized customer submits the form",
  "steps": ["web:orders:form", "api:orders:create"],
  "relations": ["REL-FORM-API"],
  "outcome": "Continue with the actual persistence and response path",
  "alternatives": [{"condition": "Validation fails", "chain": "CHAIN-INVALID-ORDER", "result": "No persistence"}],
  "evidence": ["EV-FORM-CLIENT", "EV-ORDER-ROUTE"]
}
```

The validator requires a directed relation between every consecutive pair. Each node/edge still needs source review. The example is intentionally abbreviated; real end-to-end chains cannot stop at forwarding code. Branch references inside extension fields need manual cross-checking. For richer diagrams, add a `reportPath` to a section/entity pointing to `project-analysis/diagrams/<name>.html` relative to the main report; add typed IR/receipt paths in `details`.

## Discovery and Check Records

Discovery: `id`, `scope`, `method`, `reason`, `disposition`, `entities`, `evidence`. Disposition is `mapped`, `excluded`, `false-positive`, `not-applicable`, or unresolved. All candidates including false positives remain in the ledger. A single candidate may map to multiple entities; do not collapse an entire table's fields into one candidate.

Check: `id`, `scope`, `status`, `result`, `evidence`; recommended `domain`, `repo`, `command`, `toolVersion`, `expectedIds`, `observedIds`, `missingIds`, `extraIds`, `paginationComplete`, `runAt`, `environment`. Keep expected IDs sourced from independent raw discoveries. `passed` requires empty missing/extra sets and complete pagination, with an actual result. `not-applicable` requires evidence/reason in the result. Unrun checks cannot be passed.

Create a check for every root x applicable domain. Framework-native/AST extraction, code graph results, filesystem accounting and live metadata are separate checks. Equal counts are insufficient. Mechanical validation checks links and status fields, not the honesty or completeness of a manually supplied discovery universe.

## Sections and Gaps

Required section IDs: `scope`, `architecture`, `features`, `frontend`, `api`, `data`, `chains`, `jobs`, `configuration`, `security`, `testing`, `delivery`, `operations`, `dependencies`, `risks`, `coverage`.

Sections: `id`, `title`, `summary`, `status`, `entities`, `evidence`; optional `details`, `reason`, `reportPath`. Put substantial analysis into structured details, not a one-sentence summary. Use the minimum domain checklist and attach every relevant entity ID.

Gaps: `id`, `summary`, `status` (`open`/`resolved`), `nextAction`, optional owner/scope/severity/related IDs. Resolved gaps need `resolution` describing actual evidence. Preserve the history instead of deleting inconvenient gaps.

## Gate Semantics

- `validate` exit `0`: recorded manifests and references reconciled with no unresolved checked items. Label `reconciled-within-scope`, never `all-features-guaranteed`.
- `validate` exit `1`: incomplete analysis or structural defects; a JSON receipt is still written.
- Tool exit `2`: input/IO/usage error; fix the input, do not reinterpret it as an empty result.
- `render` exit `0`: HTML was written, even if the displayed coverage is incomplete. Read the coverage status separately.
- Zero denominators produce `null`, not 100%. Exclusions remain visible and are not counted as reviewed.
- Native parsers, SQL catalog reconciliation, line-level truth, secret scanning, semantic completeness and visual QA are agent responsibilities, not promises of this small utility.

## 跨系统契约扩展

跨仓库关系以及 `boundary: true` 的同仓库系统边界需要 `contract`。字段结构、六维核对方法和冲突处理见 [跨系统整合与业务全貌](./integration-and-synthesis.md)。校验器要求双方证据、环境版本、逐维观察与判断；不兼容项可以登记为有证据、有业务后果的已核实风险，不等同于产品正确或缺陷已修复。无证据和未核实边界仍阻止整合完成。扩展内容会保留在关系完整详情、JSON 和完整打印中。