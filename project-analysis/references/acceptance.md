# Acceptance and Evidence Checklist

## Purpose

Prove that the declared analysis scope is accounted for and that the delivered HTML works. Keep three different outcomes separate: source-analysis completeness, report-tool correctness and analyzed-product test results.

## Prerequisites

Have the original independent inventories, up-to-date source snapshot, complete discovery results, current `analysis.json`, Python 3.9+ and browser tooling. Upstream diagram/design tools are optional integrations, not baseline requirements.

## Executable Checks

From the target workspace, resolve `SKILL_DIR` and `REPORT_ROOT`, then run:

```sh
python3 -m unittest discover -s "$SKILL_DIR/scripts" -p 'test_*.py' -v
python3 "$SKILL_DIR/scripts/analyze.py" validate --input "$REPORT_ROOT/docs/project-analysis/analysis.json" --inventory "$REPORT_ROOT/docs/project-analysis/inventory-app.json" --output "$REPORT_ROOT/docs/project-analysis/coverage.json"
python3 "$SKILL_DIR/scripts/analyze.py" render --input "$REPORT_ROOT/docs/project-analysis/analysis.json" --inventory "$REPORT_ROOT/docs/project-analysis/inventory-app.json" --output "$REPORT_ROOT/docs/project-analysis.html"
```

Repeat `--inventory` for each root on both commands. A validation failure must remain visible even when rendering succeeds. Do not join these with `&&` if intentionally generating an incomplete report after recording the failed gate; execute the render as a separate explicit step.

## Semantic Acceptance Gates

| Gate | Pass criterion | Evidence |
| --- | --- | --- |
| Scope | All roots/revisions/environment variants listed; no unmentioned exclusions | Root register and manifests |
| Files | Original manifest minus recorded files is empty; no unexplained extras; no unreviewed eligible entries | Set differences and review reasons |
| Discovery | Complete result pages for each root/domain; every candidate has an evidenced disposition | Raw discoveries and candidate IDs |
| Features | All entry/action/rule/permission/flag/branch candidates mapped; decisive implementations investigated | Feature matrix and reverse audit |
| Clarity | Features, APIs, tables and jobs have evidenced Chinese purpose, steps, example, failure, boundaries and terms | Explanation records and explicitly labelled self-review |
| Contracts | All frontend requests and backend entry points accounted for, with missing/external boundaries explicit | Producer-consumer matrix |
| Integration | Shared business concepts, paired boundary contracts, data ownership and failure propagation reconciled; conflicts retained with business consequences | Relation contracts, entity IDs, risk findings and integration self-review |
| Data | Tables, columns and other data objects reconciled across available authoritative sources | DDL/ORM/catalog differences, per-table field sets |
| Chains | Success, failure and async/compensation paths connected using evidence-backed directed edges | Relation IDs and branch chains |
| Lifecycle | Build, delivery, operation, recovery and security domains accounted for | Config/runbook/test artifacts |
| Evidence | All cited files/locators exist at the stated snapshot and support their claims | Source checks and logs |
| Uncertainty | No open applicable unknowns when claiming reconciled scope | Gap register and resolutions |

Set comparison is mandatory, not just matching counts. An excluded or unavailable domain cannot be counted as reviewed. A passing tool receipt cannot override a failed semantic gate.

## Browser Test Matrix

先完成深度、整合、覆盖和通俗表达的验收，再检查展示。使用 Playwright 或现有浏览器工具记录实际结果，桌面以 1440x1000 为主。手机只做一次 390px 宽度的阅读与导航检查，不要求多尺寸截图或视觉打磨；除非用户另有要求，不让手机兼容性延迟分析交付。大字号、键盘操作和桌面数据可读性仍需保留。

