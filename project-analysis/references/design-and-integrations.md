# Design, Diagrams and External Skill Integration

## Verified Reference Projects

These upstream READMEs were consulted on 2026-09-06. Upstream versions change; recheck installed skill instructions and schemas before executing tools. This package contains original workflow/report code inspired by their documented principles, not a bundled or renamed copy of those three projects.

| Reference | Verified project | Contribution to this workflow |
| --- | --- | --- |
| taste-skill | https://github.com/Leonxlnx/taste-skill | Deliberate visual direction, typography, spacing; adjustable design variance, motion intensity and visual density; avoid generic repetitive layouts |
| impeccable | https://github.com/pbakaus/impeccable | Separate product context from surface styling; critique, technical audit, responsive adaptation, hardening, optimization and final polish |
| archify | https://github.com/tt-a1i/archify | Typed diagram source, validated architecture/workflow/sequence/dataflow/lifecycle diagrams, authored relationships, finite motion, portable HTML and validation receipts |

Archify is the architecture diagram Skill by `tt-a1i`, not similarly named database, binary optimization or browser extension projects. Do not replace it with an unrelated project.

The bundled offline viewer uses Lucide 0.468.0 icons. The minified distribution and its upstream license are in `assets/`. Keep the license when redistributing the package. No runtime CDN, remote fonts, telemetry or installation hook is required by the baseline viewer.

## Integration Levels

Always record one of these levels per external project in the delivery notes:

1. **Principles applied**: this package's documented design/verification methods were used; no upstream executable ran.
2. **Installed Skill consulted**: read the installed skill and followed its applicable workflow, with a recorded version/path.
3. **Tool executed**: retain command, version, output and validation receipt. A README read is not a tool execution.

If a named Skill is available, load it and use the relevant capability. If absent, the baseline remains usable; record the unavailable integration and follow this guide. Installation of third-party skills, hook manifests or executable downloads requires user approval. Never claim “passed impeccable audit” or “archify validated” without the corresponding tool evidence.

## Visual Direction: Technical Editorial Workspace

The implemented palette and current high-star Skill research are recorded in [UI research](./ui-research.md). For this template revision, charcoal navigation, neutral light content, vermilion interaction cues and teal data accents supersede the original green-first palette suggestion below. Preserve Chinese business explanations and complete data before visual polish.

The artifact is an engineering analysis tool, not a marketing page. Start on the actual project overview with its scope, completion state and the first real chain. Prioritize scanning, inspection and comparison.

- White/mineral light surfaces, dark green ink, restrained emerald interactions, cobalt relationship accents and coral risk accents. Provide an equally legible dark theme, not a mandatory dark theme.
- Compact sidebar, clear workspace identity, strong but not oversized headings, narrow line lengths and consistent spacing. Avoid a wall of floating cards or cards inside cards.
- Use a purposeful text family such as Avenir Next with CJK fallbacks and monospace identifiers. Offline availability is more important than an unverified remote font promise. If branding requires a bundled font, retain its license.
- Suggested design dials: variance 4/10, motion 2/10, density 7/10. These are this report's chosen settings, not an upstream requirement or measured quality score.
- Group dense inventories in sortable/filterable tables or progressive detail views. Never drop fields for visual symmetry. A small number of summary indicators is useful; hundreds of decorative metric cards are not.
- Icons represent actual commands; native selects represent option sets; labels remain explicit. Tooltips/accessibility names identify icons. No decorative badges masquerading as controls.
- Motion communicates a state change or a finite trace. Honor reduced motion. No autoplay endless diagrams, glow orbs or decorative 3D.
- Use actual project diagrams, ER/data lineage and authorized screenshots as visual assets. Do not use unrelated stock photos as evidence. Empty diagram data must show an honest empty state, not invented topology.

## Archify Workflow

Use Archify for complex topology or diagram exports when installed. The bundled chain view is a lightweight ordered-path viewer, not an implementation of the full Archify renderer.

