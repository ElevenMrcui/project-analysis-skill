# Full-Scope Analysis Playbook

## 1. Scope Is a Contract

Record every root alias and revision, dirty state, analysis time, accepted exclusions, inaccessible systems, environment variants and analysis tools. Repositories with the same directory or package name remain distinct. Multi-root source may be outside the report workspace; all generated output remains inside the chosen report workspace's `docs` directory.

The filesystem manifest includes hidden files and does not silently obey `.gitignore`. Default directory exclusions are explicitly recorded: Git internals, installed Node dependencies and Python environments. Inspect each exclusion before accepting it, especially a directory merely named `venv`. Vendored/modified dependency source and patches may contain project behavior. Add such directories as separately inventoried roots when relevant. Do not infer source-language coverage from file extensions alone.

Identify nested Git repositories, `.gitmodules`, LFS pointers, archives, binary packages, source generation and template compilation. The bundled scanner does not unpack archives, follow symlinks or understand Git submodule/LFS availability. These require explicit check records. A missing submodule stays a gap until accessed or formally excluded. Archive contents that carry business logic need safe extraction into `docs/project-analysis/evidence/` with traversal/size checks and a separate manifest.

Do not scan outside an authorized root by following symlinks. Do not upload private code to public search tools. Do not include absolute local paths containing usernames in portable reports.

## 2. Discovery Before Documentation

For every repository and applicable domain, obtain an independent candidate list before writing prose. Keep the raw result under `discoveries/` with tool name/version, timestamp, revision, query/command, scope, file count, result count and pagination state. Search output truncation is a blocker. A regex match is a candidate, not proof of semantics.

Use at least two independent discovery surfaces where they exist:

| Domain | Implementation surface | Independent cross-check |
| --- | --- | --- |
| Frontend | Router registry, file routes, menu/actions, forms, stores | Browser navigation, component tests, permissions/feature flags |
| APIs | Route/controller registration, resolver/RPC/service definitions | OpenAPI/GraphQL/proto, clients, contract tests, gateway rules |
| Features | Entry handlers, services, state machines, command implementations | User stories/docs, tests, permissions and business enum definitions |
| Data | Migrations, DDL, ORM models, raw SQL | Schema dumps, authorized catalog metadata, test fixtures, BI/ETL queries |
| Jobs/events | Cron, workers, scheduler/DAG registration, subscriptions | Broker bindings, workflow configuration, producer/consumer tests |
| Configuration | Config loaders, environment lookups, defaults, flags | Deployment manifests, config schema, build/runtime overrides |
| Delivery | CI jobs, Dockerfiles, IaC, package scripts | Runbooks, release artifacts, deployment overlays |
| Dependencies | Manifests, lockfiles, imported packages | SBOM, vendored sources, license files, runtime plugin lists |

Graph-first workflow: check index freshness and supported languages per root; exhaust relevant result pages; capture both call directions and non-call relationships; use source fallback for missing ranges. Unknown coverage means unknown, not clean. Static graphs usually miss reflection, DI, dynamic imports, template resolution, generated code, SQL construction and runtime registration.

## 3. Business Capabilities

Build a hierarchy of bounded contexts, modules, capabilities and atomic actions. Separate create, read, update, delete, approve, reject, export, import, archive, restore, retry and compensation when they actually exist. Include admin-only, internal-only, feature-flagged, disabled and deprecated paths with their status. Do not invent CRUD merely because a table exists.

Each feature needs:

- Actor/role, entry route/command/event, preconditions and permission rule.
- Inputs, field-level validation, business invariants and calculations.
- Main flow and every material condition/switch/handler branch.
- Entity/state changes, transaction boundary and consistency model.
- Responses, files, notifications, external calls and data side effects.
- Failure outcomes, domain error codes, retries, timeouts, cancellation and compensation.
- Pagination, sorting, filtering, batching, concurrency and idempotency semantics.
- Locale, time zone, rounding, money, tenant isolation and data retention where relevant.
- Configuration/flags that alter behavior; active and inactive variants.
- Tests that actually exercise each rule, with untested cases explicitly named.

Do not equate a menu with the complete product. Look for keyboard actions, deep links, API-only workflows, scheduled workflows, background synchronization, CLI tasks, webhooks and stored business logic.

## 4. Frontend/Backend Contract Join

For each request compare protocol, method, base URL/gateway rewrite, path parameters, query/body/header shape, naming/casing, nullability, optional fields, enums, date/time and numeric serialization, content type, auth/CSRF, errors, pagination and versioning.

Document auth acquisition/refresh/expiry, tenant propagation, retries, cancellation, caching and optimistic updates on both sides. Trace WebSocket/SSE subscription establishment, messages and reconnection, not just HTTP setup.

Frontend route -> page/component -> action/store -> client -> gateway -> middleware -> handler -> service -> repository/query -> data object -> event/integration -> response -> state/view update.

For asynchronous chains, identify correlation IDs, producers, topics/queues, consumer groups, schema versions, delivery guarantees, retry policy, DLQ, deduplication, ordering and replay. Do not draw a direct function-call arrow where transport and asynchronous scheduling intervene.

