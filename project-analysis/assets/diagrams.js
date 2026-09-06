Object.assign(words["zh-CN"], {
 diagrams: "架构与流程图",
 database: "数据字典与表关系",
 architecture: "项目架构图",
 "function-flow": "功能流程图",
 "detail-flow": "细节功能流程图",
 sequence: "时序图",
 dataflow: "数据流向图",
 er: "数据表关系图",
 lifecycle: "状态与生命周期图",
 actors: "参与角色",
 rules: "业务规则",
 inputs: "输入",
 outputs: "输出",
 errors: "异常与错误",
 permissions: "权限",
 sideEffects: "副作用",
 tests: "测试",
 route: "路由",
 actions: "操作",
 states: "界面状态",
 protocol: "协议",
 operation: "操作",
 request: "请求",
 response: "响应",
 authorization: "授权要求",
 consumers: "消费者",
 producers: "生产者",
 qualifiedName: "完整表名",
 columns: "字段",
 keys: "主键与唯一键",
 indexes: "索引",
 readers: "读取方",
 writers: "写入方",
 parent: "所属数据表",
 dataType: "数据类型",
 nullable: "允许为空",
 default: "默认值",
 constraints: "约束",
 sensitivity: "敏感级别",
 lineage: "字段血缘",
 retry: "重试",
 idempotency: "幂等",
 failure: "失败处理",
 channel: "通道",
 schema: "数据结构",
 delivery: "投递与发布",
 signature: "函数签名",
 transaction: "事务",
 concurrency: "并发控制",
 returns: "返回值",
 stateTransitions: "状态变化",
 accessibility: "无障碍",
 schemaSource: "结构来源",
 execution: "执行情况",
 cases: "用例",
 affects: "影响对象",
 secret: "是否敏感",
 stages: "阶段",
 rollback: "回滚",
 runtimeObserved: "是否有运行证据",
 severity: "严重程度",
 confidence: "证据可信度",
 action: "处理建议",
 comment: "字段说明",
 key: "键类型",
 length: "长度",
 precision: "精度",
 scale: "小数位数",
 references: "关联引用",
 relationship: "关系类型",
 sourceColumns: "起点字段",
 targetColumns: "终点字段",
 sourceCardinality: "起点基数",
 targetCardinality: "终点基数",
 evidence: "证据索引",
 source: "来源",
 target: "去向",
 method: "核验方法",
 snapshot: "证据快照",
 note: "备注",
 result: "结果",
 resolution: "处理结果",
 nextAction: "下一步",
 entities: "功能与数据目录",
 features: "功能",
 nodes: "图节点",
 edges: "图关系",
 label: "名称",
 from: "起点",
 to: "终点",
 direction: "布局方向",
 entity: "对应对象",
 shape: "节点类型",
 reason: "说明",
 disposition: "处置结论",
 manifestEntries: "原始清单条目",
 reportedEntries: "报告清单条目",
 eligibleFiles: "应审阅文件",
 reviewedFiles: "已审阅文件",
 fileReviewPercent: "文件审阅率",
 excludedEntries: "已排除条目",
 discoveryCandidates: "发现候选数",
 mappedCandidates: "已映射候选数",
 generatedAt: "生成时间",
 locale: "报告语言",
 example: "示例数据，非真实项目分析。业务内容、证据和统计仅用于演示。",
 description: "说明",
 title: "标题",
 revision: "版本快照",
 dirty: "工作区未提交更改",
 language: "开发语言",
 module: "所属模块",
 path: "文件路径",
 file: "文件记录",
 artifact: "证据产物",
 locator: "证据定位",
 startLine: "起始行",
 endLine: "结束行",
 "foreign-key": "数据库外键",
 logical: "代码逻辑关联",
 inferred: "待核实推断",
 one: "一",
 many: "零到多",
 "zero-or-one": "零或一",
 "one-or-many": "一到多",
});
Object.assign(words.en, {
 diagrams: "Architecture & Flows",
 database: "Data Dictionary",
 architecture: "Architecture",
 "function-flow": "Feature Flow",
 "detail-flow": "Detailed Flow",
 sequence: "Sequence",
 dataflow: "Data Flow",
 er: "Entity Relationships",
 lifecycle: "State Lifecycle",
});
Object.assign(words["zh-CN"], {
 explanation: "通俗讲解",
 purpose: "它解决什么问题",
 howItWorks: "它如何运作",
 illustration: "说明性示例",
 failure: "失败时会怎样",
 boundaries: "适用范围与限制",
 terms: "术语解释",
 term: "术语",
 meaning: "通俗含义",
});
function explain(record) {
 const section = element("section", "plain-explanation");
 section.append(element("h3", "", "业务解读"));
 section.append(structured(record.explanation));
 return section;
}
report.diagrams = report.diagrams || [];
navigation.splice(1, 0, ["diagrams", "workflow"], ["database", "database"]);
const diagramCache = new Map();
let diagramSerial = 0;
const diagramText = (value) =>
 String(value ?? "").replace(
  /[&"<>;:|\r\n]/g,
  (character) =>
   ({
    "&": "#38;",
    '"': "#34;",
    "<": "#60;",
    ">": "#62;",
    ";": "#59;",
    ":": "#58;",
    "|": "#124;",
    "\r": " ",
    "\n": " ",
   })[character],
 );
const mermaidLabel = (value) => '"' + diagramText(value) + '"';
function tableKeys(table) {
 const keys = table?.details?.keys || {};
 const pk = new Set(keys.primaryKey || []);
 const fk = new Map();
 for (const constraint of keys.foreignKeys || [])
  for (const column of constraint.columns || [])
   fk.set(column, constraint.refTable);
 return { pk, fk };
}
function diagramSource(record) {
 const aliases = new Map(
  record.nodes.map((node, index) => [node.id, "node_" + index]),
 );
 const alias = (identifier) => {
  if (!aliases.has(identifier))
   throw new Error("图关系引用了不存在的节点：" + identifier);
  return aliases.get(identifier);
 };
 if (record.type === "sequence") {
  const lines = ["sequenceDiagram", "autonumber"];
  for (const node of record.nodes)
   lines.push(
    "participant " + alias(node.id) + " as " + diagramText(node.label),
   );
  for (const edge of record.edges)
   lines.push(
    alias(edge.from) +
     (edge.dashed ? "-->>" : "->>") +
     alias(edge.to) +
     ": " +
     diagramText(edge.label),
   );
  return lines.join("\n");
 }
 if (record.type === "er") {
  const names = new Map(
   record.nodes.map((node, index) => [
    node.id,
    "T" +
     index +
     "_" +
     String(entityById.get(node.entity)?.name || node.label).replace(
      /[^\p{L}\p{N}_]/gu,
      "_",
     ),
   ]),
  );
  const lines = ["erDiagram"];
  for (const node of record.nodes) {
   const table = entityById.get(node.entity);
   const keyInfo = tableKeys(table);
   lines.push(names.get(node.id) + " {");
   for (const identifier of table?.details?.columns || []) {
    const field = entityById.get(identifier);
    if (!field) continue;
    const details = field.details;
    const dataType = String(details.dataType || "unknown").replace(
     /[^\w]/g,
     "_",
    );
    const columnName = String(field.name).split(".").pop();
    const name = columnName.replace(/[^\p{L}\p{N}_]/gu, "_");
    const marks = [
     keyInfo.pk.has(columnName) ? "PK" : null,
     keyInfo.fk.has(columnName) ? "FK" : null,
    ]
     .filter(Boolean)
     .join(",");
    lines.push(
     dataType +
      " " +
      name +
      (marks ? " " + marks : "") +
      " " +
      mermaidLabel(details.comment || field.summary),
    );
   }
   lines.push("}");
  }
  const left = {
   one: "||",
   "zero-or-one": "|o",
   many: "}o",
   "one-or-many": "}|",
  };
  const right = {
   one: "||",
   "zero-or-one": "o|",
   many: "o{",
   "one-or-many": "|{",
  };
  for (const edge of record.edges) {
   alias(edge.from);
   alias(edge.to);
   const connector = edge.relationship === "foreign-key" ? "--" : "..";
   lines.push(
    names.get(edge.from) +
     " " +
     (left[edge.sourceCardinality] || "}o") +
     connector +
     (right[edge.targetCardinality] || "o{") +
     " " +
     names.get(edge.to) +
     " : " +
     mermaidLabel(labels(edge.relationship) + " / " + edge.label),
   );
  }
  return lines.join("\n");
 }
 const lines = ["flowchart " + (record.direction === "LR" ? "LR" : "TB")];
 for (const node of record.nodes) {
  const text = mermaidLabel(node.label);
  const shape =
   node.shape === "decision"
    ? "{" + text + "}"
    : node.shape === "data"
      ? "[(" + text + ")]"
      : ["start", "end"].includes(node.shape)
        ? "([" + text + "])"
        : "[" + text + "]";
  lines.push(alias(node.id) + shape);
 }
 for (const edge of record.edges)
  lines.push(
   alias(edge.from) +
    (edge.dashed ? " -.-> " : " --> ") +
    "|" +
    mermaidLabel(edge.label) +
    "| " +
    alias(edge.to),
  );
 lines.push(
  "classDef decision fill:#f9ece7,stroke:#b23c28,color:#672d20",
  "classDef storage fill:#e6f0ec,stroke:#397462,color:#234c3e",
 );
 for (const node of record.nodes) {
  if (node.shape === "decision")
   lines.push("class " + alias(node.id) + " decision");
  if (node.shape === "data") lines.push("class " + alias(node.id) + " storage");
 }
 return lines.join("\n");
}
let renderQueue = Promise.resolve();
async function diagramSVG(record) {
 const theme =
  document.documentElement.dataset.theme === "dark" ? "dark" : "default";
 const key = record.id + ":" + theme;
 if (diagramCache.has(key)) return diagramCache.get(key);
 const dark = theme === "dark";
 const themeVariables = {
  darkMode: dark,
  fontSize: "15px",
  primaryColor: dark ? "#35412f" : "#f5f7f2",
  primaryTextColor: dark ? "#f0f3e9" : "#252823",
  primaryBorderColor: dark ? "#a9bc97" : "#899a7a",
  lineColor: dark ? "#bfceb1" : "#667857",
  secondaryColor: dark ? "#49352d" : "#f9ece7",
  tertiaryColor: dark ? "#273e35" : "#e6f0ec",
  edgeLabelBackground: dark ? "#2a2e26" : "#ffffff",
  actorBkg: dark ? "#35412f" : "#f5f7f2",
  actorTextColor: dark ? "#f0f3e9" : "#252823",
  actorBorder: dark ? "#a9bc97" : "#899a7a",
  signalColor: dark ? "#bfceb1" : "#667857",
 };
 const task = async () => {
  mermaid.initialize({
   startOnLoad: false,
   securityLevel: "strict",
   theme: "base",
   themeVariables,
   fontFamily: "Avenir Next, PingFang SC, sans-serif",
   flowchart: {
    htmlLabels: false,
    useMaxWidth: false,
    curve: "basis",
    nodeSpacing: 38,
    rankSpacing: 52,
    padding: 18,
   },
   sequence: { useMaxWidth: false },
   er: { useMaxWidth: false },
   maxTextSize: 200000,
  });
  const result = await mermaid.render(
   "diagram_" + ++diagramSerial,
   diagramSource(record),
  );
  diagramCache.set(key, result.svg);
  return result.svg;
 };
 const result = renderQueue.then(task, task);
 renderQueue = result.then(
  () => {},
  () => {},
 );
 return result;
}
function attachSVG(container, source) {
 const parsed = new DOMParser().parseFromString(source, "image/svg+xml");
 const root = parsed.documentElement;
 if (
  root.tagName.toLowerCase() !== "svg" ||
  parsed.querySelector("parsererror")
 )
  throw new Error("图形引擎未返回有效 SVG");
 for (const unsafe of root.querySelectorAll("script,foreignObject,image,a"))
  unsafe.remove();
 for (const node of [root, ...root.querySelectorAll("*")])
  for (const attribute of [...node.attributes])
   if (
    /^on/i.test(attribute.name) ||
    ["href", "xlink:href"].includes(attribute.name)
   )
    node.removeAttribute(attribute.name);
 const svg = document.importNode(root, true);
 container.replaceChildren(svg);
 return svg;
}
function diagramPanel(record, compact = false) {
 const section = element("section", "diagram-panel");
 const toolbar = element("div", "diagram-toolbar");
 const title = element("div");
 title.append(
  element("h3", "", record.name),
  element("p", "small muted", record.summary),
 );
 const actions = element("div", "diagram-actions");
 const stage = element("div", "diagram-scroll");
 stage.tabIndex = 0;
 stage.setAttribute("role", "region");
 stage.setAttribute("aria-label", record.name);
 if (compact) stage.classList.add("compact");
 stage.append(element("p", "muted", "正在绘制图示…"));
 let scale = 1,
  baseWidth = 0,
  naturalWidth = 0,
  svg = null,
  source = "";
 const resize = () => {
  if (svg) {
   svg.style.width = baseWidth * scale + "px";
   svg.style.height = "auto";
  }
 };
 actions.append(
  iconCommand("zoom-out", "缩小", () => {
   scale = Math.max(0.25, scale - 0.25);
   resize();
  }),
  iconCommand("zoom-in", "放大", () => {
   scale = Math.min(4, scale + 0.25);
   resize();
  }),
  iconCommand("scan", "适应宽度", () => {
   scale =
    Math.min(naturalWidth, Math.max(240, stage.clientWidth - 48)) / baseWidth;
   resize();
  }),
  iconCommand("download", "导出 SVG", () => {
   if (source) download(record.id + ".svg", source, "image/svg+xml");
  }),
  iconCommand("file-search", "图示证据与明细", () => openRecord(record)),
 );
 toolbar.append(title, actions);
 section.append(toolbar, stage);
 diagramSVG(record)
  .then((result) => {
   if (!stage.isConnected) return;
   source = result;
   svg = attachSVG(stage, result);
   svg.setAttribute("role", "img");
   svg.setAttribute("aria-label", record.name);
   const bounds = svg.viewBox.baseVal;
   const available = Math.max(240, stage.clientWidth - 48);
   naturalWidth = bounds.width || available;
   baseWidth = Math.min(naturalWidth, available);
   resize();
   record.nodes.forEach((node, index) => {
    if (!node.entity) return;
    const group = svg.querySelector('[id^="flowchart-node_' + index + '-"]');
    if (group) {
     group.style.cursor = "pointer";
     group.setAttribute("role", "button");
     group.setAttribute("tabindex", "0");
     group.setAttribute("aria-label", node.label);
     const open = () => openRecord(entityById.get(node.entity) || node);
     group.addEventListener("click", open);
     group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
       event.preventDefault();
       open();
      }
     });
    }
   });
  })
  .catch((error) => {
   stage.replaceChildren(
    element("p", "notice", "图示渲染失败：" + error.message),
   );
   stage.dataset.error = "true";
  });
 if (!compact) {
  const links = element("div", "diagram-references");
  const identifiers = [
   ...new Set(record.nodes.map((node) => node.entity).filter(Boolean)),
  ];
  for (const identifier of identifiers) links.append(entityLink(identifier));
  section.append(links);
 }
 icons();
 return section;
}
function renderDiagrams(container) {
 container.append(heading(labels("diagrams"), report.project.title));
 if (!report.diagrams.length) {
  container.append(element("div", "notice", "尚未提供图示，图示覆盖未完成。"));
  return;
 }
 const bar = element("div", "filterbar");
 const typeLabel = element("label", "field", "图示类型");
 const type = element("select");
 type.setAttribute("aria-label", "图示类型");
 type.append(new Option("全部类型", ""));
 for (const value of [...new Set(report.diagrams.map((record) => record.type))])
  type.append(new Option(labels(value), value));
 typeLabel.append(type);
 const diagramLabel = element("label", "field search", "选择图示");
 const select = element("select");
 select.setAttribute("aria-label", "选择图示");
 diagramLabel.append(select);
 bar.append(typeLabel, diagramLabel);
 container.append(bar);
 const target = element("div");
 container.append(target);
 const show = () => {
  const record = report.diagrams.find((item) => item.id === select.value);
  target.replaceChildren();
  if (record) {
   target.append(diagramPanel(record));
   const details = element("details", "detail-group");
   details.append(element("summary", "", "图示模型与证据"));
   details.addEventListener("toggle", () => {
    if (details.open && !details.dataset.loaded) {
     details.dataset.loaded = "true";
     details.append(structured(record));
    }
   });
   target.append(details);
  }
  icons();
 };
 const options = () => {
  select.replaceChildren();
  for (const record of report.diagrams.filter(
   (item) => !type.value || item.type === type.value,
  ))
   select.append(
    new Option(labels(record.type) + " / " + record.name, record.id),
   );
  show();
 };
 type.addEventListener("change", options);
 select.addEventListener("change", show);
 options();
}
function columnDictionary(table) {
 const region = element("div", "table-scroll");
 region.tabIndex = 0;
 region.setAttribute("role", "region");
 region.setAttribute("aria-label", table.name + " 字段字典");
 const grid = element("table", "catalog field-catalog");
 grid.append(element("caption", "", table.name + " / 全部字段"));
 const header = element("tr");
 for (const title of [
  "字段 / 说明",
  "数据类型",
  "键",
  "可空",
  "默认值",
  "约束 / 引用",
  "敏感级别",
 ]) {
  const cell = element("th", "", title);
  cell.scope = "col";
  header.append(cell);
 }
 const head = element("thead");
 head.append(header);
 grid.append(head);
 const body = element("tbody");
 const keyInfo = tableKeys(table);
 const dash = (value) =>
  value === undefined || value === null || value === "" || value === "none"
   ? "—"
   : value;
 for (const identifier of table.details.columns || []) {
  const field = entityById.get(identifier);
  if (!field) {
   const row = element("tr");
   const cell = element("td", "", "缺少字段记录：" + identifier);
   cell.colSpan = 7;
   row.append(cell);
   body.append(row);
   continue;
  }
  const details = field.details;
  const row = element("tr");
  const name = element("td");
  name.append(
   entityLink(identifier),
   element("p", "small muted", details.comment || field.summary),
  );
  row.append(name);
  const columnName = String(field.name).split(".").pop();
  const marks =
   [
    keyInfo.pk.has(columnName) ? "PK" : null,
    keyInfo.fk.has(columnName) ? "FK→" + keyInfo.fk.get(columnName) : null,
   ]
    .filter(Boolean)
    .join(" ") || "无";
  for (const value of [
   details.dataType,
   marks,
   details.nullable === true
    ? "是"
    : details.nullable === false
      ? "否"
      : "待核实",
   dash(details.default),
   {
    constraints: dash(details.constraints),
    references: details.references?.length ? details.references : "—",
   },
   details.sensitivity,
  ]) {
   const cell = element("td", "small");
   cell.append(structured(value));
   row.append(cell);
  }
  body.append(row);
 }
 grid.append(body);
 region.append(grid);
 return region;
}
function tableMetadata(table) {
 const details = table.details || {};
 const columnChip = (name) => {
  const chip = element("span", "chip");
  chip.append(entityLink("db:c:" + table.name + ":" + name));
  return chip;
 };
 const section = (title) => {
  const node = element("section", "meta-section");
  node.append(element("h3", "", title));
  return node;
 };
 const wrap = element("div", "meta-grid");
 const identity = section("表标识与主键");
 const qualifiedLine = element("p", "pk-line");
 qualifiedLine.append(
  element("span", "chip", details.qualifiedName || table.name),
 );
 identity.append(qualifiedLine);
 const pkLine = element("p", "pk-line");
 pkLine.append(element("span", "small muted", "主键 "));
 const pk = details.keys?.primaryKey || [];
 if (pk.length) for (const column of pk) pkLine.append(columnChip(column));
 else pkLine.append(element("span", "small muted", "未声明主键"));
 identity.append(pkLine);
 wrap.append(identity);
 const fks = details.keys?.foreignKeys || [];
 const fkSection = section("数据库外键（" + fks.length + "）");
 if (fks.length) {
  for (const fk of fks) {
   const line = element("div", "fk-line");
   (fk.columns || []).forEach((column, i) => {
    if (i) line.append(element("span", "small muted", ","));
    line.append(columnChip(column));
   });
   line.append(element("span", "small muted", "→"));
   line.append(entityLink("db:t:" + fk.refTable));
   line.append(
    element(
     "span",
     "small muted",
     "(" +
      (fk.refColumns || []).join(", ") +
      ")" +
      (fk.onDelete ? " ON DELETE " + fk.onDelete : "") +
      (fk.onUpdate ? " ON UPDATE " + fk.onUpdate : ""),
    ),
   );
   fkSection.append(line);
  }
 } else {
  fkSection.append(
   element(
    "p",
    "small muted",
    "无数据库外键约束；表间关联由应用层维护（见数据生命周期）。",
   ),
  );
 }
 if (details.keys?.checkConstraints && details.keys.checkConstraints !== "none")
  fkSection.append(
   element("p", "small", "CHECK：" + details.keys.checkConstraints),
  );
 wrap.append(fkSection);
 const indexes = details.indexes || [];
 if (indexes.length) {
  const indexSection = section("索引（" + indexes.length + "）");
  const grid = element("table", "index-table");
  const head = element("thead");
  const headerRow = element("tr");
  for (const title of ["索引名", "类型", "字段"]) {
   const cell = element("th", "", title);
   cell.scope = "col";
   headerRow.append(cell);
  }
  head.append(headerRow);
  grid.append(head);
  const body = element("tbody");
  for (const idx of indexes) {
   const row = element("tr");
   const name = element("td");
   name.append(element("code", "", idx.name));
   row.append(name);
   row.append(element("td", "small", idx.unique ? "唯一" : "普通"));
   const cols = element("td");
   (idx.columns || []).forEach((column, i) => {
    if (i) cols.append(document.createTextNode(", "));
    cols.append(columnChip(column));
   });
   row.append(cols);
   body.append(row);
  }
  grid.append(body);
  indexSection.append(grid);
  wrap.append(indexSection);
 }
 const lifecycle = section("数据生命周期与读写");
 if (details.lifecycle)
  lifecycle.append(element("p", "small", details.lifecycle));
 for (const [key, title] of [
  ["readers", "读取方"],
  ["writers", "写入方"],
 ]) {
  if (details[key]) {
   const line = element("p", "small muted");
   line.append(
    element("strong", "", title + "："),
    document.createTextNode(details[key]),
   );
   lifecycle.append(line);
  }
 }
 wrap.append(lifecycle);
 return wrap;
}
function renderDatabase(container) {
 const tables = report.entities.filter((record) => record.kind === "table");
 container.append(
  heading(
   labels("database"),
   `${tables.length} 张表 / ${report.entities.filter((record) => record.kind === "column").length} 个字段`,
  ),
 );
 if (!tables.length) {
  container.append(
   element(
    "p",
    "notice",
    "当前台账没有数据库表。适用性与未接入数据库须在覆盖章节中说明。",
   ),
  );
  return;
 }
 const controls = element("div", "filterbar");
 const searchLabel = element("label", "field search", "检索数据表或字段");
 const input = element("input");
 input.type = "search";
 input.setAttribute("aria-label", "检索数据表或字段");
 searchLabel.append(input);
 const tableLabel = element("label", "field", "数据表");
 const select = element("select");
 select.setAttribute("aria-label", "数据表");
 tableLabel.append(select);
 controls.append(searchLabel, tableLabel);
 container.append(controls);
 const result = element("div");
 container.append(result);
 const show = () => {
  result.replaceChildren();
  const table = tables.find((item) => item.id === select.value);
  if (!table) {
   result.append(element("p", "empty", "没有匹配的数据表或字段"));
   return;
  }
  const heading = band(
   table.name,
   command("表定义与证据", () => openRecord(table), "text-link"),
  );
  heading.append(element("p", "description", table.summary));
  if (table.explanation) heading.append(explain(table));
  heading.append(columnDictionary(table));
  result.append(heading);
  const metadata = band("主键、索引与数据生命周期");
  metadata.append(tableMetadata(table));
  result.append(metadata);
  const diagrams = report.diagrams.filter(
   (record) =>
    record.type === "er" &&
    record.nodes.some((node) => node.entity === table.id),
  );
  for (const diagram of diagrams) {
   result.append(diagramPanel(diagram));
   const relations = band("关系字段与约束依据");
   for (const edge of diagram.edges) {
    const nodeMap = new Map(
     diagram.nodes.map((node) => [node.id, node.entity]),
    );
    if (
     nodeMap.get(edge.from) === table.id ||
     nodeMap.get(edge.to) === table.id
    ) {
     const entry = element("details", "detail-group");
     entry.append(
      element("summary", "", labels(edge.relationship) + " / " + edge.label),
      structured(edge),
     );
     relations.append(entry);
    }
   }
   result.append(relations);
  }
  if (!diagrams.length)
   result.append(
    element("p", "notice", "该表尚未纳入 ER 关系图，关系覆盖未完成。"),
   );
  icons();
 };
 const search = () => {
  const query = input.value.toLocaleLowerCase();
  select.replaceChildren();
  for (const table of tables) {
   const records = [
    table,
    ...(table.details.columns || []).map((identifier) =>
     entityById.get(identifier),
    ),
   ];
   if (!query || JSON.stringify(records).toLocaleLowerCase().includes(query))
    select.append(new Option(table.name, table.id));
  }
  show();
 };
 input.addEventListener("input", search);
 select.addEventListener("change", show);
 search();
}
async function prepareDiagramPrint() {
 for (const record of report.diagrams) await diagramSVG(record);
}
function addDiagramPrint(container) {
 for (const record of report.diagrams) {
  const section = element("section");
  section.append(
   element("h2", "", record.name),
   element("p", "", record.summary),
  );
  const theme =
   document.documentElement.dataset.theme === "dark" ? "dark" : "default";
  const source = diagramCache.get(record.id + ":" + theme);
  if (source) {
   const stage = element("div", "print-diagram");
   attachSVG(stage, source);
   section.append(stage);
  }
  section.append(structured(record));
  container.append(section);
 }
}