1. Choose diagram type from the question: architecture for ownership/boundaries; workflow for stages/branches; sequence for ordered request/response; dataflow for field movement/sensitivity; lifecycle for state/retry/cancel/terminal behavior.
2. Read the installed type schema and examples. Build its typed JSON IR from already evidenced report entities/relations. Do not invent schema keys or assume this package's `analysis.json` is valid Archify IR.
3. Preserve mapping between report IDs and diagram IDs. Record layout annotations separately from factual relationships. Each edge retains direction, protocol/event or transformation semantics and evidence confidence.
4. Organize an overview plus drill-down views. An overview may show only major components, but the complete inventory and detailed diagrams must remain reachable. Do not use Archify's compact overview recommendation as a reason to omit project features.
5. Run the installed validator and delivery command as documented by that version. The consulted README documents this shape, with the executable rooted at the actual installation:

```sh
node "$ARCHIFY_DIR/bin/archify.mjs" validate architecture "$REPORT_ROOT/docs/project-analysis/diagrams/system.json" --quality showcase --json
node "$ARCHIFY_DIR/bin/archify.mjs" deliver architecture "$REPORT_ROOT/docs/project-analysis/diagrams/system.json" "$REPORT_ROOT/docs/project-analysis/diagrams/system.html" --quality showcase --json
```

6. Save the actual receipts under the same output tree. Follow rule-specific repair instructions, rerun validation and preserve the last passing artifact on failure. Disable update checks with `ARCHIFY_UPDATE_CHECK_DISABLED=1` when an offline run is required and the installed version supports it.
7. Verify source pinning, long labels, label-to-edge clearance, node bounds, no orphan references, theme consistency, reduced-motion behavior and complete exports in a browser. Passing layout validation does not prove the model matches source.
8. Attach the diagram HTML path to a report section via `reportPath`; retain JSON and receipts. Embed only when offline isolation, payload size and script safety have been checked. Linked self-contained diagrams below `docs` are acceptable supporting artifacts.

Focus/reach/route interactions describe authored relationships. They are not measured runtime traffic or proof of change impact. Do not use animation speed to imply real latency.

## Impeccable-Inspired Review Loop

**Critique**: can a maintainer locate one feature, its API, physical fields, failure path and evidence without reading the entire report? Are scope and incomplete state unmistakable?

**Audit**: inspect real rendered contrast, landmarks/headings, accessible names, keyboard operation, focus visibility, table semantics, reduced motion, overflow and performance. Automated lint alone is insufficient.

**Harden**: exercise long paths, Unicode identifiers, missing evidence, empty lists, unresolved references, dozens of columns, large inventories, disabled localStorage, offline mode and adversarial text such as `</script>`.

**Adapt**: test narrow mobile, tablet, desktop, 200% zoom and both themes. Large tables can scroll within a labelled container; the entire page must not overflow horizontally. Navigation and dialogs must remain operable.

**Polish/optimize**: align spacing and typography; keep control dimensions stable; defer expensive detail DOM until needed; paginate without data loss; preserve full print/export records. Fix functional defects before visual refinements.

If the actual impeccable CLI is installed, consult its help/version before invoking detection against generated HTML. Save the real findings and state any waivers. Avoid invoking its project-init commands against the analyzed repository if they would write outside the permitted `docs` output tree.

## Offline and Security Contract

Escape embedded JSON `<`, `>`, `&` and script-closing sequences. Render source strings using text nodes, never `innerHTML`, executable Markdown, `eval` or dynamic script URLs. Source URLs must be verified, credential-free and use safe schemes. Reject traversal and protocol-relative URLs for local diagram links.

CSV exports must neutralize formula-leading text. Exports include all filtered rows, not just the current page; full JSON and full print include the complete dataset. Any externally linked source may require network/authentication; baseline navigation/search/data does not.

Do not publish internal reports without checking source paths, metadata, screenshots, URL queries and samples for secrets/PII. This viewer is not a secret scanner.