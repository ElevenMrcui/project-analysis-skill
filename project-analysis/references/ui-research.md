# UI 设计参考与采用记录

## GitHub 检索

核实日期：2026-09-06。以下为当次 GitHub API 返回的快照，Star 会变化，不是全站排名或质量认证。

| 项目 | Star 快照 | 本次读取的规范 | 采用内容 |
| --- | ---: | --- | --- |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 125,327 | `.claude/skills/ui-ux-pro-max/SKILL.md` | 产品类型优先、信息层级、语义色、可见焦点、触控尺寸、图表及响应式检查 |
| [UI Skills](https://github.com/ibelick/ui-skills) | 8,154 | `skills/baseline-ui/SKILL.md` | 数字等宽、标题平衡、控件命名、原生可访问性、减少动效、避免装饰堆叠 |

还检索到 OpenPencil、baoyu-design、Nothing Design Skill。没有因为 Star 数选择不同产品类型的模板，也没有叠加多个互相冲突的风格体系。

原先指定的 [taste-skill](https://github.com/Leonxlnx/taste-skill)、[impeccable](https://github.com/pbakaus/impeccable)、[archify](https://github.com/tt-a1i/archify) 的来源与方法保留在 [设计及集成指南](./design-and-integrations.md)。后续部分 GitHub API 请求返回 403，未为这些项目补写未核实的 Star 数。

## 本包视觉方向

中文工程分析工作台，不是营销首页。采用炭黑导航、浅灰正文、朱红定位色和青绿数据色；Avenir Next 与中文系统字体组合，数字和代码标识采用等宽显示。使用细分隔线建立信息层级，不把所有章节做成卡片。

图示使用统一主题；默认保留可读比例，过宽时在图区域滚动，另有适应宽度。数据字典先展示中文业务解读，再展示全部字段。详情、检索、证据和导出必须继续可用，视觉优化不能减少记录。

## 集成边界

本次实际读取 UI UX Pro Max 和 Baseline UI 的上游 Skill 文本，并选择适合现有原生 HTML/JavaScript 的规则落实到模板。没有安装其运行时、执行其检索 CLI 或宣称通过其自动审计。Baseline UI 的 Tailwind/React 专用要求不适用于本包，未为改版迁移技术栈。

taste-skill、impeccable 和 archify 的可核实方法作为工作流参考；本次未执行 Archify CLI。图形渲染实际使用内嵌 Mermaid，不冒充 Archify 原生渲染。

## 离线第三方资源

- Mermaid 10.9.3：`assets/mermaid.min.js`，保留 `assets/MERMAID-LICENSE`。
- Lucide 0.468.0：`assets/lucide.min.js`，保留 `assets/LUCIDE-LICENSE`。
- 未捆绑上述设计 Skill 项目的完整源码；引用规范不代表获得商标或品牌授权。