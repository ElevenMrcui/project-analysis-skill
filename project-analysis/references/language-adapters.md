# Language and Framework Adapters

## Adapter Selection

Choose adapters from actual manifests, extensions, build targets, generated-source configuration and runtime wiring. One repository may require several. Do not force frontend concepts onto a library or CLI, or pretend a pure frontend owns remote database tables. Mandatory domains remain present with evidence-backed not-applicable explanations.

For an unfamiliar language, identify compiler/runtime, package/build metadata, entry/export mechanisms, dependency resolution, reflection/metaprogramming, error/concurrency semantics and persistence conventions. Use the native parser/LSP or a supported tree-sitter grammar; record unsupported syntax and fallback source review. Do not assume a regex extractor is complete.

## Adaptation Matrix

| Ecosystem | Discovery anchors | Required language-specific analysis | Emphasized report views |
| --- | --- | --- | --- |
| JS/TS, Node, Deno, Bun | package manifests/lockfiles, tsconfig, route/bootstrap files, workspaces, exports | ESM/CJS, dynamic import, event loop, Promise/cancellation, serialization, runtime validation vs TypeScript-only types, generated clients | Request contracts, module graph, async lifecycle, bundle/runtime boundaries |
| React/Next/Remix | file routes, router config, server/client directives, actions/loaders, middleware | Server components/actions, SSR/SSG/ISR, hydration, streaming, hooks/state/cache, error boundaries, layout inheritance and auth | Route/action/state catalog, render/request/cache flows, accessibility |
| Vue/Nuxt | router/file routes, stores/composables, plugins, server routes | Composition/reactivity, SSR/hydration, auto-imports, directives, guards, Pinia actions and generated routes | User journeys, state transitions, client-server joins |
| Angular/Svelte/Astro | route files, DI/providers, stores, islands, server endpoints | Angular interceptors/guards/resolvers; Svelte load/actions; Astro content collections/islands; build-generated registrations | Page states, dependency injection, hydration boundaries |
| Python | pyproject/requirements/lockfiles, entry_points, app factories, decorators, imports | Selected interpreter/version, dynamic imports, decorators, metaclasses, sync/async boundary, context managers, generator lifetime, Pydantic validation, Celery/Airflow jobs | API/DAG/data lineage, model mapping, validation and scheduling |
| Java/Kotlin/Scala | Maven/Gradle modules, application entry, annotations, config profiles | Spring DI/AOP/proxy, transaction self-invocation, JPA/MyBatis mapping, coroutines/reactive pipelines, sealed types, reflection, serialization | Bean/module ownership, transactional paths, RPC and persistence |
| C#/F#/VB/.NET | solutions/projects, Program/Startup, DI registrations, appsettings, endpoints | Middleware ordering, scoped lifetimes, async/await/cancellation, LINQ translation, EF model/migrations, hosted services, attributes/source generators | Endpoint catalog, DI/lifetime, transaction and background service flows |
| Go | go.mod/go.work, cmd packages, init functions, router registrations | Implicit interfaces, goroutines/channels, context cancellation, defer/cleanup, error wrapping, build tags, generated code, race risks | Package/entry map, concurrency lifecycle, API/store contracts |
| Rust | Cargo workspaces/features, bin/lib targets, build.rs, macro invocations | Ownership/lifetimes, trait impls, async runtimes, Result/panic, unsafe/FFI, procedural macros, feature-gated variants | Crate/public API catalog, ownership/resource lifecycle, concurrency |
| C/C++ | CMake/Make/Bazel, compile_commands, main/export headers | Preprocessor/platform variants, templates/macros, memory ownership, ABI, RAII, threads/locks, callbacks, native libraries | Exported symbols, call/resource graphs, build/platform matrix |
| PHP | Composer/autoload, framework routes, service container, migrations | Laravel/Symfony providers, middleware/policies, ORM scopes, queues, magic methods, serialization | Routes/policies, transactions and scheduled/queued work |
| Ruby | Gemfile/lock, Rails routes, engines, models, migrations, jobs | Metaprogramming, concerns/callbacks, implicit ORM behavior, scopes, authorization, ActiveJob and convention routing | Convention-to-runtime map, callback/data effects, jobs |
| Swift/Objective-C | Package.swift, Xcode targets, app delegates/scenes, entitlements | ARC/retain cycles, actor isolation, task cancellation, Combine, selectors, delegate callbacks, Core Data/SwiftData migrations | Screen/navigation/state, permissions, resource and background lifecycles |
| Kotlin Android | Gradle modules, AndroidManifest, Activity/Service/Receiver, navigation | Lifecycle, coroutines/Flow, ViewModel, Room, WorkManager, IPC/intents, permissions, offline sync | Mobile journeys, lifecycle, local/remote data consistency |
| Dart/Flutter | pubspec, routes, widgets/state, platform channels | Widget lifecycle, isolates, streams, futures, state management, native plugins, local DB and sync | Navigation/state, platform boundaries, offline workflows |
| SQL/PLSQL/TSQL | Ordered migrations, DDL, views/procedures, triggers, grants | Dialect semantics, implicit casts, null/three-valued logic, transaction isolation, dynamic SQL, execution context, cursors, dependencies | Complete data dictionary, ER, object dependency and field lineage |
| R/Julia/notebooks | project/lock files, notebook cells, data/model scripts | Execution order, random seeds, environments, numerical precision, vectorization, input provenance and side effects | Reproducibility, analytical pipelines, dataset/model lineage |
| Elixir/Erlang | mix/rebar, applications, supervisors, routers, schemas | OTP supervision, mailbox/process ownership, failure/restart, distributed state and message contracts | Supervision/process topology, event and failure lifecycles |
| Haskell/Clojure/Lua | build manifests, main/ns/module exports, handlers | Effects/laziness, macros, protocol dispatch, embedded host callbacks and state boundaries | Public API, transformation pipelines, host integration |
| Shell/PowerShell | scripts, scheduled tasks, CI jobs, service units | Quoting, exit codes, pipelines, traps, env expansion, privilege and destructive commands | Operational workflow, side effects, rollback and portability |
| Terraform/Kubernetes/Helm | modules, resources, values, overlays, policies | Plan vs applied state, interpolation, secret refs, network/RBAC, volumes, probes, rollout and environment differences | Deployment ownership, trust boundaries, recovery lifecycle |
| Protobuf/GraphQL/OpenAPI | schemas, generated clients/servers, resolvers | Compatibility, optional/null semantics, field numbering, operation binding, subscriptions, validation and version drift | Producer/consumer contracts and compatibility matrix |

