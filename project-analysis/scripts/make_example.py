import argparse
from pathlib import Path

from analyze import SECTIONS, initialize, now, render, validate, write_json
from example_models import enrich_example


def example():
    manifest = {"schemaVersion": 1, "generatedAt": now(), "root": {"id": "demo", "name": "Synthetic fulfillment example", "revision": "synthetic-example-v1", "dirty": False}, "files": [], "scanErrors": []}
    data = initialize([manifest], "订单履约 · 参考工作区")
    data["project"].update(description="Commerce reference / React + TypeScript + Python + PostgreSQL", example=True)
    data["evidence"] = [{"id": "EV-DEMO", "artifact": "Synthetic fixture", "locator": "make_example.py:example", "method": "Authored demonstration, not source inspection", "snapshot": "synthetic-example-v1", "note": "所有业务内容均为虚构示例，不代表当前工作区存在订单系统。"}]

    def entity(identifier, kind, name, summary, details, language="TypeScript", module="orders"):
        data["entities"].append({"id": identifier, "kind": kind, "name": name, "summary": summary, "repo": "demo", "module": module, "language": language, "status": "verified", "evidence": ["EV-DEMO"], "details": details})

    entity("FEATURE-CREATE", "feature", "创建订单", "从购物车确认到订单持久化及异步通知的示例业务能力。", {"actors": ["Customer"], "trigger": "提交已确认购物车", "rules": ["商品数量为正整数", "服务端计算金额", "租户隔离", "重复幂等键返回已有订单"], "inputs": ["cartId", "shippingAddressId", "idempotencyKey"], "outputs": ["orderId", "status", "total"], "errors": ["库存不足", "无效地址", "授权失败"], "permissions": "orders:create in current tenant", "sideEffects": ["TABLE-ORDERS", "EVENT-CREATED"], "tests": ["TEST-CREATE"], "stateTransitions": ["draft -> confirmed", "confirmed -> fulfilling", "fulfilling -> completed"]})
    entity("PAGE-CHECKOUT", "page", "Checkout / 结算页", "校验地址和购物车状态，提交订单后同步页面状态。", {"route": "/checkout", "actions": ["确认地址", "提交订单", "重试失败请求"], "states": ["loading", "ready", "submitting", "success", "error"], "permissions": "authenticated customer", "accessibility": "Form errors associated with fields"}, "React / TypeScript", "storefront")
    entity("API-CREATE", "api", "POST /api/orders", "鉴权、参数校验、幂等检查后交由领域服务执行。", {"protocol": "HTTP JSON", "operation": "POST /api/orders", "request": {"cartId": {"type": "uuid", "required": True}, "shippingAddressId": {"type": "uuid", "required": True}, "Idempotency-Key": {"location": "header", "type": "string"}}, "response": {"201": {"orderId": "uuid", "status": "confirmed"}}, "errors": {"400": "invalid input", "401": "unauthorized", "409": "insufficient stock"}, "authorization": "tenant-scoped orders:create", "consumers": ["PAGE-CHECKOUT"]})
    entity("SERVICE-ORDER", "symbol", "OrderService.create", "在事务内创建订单与待发布事件。", {"signature": "create(input, tenant, idempotencyKey)", "transaction": "order + outbox atomic commit", "concurrency": "unique idempotency constraint", "returns": "OrderResult"})
    entity("TABLE-ORDERS", "table", "commerce.orders", "订单主表，保留租户、金额、状态与创建时间。", {"qualifiedName": "demo.commerce.orders", "columns": ["COL-ID", "COL-TENANT", "COL-STATUS", "COL-TOTAL", "COL-CREATED"], "keys": ["PRIMARY KEY (id)"], "indexes": ["(tenant_id, created_at DESC)"], "lifecycle": "Create on confirmation; transition on fulfillment", "readers": ["API-CREATE", "JOB-NOTIFY"], "writers": ["SERVICE-ORDER"], "schemaSource": "Synthetic schema, not live metadata"}, "PostgreSQL")
    columns = [("COL-ID", "id", "uuid", "generated", "internal"), ("COL-TENANT", "tenant_id", "uuid", "none", "tenant identifier"), ("COL-STATUS", "status", "order_status", "confirmed", "internal"), ("COL-TOTAL", "total", "numeric(14,2)", "none", "financial"), ("COL-CREATED", "created_at", "timestamptz", "now()", "internal")]
    for identifier, name, data_type, default, sensitivity in columns:
        entity(identifier, "column", "orders." + name, "示例字段：" + name, {"parent": "TABLE-ORDERS", "dataType": data_type, "nullable": False, "default": default, "constraints": ["NOT NULL"], "sensitivity": sensitivity, "lineage": {"source": "OrderService validated input or generated value", "target": "commerce.orders." + name}}, "PostgreSQL")
    entity("EVENT-CREATED", "event", "order.created.v1", "通过 outbox 发布的订单创建事件。", {"channel": "orders.events", "schema": {"eventId": "uuid", "orderId": "uuid", "tenantId": "uuid", "occurredAt": "timestamp"}, "producers": ["SERVICE-ORDER"], "consumers": ["JOB-NOTIFY"], "delivery": "at-least-once", "failure": "outbox retry then dead-letter review"})
    entity("JOB-NOTIFY", "job", "SendOrderConfirmation", "消费创建事件，生成通知并记录发送结果。", {"trigger": "order.created.v1", "inputs": ["eventId", "orderId"], "outputs": ["notification delivery record"], "retry": "exponential backoff, bounded attempts", "idempotency": "eventId deduplication", "failure": "dead-letter queue and alert"}, "Python / Celery", "notifications")
    entity("TEST-CREATE", "test", "Order creation contract", "示例验收场景清单，未在真实应用上执行。", {"execution": "not run; synthetic fixture", "cases": ["valid order", "cross-tenant denial", "duplicate idempotency key", "outbox rollback on failure"]}, "TypeScript / pytest", "quality")
    entity("FLAG-NOTIFY", "flag", "ORDER_CONFIRMATION_ENABLED", "控制订单通知消费者是否发送消息的示例开关。", {"default": True, "scope": "environment", "affects": ["JOB-NOTIFY"], "secret": False}, "Configuration", "operations")
    entity("DEPLOY-API", "deployment", "Order API deployment", "示例构建、迁移、滚动发布与健康检查阶段。", {"stages": ["build", "unit/contract tests", "image", "migration", "rolling deploy", "readiness"], "rollback": "previous image; schema rollback separately assessed", "runtimeObserved": False}, "Kubernetes", "operations")
    entity("RISK-SCHEMA", "risk", "运行库结构尚未核验", "未连接数据库，不能将示例结构解释为真实数据库元数据。", {"severity": "high", "confidence": "known limitation", "action": "Collect approved read-only catalog metadata"}, "PostgreSQL", "assurance")
    path = ["PAGE-CHECKOUT", "API-CREATE", "SERVICE-ORDER", "TABLE-ORDERS"]
    relationships = [("PAGE-CHECKOUT", "API-CREATE", "HTTP_CALLS", "POST /api/orders"), ("API-CREATE", "SERVICE-ORDER", "CALLS", "validated create"), ("SERVICE-ORDER", "TABLE-ORDERS", "WRITES", "transactional insert"), ("SERVICE-ORDER", "EVENT-CREATED", "PRODUCES", "outbox commit"), ("EVENT-CREATED", "JOB-NOTIFY", "CONSUMES", "async delivery")]
    for index, (source, target, kind, label) in enumerate(relationships, 1):
        data["relations"].append({"id": "REL-" + str(index), "from": source, "to": target, "kind": kind, "label": label, "status": "verified", "evidence": ["EV-DEMO"]})
    data["chains"] = [{"id": "CHAIN-CREATE", "name": "订单提交 / 事务持久化", "status": "verified", "steps": path, "relations": ["REL-1", "REL-2", "REL-3"], "trigger": "Customer confirms checkout", "outcome": "订单与 outbox 在同一事务中持久化，响应返回订单标识。", "alternatives": [{"condition": "validation fails", "result": "400; no write"}, {"condition": "stock conflict", "result": "409; transaction rollback"}], "evidence": ["EV-DEMO"]}, {"id": "CHAIN-NOTIFY", "name": "异步通知 / 消费与重试", "status": "verified", "steps": ["SERVICE-ORDER", "EVENT-CREATED", "JOB-NOTIFY"], "relations": ["REL-4", "REL-5"], "trigger": "outbox dispatcher publishes committed event", "outcome": "幂等消费并发送订单确认通知。", "alternatives": [{"condition": "delivery failure", "result": "bounded retry then DLQ"}], "evidence": ["EV-DEMO"]}]
    descriptions = {
        "scope": ("范围与证据边界", "虚构的前后端联合分析样例；没有扫描实际业务仓库。", []),
        "architecture": ("架构与系统边界", "React 入口、TypeScript API、Python 消费者和 PostgreSQL 存储。", ["PAGE-CHECKOUT", "API-CREATE", "JOB-NOTIFY", "TABLE-ORDERS"]),
        "features": ("业务能力与规则", "订单创建、校验、幂等、事务及通知的示例业务规则。", ["FEATURE-CREATE"]),
        "frontend": ("页面与交互状态", "结算页的加载、提交、失败和成功状态。", ["PAGE-CHECKOUT"]),
        "api": ("接口契约与联调", "请求字段、认证要求、响应结构与错误语义。", ["API-CREATE"]),
        "data": ("数据字典与血缘", "订单表示例及全部 5 个字段；未连接运行数据库。", ["TABLE-ORDERS"]),
        "chains": ("同步与异步链路", "请求事务链路和异步事件消费链路分别表达。", ["SERVICE-ORDER", "EVENT-CREATED"]),
        "jobs": ("后台任务与消息", "消费者的重试、去重与失败处理。", ["JOB-NOTIFY"]),
        "configuration": ("配置与功能开关", "环境级通知开关及影响范围。", ["FLAG-NOTIFY"]),
        "security": ("权限与数据边界", "租户隔离和创建订单权限为示例规则。", ["FEATURE-CREATE"]),
        "testing": ("测试与验收", "仅列出示例用例，不宣称真实产品测试通过。", ["TEST-CREATE"]),
        "delivery": ("构建、发布与回滚", "构建产物、数据库迁移、滚动发布与就绪检查。", ["DEPLOY-API"]),
        "operations": ("运维与故障恢复", "失败事件与运行库证据仍需在真实分析中核验。", ["JOB-NOTIFY"]),
        "dependencies": ("依赖与许可证", "示例未包含实际项目依赖清单。", []),
        "risks": ("风险与待核实事项", "明确区分示例事实、运行库缺口和真实项目结论。", ["RISK-SCHEMA"]),
        "coverage": ("覆盖率与对账", "零源文件分母显示未计量，不能显示 100%。", []),
    }
    data["sections"] = []
    for identifier in SECTIONS:
        title, summary, entities = descriptions[identifier]
        data["sections"].append({"id": identifier, "title": title, "summary": summary, "status": "unknown" if identifier == "data" else "verified", "entities": entities, "evidence": ["EV-DEMO"], "details": {"scope": "synthetic demonstration only", "entities": entities, "review": "Replace with observed source evidence when analyzing a real project"}})
    data["discoveries"] = [{"id": "DISC-" + record["id"], "scope": "synthetic fixture", "method": "Authored example registry", "disposition": "mapped", "reason": "Synthetic example mapping", "entities": [record["id"]], "evidence": ["EV-DEMO"]} for record in data["entities"]]
    data["checks"] = [{"id": "CHECK-DEMO", "scope": "synthetic fixture", "status": "passed", "result": "Example registry mapped; no actual project tests executed", "evidence": ["EV-DEMO"]}]
    data["gaps"] = [{"id": "GAP-LIVE-DB", "status": "open", "summary": "示例未读取真实数据库和业务源码。", "nextAction": "在目标项目运行本 Skill，收集真实源码和经授权的结构元数据。"}]
    enrich_example(data)
    return data, manifest


def main():
    parser = argparse.ArgumentParser(description="Generate an explicitly synthetic offline preview")
    parser.add_argument("--workspace", default=".")
    arguments = parser.parse_args()
    root = Path(arguments.workspace).resolve() / "docs"
    data, manifest = example()
    write_json(root / "project-analysis" / "example.json", data)
    write_json(root / "project-analysis" / "inventory-demo.json", manifest)
    write_json(root / "project-analysis" / "coverage-example.json", validate(data, [manifest]))
    for diagram in data["diagrams"]:
        write_json(root / "project-analysis" / "diagrams" / (diagram["id"] + ".json"), diagram)
    render(data, [manifest], root / "project-analysis.html")
    print(str(root / "project-analysis.html"))


if __name__ == "__main__":
    main()