1. Open `docs/project-analysis.html` directly using `file:`; no local web server is required for the baseline.
2. Verify no uncaught console errors or failed asset requests. Block network to prove the report remains usable. Lucide icons must render, not empty placeholders.
3. Confirm project title, example/incomplete banners, repository roots, entity counts and coverage denominators match JSON exactly.
4. Open every navigation section. Search an ID, a field only inside nested details, a Unicode string and a no-match value. Clear search and verify all records return.
5. Combine type/repository/status filters and reset them. Exercise first/middle/last pages with more than 80 records. Verify a last-page record is searchable and exportable.
6. Open entity details, table columns, evidence and related nodes. Use Tab/Enter/Escape; confirm dialog focus stays contained and returns to the trigger on close. Reopen long details and scroll.
7. Open chains and inspect ordered node links, error branches and evidence. For upstream/downstream claims, check the actual authored direction. The baseline relationship catalog exposes direct relationships in details, not a transitive graph claim.
8. Export full JSON and filtered CSV; parse downloaded data and compare IDs/counts/content to the source, including records on hidden pages. Check cells beginning `=`, `+`, `-`, `@` are neutralized.
9. Print/PDF all records with active filters and a non-first page. Confirm full inventory, all nested fields, evidence, exclusions and gaps are present. Do not print only the currently visible page.
10. Toggle theme and UI language. Authored business/source content does not magically translate; only viewer labels switch. Check localStorage denial does not crash.
11. 保存有用的桌面截图并检查图示、长字段和证据可读性。手机只核对正文可读、导航可达，宽表/宽图可在自身容器滚动；不为手机截图异常反复换工具或重做样式。
12. Verify `prefers-reduced-motion`, empty/non-applicable domains, very long identifiers and literal markup strings. Ensure an `<img onerror=...>` string appears as text and never executes.

These snippets express useful checks; adapt them to the tool's API and observed page, not an imaginary test environment:

```javascript
await page.setViewportSize({ width: 390, height: 844 });
const fits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
if (!fits) throw new Error('Unexpected horizontal page overflow');
await page.emulateMedia({ reducedMotion: 'reduce' });
await page.getByRole('button', { name: '导航菜单', exact: true }).click();
await page.getByRole('button', { name: /功能与数据目录/ }).click();
await page.getByRole('searchbox').fill('known-entity-id');
await page.screenshot({ path: 'docs/project-analysis/evidence/mobile.png', fullPage: true });
```

## Troubleshooting

- `node` unavailable: use the Python baseline; record archify CLI execution unavailable. Do not claim the Archify integration was run.
- MCP absent/stale/unsupported language: use native parsers/LSP and scoped source review; preserve the gap in graph coverage.
- Cannot access live DB: report repository-defined schema, identify unresolved live drift and list the exact read-only metadata needed.
- Validator rejects a table: enumerate every column as a separate entity and repair both parent and column-ID lists.
- Validator rejects a chain: inspect the real forwarding/transport/handler boundary; add only supported relations, not convenient arrows.
- JSON/schema error: preserve the previous report, repair the failing input and rerun. Do not replace it with an empty passing dataset.
- UI freezes on a very large dataset: measure first, then split complete module detail artifacts or add indexed search/virtualization. Do not delete objects or evidence.
- Browser tools unavailable: retain tool tests and explicitly mark visual, accessibility and download verification unrun.

## Evidence Packaging

Keep inventories, discoveries, analysis JSON, coverage receipt, diagram IR/receipts, sanitized command logs, screenshots and a validation summary under `docs/project-analysis/`. Include tool versions and root revisions. Redact before packaging. Never package secrets, installed runtimes, raw production rows or unrelated workspace files.

## Delivery Summary Template

```text
报告：docs/project-analysis.html
范围：<仓库别名、快照、环境>
覆盖：<审阅文件 / 应审阅文件>；<已映射候选 / 已发现候选>
数据：<表、字段、其他对象数量及结构来源>
链路：<已核实链路及分支数量>
整合：<双向核对的系统边界、未匹配项、证据冲突及业务后果>
校验：<实际执行的工具、浏览器与结果>
集成：taste-skill <级别>；impeccable <级别>；archify <级别>
限制：<排除项、未接入系统、未执行测试、开放缺口>
结论：<范围内已对账 / 覆盖未完成>，不作绝对零遗漏保证。
```