## Project-Type Adaptation

| Project type | Primary entities and chains | Do not fabricate |
| --- | --- | --- |
| Frontend-only | Screens/actions, state, permissions, network contracts, assets/localization | Backend implementation or physical tables absent from scope |
| Backend-only | Endpoints, handlers, domain rules, data objects, integrations, jobs | UI pages or user interactions without a known client |
| Library/SDK | Public API, overloads/types, extension points, errors, lifecycle, compatibility | HTTP routes merely because networking is a dependency |
| CLI/daemon | Commands/options/config precedence, I/O, exit codes, signals and state | Web pages and dashboards |
| ETL/data platform | DAGs, transforms, datasets, field lineage, schedules, retries, checkpoints | Live data quantities without a measured catalog/run |
| Mobile/desktop | Screens, menus/shortcuts, lifecycle, OS permissions, packaging, IPC, local storage | A web frontend layer where none exists |
| Embedded/firmware | Interrupts, state machines, memory maps, buses, timing, watchdogs, updates | Timing guarantees without target measurements |
| ML/AI | Data preprocessing, training/evaluation, model/version, prompts, retrieval, tools, safety, cost/latency evidence | Model quality, token costs or benchmark outcomes without measurements |
| Plugin/extension | Contribution points, activation, commands, permissions, host API and IPC | Standalone process or service boundaries not supported by evidence |

## Evidence Discipline

For Python, prefer Pylance/LSP facts and the actual selected interpreter when available; terminal PATH does not prove editor configuration. For compiler-driven ecosystems, use the real build configuration and target. Do not combine mutually exclusive build profiles into one imaginary runtime.

Do not install or execute each ecosystem's tooling merely because it is named here. Prefer available tools, read-only metadata and existing test results, then ask before expensive builds or commands with external effects. Record the actual tool, command, environment and outcome in the report.