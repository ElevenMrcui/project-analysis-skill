def enrich_example(data):
    evidence = ["EV-DEMO"]
    records = {record["id"]: record for record in data["entities"]}
    data["project"]["description"] = "订单履约参考系统：客户提交订单，服务端核验并保存，后台发送通知。全部业务内容均为虚构示例。"
    data["evidence"][0].update(artifact="虚构演示模型", method="人工编写的演示数据，未读取真实业务源码", note="图示、解释和数据结构仅供展示，不代表真实系统的已验证行为。")
    explanations = {
        "FEATURE-CREATE": ("把客户确认的购物车变成可跟踪的订单。", ["客户提交购物车、地址和用于识别重复请求的幂等键。", "服务端检查权限、输入、库存及重复请求；不符合条件就拒绝。", "校验通过后保存订单，并在事务提交后安排通知。"], "说明性假设：同一客户连续提交两次相同幂等键，预期复用同一订单，而不是生成两份。", "权限不符、地址无效或库存不足时拒绝创建；事务失败时不保留本次写入。", [{"term": "幂等键", "meaning": "用来识别同一次业务请求的标识；重复请求应复用原结果。"}, {"term": "事务", "meaning": "一组数据库操作要么一起成功，要么一起撤回。"}]),
        "API-CREATE": ("接收前端创建订单的请求，并返回成功结果或明确的失败原因。", ["接收 POST /api/orders 及 Idempotency-Key 请求头。", "校验身份和请求，再交给订单服务处理。", "成功返回订单标识；失败返回对应状态码及原因。"], "说明性假设：库存不足时返回 409，前端展示库存冲突。", "校验失败不应创建订单；实际错误码和副作用须在目标项目中核验。", [{"term": "API", "meaning": "程序之间约定好的请求入口和数据格式。"}]),
        "TABLE-ORDERS": ("保存订单主记录；一行代表一个订单，包含所属租户、状态、总额和创建时间。", ["订单服务创建主记录，id 唯一标识该订单。", "tenant_id 指向所属租户，限定数据归属。", "履约过程更新 status；total 保存订单金额。"], "说明性假设：某个订单状态从 confirmed 变为 fulfilling，表示开始履约，不代表已送达。", "缺少必填字段或违反约束时写入失败；运行库约束尚未核验。", [{"term": "主键", "meaning": "唯一标识表中一行数据的字段或字段组合。"}, {"term": "外键", "meaning": "数据库约束，用来保证引用的另一张表记录确实存在。"}]),
        "JOB-NOTIFY": ("在订单保存后发送确认通知，避免客户一直等待通知服务响应。", ["接收订单创建事件。", "按 eventId 检查是否已处理，避免重复发送。", "失败时按有限次数重试，仍失败则交给故障处理流程。"], "说明性假设：邮件服务暂时不可用，订单仍已创建，通知稍后重试。", "通知失败不等于订单创建失败；超过重试次数的消息需处理。", [{"term": "死信队列", "meaning": "多次处理失败后暂存消息、等待排查或重放的地方。"}]),
    }
    for identifier, (purpose, steps, example, failure, terms) in explanations.items():
        records[identifier]["explanation"] = {"purpose": purpose, "howItWorks": steps, "example": example, "failure": failure, "boundaries": "以上为虚构行为模型，未通过真实源码、数据库或产品测试证实。", "terms": terms, "evidence": evidence}
    records["FEATURE-CREATE"]["details"].update(actors=["已登录客户"], trigger="提交已确认的购物车", permissions="当前租户内的 orders:create 权限", sideEffects=["保存订单", "记录待发送事件"], rules=["数量必须为正整数", "金额由服务端计算", "数据按租户隔离", "重复幂等键复用已有订单"], errors=["权限不足", "库存不足", "地址无效"], stateTransitions=["草稿 -> 已确认", "已确认 -> 履约中", "履约中 -> 已完成"])
    records["SERVICE-ORDER"]["details"].update(transaction="订单与 outbox 在同一事务提交", concurrency="幂等唯一约束，实际保障需源码核验", returns="订单结果")
    records["TABLE-ORDERS"]["details"].update(lifecycle="创建后随履约更新状态，按数据保留规则归档", schemaSource="虚构结构，非运行库元数据")
    records["API-CREATE"]["details"]["errors"] = {"400": "输入无效", "401": "未授权", "409": "库存冲突"}
    records["JOB-NOTIFY"]["details"].update(retry="指数退避，有限次数", idempotency="按 eventId 去重", failure="进入死信队列并告警")
    records["TEST-CREATE"]["details"] = {"execution": "仅示例用例清单，未在真实产品上执行", "cases": ["正常创建", "跨租户拒绝", "重复幂等键", "写入失败时事务回滚"]}
    records["RISK-SCHEMA"]["details"].update(severity="高", confidence="已知限制", action="获取授权后读取运行库结构元数据")
    comments = {"COL-ID": "唯一订单标识", "COL-TENANT": "所属租户标识", "COL-STATUS": "订单当前业务状态", "COL-TOTAL": "服务端计算的订单总额", "COL-CREATED": "订单创建时间"}
    for identifier, comment in comments.items():
        field = records[identifier]
        field["summary"] = comment
        field["details"].update(comment=comment, key="PK" if identifier == "COL-ID" else "FK" if identifier == "COL-TENANT" else "", sensitivity="财务数据" if identifier == "COL-TOTAL" else "内部业务数据")
        field["details"]["lineage"]["source"] = "订单服务校验后的输入或数据库生成值"
    records["COL-TENANT"]["details"].update(references=["TENANT-ID"], constraints=["NOT NULL", "FK -> tenancy.tenants.id", "ON DELETE RESTRICT"])
    records["COL-TOTAL"]["details"].update(precision=14, scale=2)
    new_records = [
        {"id": "TABLE-TENANTS", "kind": "table", "name": "tenancy.tenants", "summary": "租户主表；一行代表一个独立的数据归属单位。", "details": {"qualifiedName": "demo.tenancy.tenants", "columns": ["TENANT-ID", "TENANT-NAME"], "keys": ["PRIMARY KEY (id)"], "indexes": ["PRIMARY KEY (id)"], "lifecycle": "先建立租户，再关联其订单；有关联订单时拒绝删除", "readers": ["SERVICE-ORDER"], "writers": ["外部租户管理服务，示例范围外"], "schemaSource": "虚构结构，非运行库元数据"}, "explanation": {"purpose": "区分订单属于哪个组织；一行代表一个租户。", "howItWorks": ["建立租户标识和名称。", "订单通过 tenant_id 引用租户 id。", "删除仍有关联订单的租户时，外键限制会阻止删除。"], "example": "说明性假设：两个租户分别创建订单，数据归属由 tenant_id 区分。", "failure": "只存在外键并不能保证访问隔离，仍需要服务端权限校验。", "boundaries": "租户管理入口未包含在虚构示例范围中。", "terms": [{"term": "租户", "meaning": "使用同一系统、但需要区分数据归属的组织或客户单位。"}], "evidence": evidence}},
        {"id": "TENANT-ID", "kind": "column", "name": "tenants.id", "summary": "唯一租户标识", "details": {"parent": "TABLE-TENANTS", "dataType": "uuid", "nullable": False, "default": "生成 UUID", "key": "PK", "constraints": ["PRIMARY KEY", "NOT NULL"], "sensitivity": "内部标识", "comment": "订单引用的租户标识", "lineage": {"source": "租户管理服务", "target": "COL-TENANT"}}},
        {"id": "TENANT-NAME", "kind": "column", "name": "tenants.name", "summary": "租户显示名称", "details": {"parent": "TABLE-TENANTS", "dataType": "varchar(120)", "length": 120, "nullable": False, "default": "无默认值", "key": "", "constraints": ["NOT NULL"], "sensitivity": "组织信息", "comment": "用于区分租户的显示名称", "lineage": {"source": "租户管理服务", "target": "租户显示界面，示例范围外"}}},
    ]
    for record in new_records:
        record.update(repo="demo", module="tenancy", language="PostgreSQL", status="verified", evidence=evidence)
        data["entities"].append(record)
        data["discoveries"].append({"id": "DISC-" + record["id"], "scope": "虚构注册表", "method": "演示模型登记，非真实独立发现", "disposition": "mapped", "reason": "仅供展示", "entities": [record["id"]], "evidence": evidence})

    def diagram(identifier, kind, title, nodes, edges, direction="TB"):
        record = {"id": identifier, "type": kind, "name": title, "summary": "虚构示例：" + title + "。节点可关联对象详情，不能视为真实项目结论。", "status": "verified", "features": ["FEATURE-CREATE"], "evidence": evidence, "direction": direction, "nodes": [], "edges": []}
        for node_id, label, entity_id, shape in nodes:
            record["nodes"].append({"id": node_id, "label": label, "entity": entity_id, "shape": shape})
        for source, target, label in edges:
            record["edges"].append({"from": source, "to": target, "label": label, "evidence": evidence})
        data["diagrams"].append(record)
        return record

    components = [("web", "客户结算页 / React", "PAGE-CHECKOUT", "action"), ("api", "订单接口 / TypeScript", "API-CREATE", "action"), ("service", "订单服务 / 校验与事务", "SERVICE-ORDER", "action"), ("db", "订单存储 / PostgreSQL", "TABLE-ORDERS", "data"), ("event", "订单创建事件", "EVENT-CREATED", "action"), ("job", "确认通知 / Python", "JOB-NOTIFY", "action")]
    edges = [("web", "api", "HTTPS 请求"), ("api", "service", "经权限校验的调用"), ("service", "db", "事务写入"), ("service", "event", "提交后经 outbox 发布"), ("event", "job", "消息投递")]
    diagram("DIAG-ARCH", "architecture", "项目架构：请求、存储与通知边界", components, edges, "LR")
    diagram("DIAG-FLOW", "function-flow", "创建订单：从提交到结果", [("start", "客户提交购物车", "PAGE-CHECKOUT", "start"), ("check", "订单符合创建规则？", "FEATURE-CREATE", "decision"), ("save", "保存订单", "TABLE-ORDERS", "data"), ("notify", "返回结果并安排通知", "JOB-NOTIFY", "end"), ("reject", "展示拒绝原因", "PAGE-CHECKOUT", "end")], [("start", "check", "服务端校验"), ("check", "save", "是"), ("check", "reject", "否"), ("save", "notify", "事务提交成功")])
    diagram("DIAG-DETAIL", "detail-flow", "创建细节：权限、重复请求与回滚", [("start", "接收请求", "API-CREATE", "start"), ("auth", "当前租户权限通过？", "FEATURE-CREATE", "decision"), ("deny", "拒绝越权请求", "API-CREATE", "end"), ("duplicate", "已有相同幂等键？", "SERVICE-ORDER", "decision"), ("reuse", "返回已有订单", "API-CREATE", "end"), ("valid", "库存与输入有效？", "SERVICE-ORDER", "decision"), ("invalid", "返回校验错误", "API-CREATE", "end"), ("write", "事务写入并提交", "TABLE-ORDERS", "data"), ("commit", "提交成功？", "SERVICE-ORDER", "decision"), ("rollback", "撤回写入并返回错误", "SERVICE-ORDER", "end"), ("done", "返回订单并发布事件", "EVENT-CREATED", "end")], [("start", "auth", "校验"), ("auth", "deny", "否"), ("auth", "duplicate", "是"), ("duplicate", "reuse", "是"), ("duplicate", "valid", "否"), ("valid", "invalid", "否"), ("valid", "write", "是"), ("write", "commit", "提交"), ("commit", "rollback", "失败"), ("commit", "done", "成功")])
    diagram("DIAG-SEQUENCE", "sequence", "跨组件时序：提交、响应与异步通知", components, [("web", "api", "提交订单"), ("api", "service", "校验后的请求"), ("service", "db", "保存订单及待发布事件"), ("db", "service", "提交确认"), ("service", "api", "返回订单结果"), ("api", "web", "201 响应"), ("service", "event", "提交后发布事件"), ("event", "job", "异步消费")])
    diagram("DIAG-DATAFLOW", "dataflow", "租户字段流向：身份到存储", [("api", "请求身份 / 租户上下文", "API-CREATE", "action"), ("service", "校验当前租户的操作权限", "SERVICE-ORDER", "decision"), ("tenant", "tenant_id / 数据归属", "COL-TENANT", "data"), ("table", "订单按租户关联", "TABLE-ORDERS", "data")], [("api", "service", "可信身份上下文"), ("service", "tenant", "权限通过"), ("tenant", "table", "写入订单")], "LR")
    relation = diagram("DIAG-ER", "er", "数据表关系：租户与订单", [("tenants", "租户", "TABLE-TENANTS", "data"), ("orders", "订单", "TABLE-ORDERS", "data")], [("tenants", "orders", "tenants.id = orders.tenant_id")])
    relation["edges"][0].update(relationship="foreign-key", sourceCardinality="one", targetCardinality="many", sourceColumns=["TENANT-ID"], targetColumns=["COL-TENANT"], constraintName="fk_orders_tenant_id", onDelete="RESTRICT", onUpdate="NO ACTION")
    diagram("DIAG-LIFECYCLE", "lifecycle", "订单状态：确认到完成", [("draft", "草稿", "FEATURE-CREATE", "start"), ("confirmed", "已确认", "COL-STATUS", "action"), ("fulfilling", "履约中", "COL-STATUS", "action"), ("completed", "已完成", "COL-STATUS", "end")], [("draft", "confirmed", "创建成功"), ("confirmed", "fulfilling", "开始履约"), ("fulfilling", "completed", "履约完成")], "LR")
    data["relations"].append({"id": "REL-TENANT-ORDER", "from": "TABLE-ORDERS", "to": "TABLE-TENANTS", "kind": "FOREIGN_KEY", "label": "orders.tenant_id 引用 tenants.id", "status": "verified", "evidence": evidence, "details": {"relationship": "foreign-key", "sourceColumns": ["COL-TENANT"], "targetColumns": ["TENANT-ID"], "onDelete": "RESTRICT"}})
    for section in data["sections"]:
        section["details"] = {"scope": "虚构演示范围", "entities": section["entities"], "review": "真实分析时必须替换为源码和结构证据"}
        if section["id"] == "data":
            section.update(summary="2 张表、全部 7 个字段及租户与订单的关联；运行库未核验。", entities=["TABLE-ORDERS", "TABLE-TENANTS"])
    for chain in data["chains"]:
        chain["trigger"] = "客户提交订单" if chain["id"] == "CHAIN-CREATE" else "事务提交后发布订单创建事件"
    data["checks"][0].update(scope="虚构模型", result="示例记录已登记；未执行真实产品测试")