For each relationship attach its own evidence; two evidenced nodes do not prove an edge. Each alternative branch has an explicit chain or documented branch record, including why no persistence/external effect exists when appropriate.

## 5. Data Completeness

Record catalog/database, schema/namespace, object name, physical/logical name, owning service, storage engine and source-of-truth stage. Preserve quoting/case rules and distinguish databases with identical table names.

Inventory these objects individually where present:

- Tables, columns (including generated/computed), types/domains/enums, defaults, nullability and comments.
- Primary/foreign/unique/check constraints, indexes including order, expressions, predicates and included columns.
- Views/materialized views, stored procedures/functions/packages and triggers.
- Sequences/identity, partitions/shards, temporal/history/archive tables, synonyms and extensions.
- Lookup/reference/seed dictionaries, enum values, status mappings, tenant/environment crosswalks.
- Document collections and nested fields, cache key patterns/TTL/invalidation, search indexes/mappings, object buckets/key formats, graph nodes/edges, vector indexes/embedding versions.
- Queue/event payloads, files/CSV/fixed-width layouts, report templates and ETL intermediate datasets.

Every table owns an explicit list of column IDs. Every column points back to its table. Keep separate column records so summary tables cannot hide fields. Link readers/writers, CRUD operations, joins, lineage transformations and feature/API consumers.

Reconcile migrations in execution order, not as a union of all historical CREATE statements. Account for rename/drop/alter, branch-specific migrations and repeatable migrations. ORM-to-physical names, raw SQL tables, triggers and DB-generated effects need separate checks. A historical dropped object remains documented as historical, not current.

If approved, query read-only catalog metadata using engine-native tools and save sanitized results. Capture server version, environment alias, timestamp, row-count method (exact/estimated) and permission-limited visibility. Never infer production contents from repository fixtures. Do not issue full production table counts, EXPLAIN ANALYZE or schema locks casually. No production rows are necessary for a structural data dictionary.

Field-level lineage: source field -> validation/coercion -> transformations/joins -> target field -> downstream consumer. Capture PII classification, encryption/masking, retention, deletion, ownership and audit access. Data sensitivity names are metadata; values remain redacted.

## 6. Build-to-Operate Lifecycle

Record supported toolchain versions, lockfile/package management, code generation, build targets, platform/architecture variants, native dependencies, configuration precedence, secret injection, test layers and CI gates. Inspect scripts before running them; a harmless-sounding test command may invoke migrations or external systems.

Trace source -> build -> artifact/image -> registry -> environment overlay -> migration -> rollout -> health check -> monitoring -> rollback/restore. Document deployment ownership, trust/network boundaries, ports/protocols, replicas/scaling, resource limits, storage and schedules when evidenced. Distinguish intended IaC from observed runtime deployment.

Cover logs, metrics, traces, alert routing, health/readiness, backup/restore, RPO/RTO evidence, incident playbooks, data repair and retirement. Never manufacture SLO or recovery numbers.

Security includes identity, role/attribute authorization, tenant isolation, input/output handling, upload/download boundaries, SSRF/injection risks, secret handling, dependency vulnerabilities with actual tool/version evidence and license obligations. Findings carry severity, exact location, impact, evidence, confidence and a bounded recommendation. A static scan finding is not automatically an exploitable vulnerability.

## 7. Reconciliation and Independent Review

Before delivery, check every root x domain cell: `verified`, `unknown` or evidenced `not-applicable`. Compare discovered identifiers with documented identifiers using set differences, not only totals. Two lists with equal sizes can still disagree.

Required reverse checks:

- Every manifest entry has a recorded review, exclusion or unresolved disposition.
- Every route/action/API/job/event/flag and data object/column candidate has a disposition.
- Every documented implemented entity has source evidence; every substantive claim has evidence at the right granularity.
- Every UI request maps to an API or an explicit absent/external boundary.
- Every API has consumers or an evidenced external/internal-only designation.
- Every data object has readers/writers or an evidenced unused/external/legacy explanation.
- Every chain is contiguous across real directed relations; verify all alternate paths separately.
- Every test/result is clearly observed, skipped, unavailable or proposed.
- Every source mismatch, missing field or unknown branch has a gap with owner/action.

If independent review is permitted, delegate a bounded read-only audit with exact root, revision, inventories, graph coverage, evidence paths, unprocessed scopes and expected return fields. Without delegation, perform a second pass from inventories toward the report, not a reread of the prose alone. Do not claim independence when the same pass only restates its findings.

## 8. Large Projects and Resume

Checkpoint processed file IDs, module scopes, candidate offsets, graph generation, pending gaps and validation result under `docs/project-analysis/checkpoints/`. Resume from these artifacts, verify source freshness and continue. Do not drop detail to fit the context window.

Use stable namespaced entity IDs and merge batches by ID with duplicate/conflict detection. Preserve aliases for renamed symbols. Large reports may split detailed module HTML files under `docs/project-analysis/modules/`, but the main catalog, search, inventories and exports must remain complete. Test first, middle and last records; pagination is not permission to discard data.