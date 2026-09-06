# 图示与数据字典

## 必需图示

项目架构图必须展示真实组件、运行边界和通信方向。每个功能必须关联功能流程图与细节流程图，后者覆盖关键判断、失败、权限、重试、回滚和终态。按实际场景补充时序图、数据流向图、生命周期图。数据库项目的每张表必须纳入 ER 图；不存在关系的表也需保留为孤立节点并说明原因。

大项目拆为总览和模块图，所有细节均可访问，不用一张大图代替完整分析。中文节点名称先描述动作/业务含义，再保留必要原始标识。每张图给出一句解释、范围和证据；不要把图当作没有说明的装饰。

## 模型契约

`analysis.json` 中的 `diagrams` 为独立记录集合。记录含 `id`、`type`、中文 `name`/`summary`、`status`、`evidence`、`features`、`nodes`、`edges` 和可选 `direction`（`LR`/`TB`）。

- `type`：`architecture`、`function-flow`、`detail-flow`、`sequence`、`dataflow`、`er`、`lifecycle`。
- `features`：被本图覆盖的功能实体 ID。填写 ID 不等于证明图已覆盖全部分支，仍需语义审阅。
- 节点：`id`、`label`、可选 `entity`，以及 `shape`（`action`、`decision`、`data`、`start`、`end`）。
- 边：`from`、`to`、`label`、`evidence`；每条边单独引用证据，不能用两个节点的证据代替边的证据。
- ER 节点必须绑定 `table` 实体；全部字段从对应表的 `details.columns` 及字段实体取得。
- ER 边另含 `relationship`（`foreign-key`、`logical`、`inferred`）、`sourceCardinality`/`targetCardinality`（`one`、`zero-or-one`、`many`、`one-or-many`）、`sourceColumns`/`targetColumns`，可补 `constraintName`、`onDelete`、`onUpdate`。

实体 ID 与图节点 ID 属于不同命名空间；跨记录引用必须显式绑定。基数、连接字段与约束方向需要从定义和代码验证，不能根据一对多图形倒推事实。Mermaid 是本包内置离线渲染器；此模型不是 Archify 原生 IR。使用 Archify 时按其实际版本转换并保存验证结果。

## 数据字典

每张表展示业务含义、一行代表什么、完整限定名、当前/历史状态、全部字段、键/约束/索引、读写者、生命周期和证据。

每个字段独立成实体，并展示原名、中文业务含义、类型、长度/精度/小数位、可空、默认值、生成方式、主外键/唯一键、检查约束、注释、敏感级别、来源/去向。缺少字段含义或现场结构时标为待核实，不能根据名称编造。

关系区同时展示连接列、基数、物理外键还是逻辑关联、证据、删除和更新规则。复合键逐列对应；多态关联、跨库关联、隐含 ORM 关系不能伪装成数据库外键。继承、关联表、历史表、触发器副作用和跨系统同步都需单独解释。

## 验收

逐表对比原始发现字段 ID 与字典字段 ID，并核对 ER 图是否使用同一数据源。逐功能对比决定点和分支台账，核对图中成功与失败路径。浏览器验证每种图可渲染、文字可读、缩放与详情可操作。未执行真实业务测试时，不能以示例图渲染成功替代业务验证。