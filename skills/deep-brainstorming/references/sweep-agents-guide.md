# 多维度信息搜集 Agent 指南（深度脑暴专用）

Phase 1 的核心是**并行派出多个 agent，每个从不同维度搜集信息**，确保分析建立在全面的事实基础上，而不是单一视角的片面理解。

> 下文 Prompt 模板和搜集要点中出现的 `application.yml`、`项目指令文件「域知识沉淀」`、`memory/` 等是具体项目的示例路径，**仅为示例**。跨项目使用时替换为目标项目的配置文件、指令文件（项目实际采用的 agent 指令文件命名）和经验存储位置；搜集维度本身（代码/业务/历史/数据/外部参考）是通用的。

## 维度清单

### 1. Code Search Agent（代码搜索）

**职责**：从代码层面搜集与问题相关的所有技术事实。

**搜集内容**：
- 相关函数、方法、接口的签名和实现
- 调用链（谁调用谁，数据怎么流转）
- 状态字段、枚举值、条件分支
- 配置项、常量、字典映射
- 相关的 Entity、DTO、Mapper XML

**工具**：Grep, Glob, Read

**Prompt 模板**：
```
你是代码搜索 agent。请从代码层面搜集与以下问题相关的所有技术事实：

问题：{problem_description}

搜索要求：
1. 搜索相关的函数、方法、接口（Grep 关键函数名、接口路径）
2. 追踪调用链（谁调用谁，数据怎么流转）
3. 找到相关的状态字段、枚举值、条件分支
4. 找到相关的 Entity、DTO、Mapper XML

输出格式（JSON）：
{
  "findings": [
    {
      "type": "function|interface|entity|config|mapping",
      "file": "文件路径",
      "name": "函数/类/接口名",
      "summary": "一段话说明其职责和关键逻辑",
      "codeAnchor": "文件:行号 或 类名#方法名"
    }
  ],
  "gaps": ["搜索过程中发现但无法确认的信息缺口"],
  "confidence": 0.0-1.0,
  "sources": ["文件路径列表"]
}
```

### 2. Business Context Agent（业务上下文）

**职责**：从文档和业务规则层面搜集约束条件和历史决策。

**搜集内容**：
- docs/ 目录下的设计文档、业务规则文档
- 项目指令文件（项目实际采用的 agent 指令文件，如 `AGENTS.md`）中的业务域知识（如「域知识沉淀」章节）
- memory/ 中的历史经验和决策记录
- 相关的注释、TODO、FIXME

**工具**：Read, Grep

**Prompt 模板**：
```
你是业务上下文 agent。请搜集与以下问题相关的业务规则、约束条件和历史决策：

问题：{problem_description}

搜索要求：
1. 搜索 docs/ 目录下的相关设计文档和业务规则
2. 搜索项目指令文件（项目实际采用的 agent 指令文件命名）中的相关业务域知识
3. 搜索 memory/ 中的相关历史经验和决策记录
4. 搜索代码中的相关注释、TODO、FIXME

输出格式（JSON）：
{
  "findings": [
    {
      "type": "business_rule|constraint|decision|todo",
      "source": "来源文件或位置",
      "content": "具体的业务规则/约束/决策内容",
      "relevance": "与当前问题的关联说明"
    }
  ],
  "gaps": ["发现但无法确认的业务规则或约束"],
  "confidence": 0.0-1.0,
  "sources": ["文件路径列表"]
}
```

### 3. Historical Experience Agent（历史经验）

**职责**：从过去类似问题的解决方案中提取经验。

**搜集内容**：
- 会话记忆检索工具（如 episodic-memory 类 MCP，可用时）中类似问题的解决方案
- git 历史中的相关修复记录
- memory/ 中记录的经验教训

**工具**：会话可用的记忆检索工具（如 episodic-memory 类 MCP 的 search 工具，工具名以当前环境实际注册的为准）, Bash (git log)

**Prompt 模板**：
```
你是历史经验 agent。请搜集与以下问题相关的历史解决方案和经验教训：

问题：{problem_description}

搜索要求：
1. 使用会话中可用的记忆检索工具搜索过去类似问题的解决方案；当前环境没有此类工具时跳过并在 gaps 中说明
2. 搜索 memory/ 中的相关经验记录
3. 如适用，搜索 git log 中的相关修复记录

输出格式（JSON）：
{
  "findings": [
    {
      "type": "solution|lesson|pattern",
      "source": "来源（session ID、commit、memory 文件）",
      "problem": "当时遇到的问题",
      "solution": "当时的解决方案",
      "effectiveness": "方案效果（如有记录）",
      "relevance": "与当前问题的关联"
    }
  ],
  "gaps": ["历史经验中缺失的部分"],
  "confidence": 0.0-1.0,
  "sources": ["来源列表"]
}
```

### 4. Data Verification Agent（数据验证）

**职责**：从数据库层面验证实际数据状态，确认假设是否成立。

**搜集内容**：
- 相关表的实际数据样本
- 数据分布、异常值、空值统计
- 关联数据的完整性
- 状态字段的当前值和历史变更

**工具**：Bash (SQL 查询)

**Prompt 模板**：
```
你是数据验证 agent。请通过数据库查询验证与以下问题相关的数据状态：

问题：{problem_description}

验证要求：
1. 查询相关表的数据样本（SELECT * FROM table WHERE ... LIMIT N）
2. 检查数据分布和异常值（COUNT、GROUP BY、MIN/MAX）
3. 验证关联数据的完整性（JOIN 检查外键）
4. 检查状态字段的当前值

注意：
- 先读取 application.yml 获取数据库连接信息
- 查询前先确认表名和字段名（从代码中的 Entity/Mapper 获取）
- 禁止修改数据，只做 SELECT 查询
- 敏感数据脱敏处理

输出格式（JSON）：
{
  "findings": [
    {
      "type": "data_sample|distribution|anomaly|integrity",
      "table": "表名",
      "query": "执行的 SQL",
      "result": "查询结果摘要（脱敏）",
      "observation": "观察到的数据特征"
    }
  ],
  "gaps": ["需要但无法查询的数据"],
  "confidence": 0.0-1.0,
  "sources": ["表名列表"]
}
```

### 5. External Reference Agent（外部参考）

**职责**：从外部资源搜集行业最佳实践和类似系统的设计参考。

**搜集内容**：
- 类似系统的架构设计
- 行业最佳实践和标准
- 技术方案的优劣对比
- 相关框架/库的文档

**工具**：WebSearch, WebFetch

**Prompt 模板**：
```
你是外部参考 agent。请搜集与以下问题相关的行业最佳实践和设计参考：

问题：{problem_description}

搜索要求：
1. 搜索类似系统的解决方案
2. 搜索行业最佳实践和标准
3. 搜索相关技术方案的对比分析

输出格式（JSON）：
{
  "findings": [
    {
      "type": "best_practice|architecture|comparison",
      "source": "来源 URL 或文档名",
      "summary": "方案摘要",
      "applicability": "对当前问题的适用性评估"
    }
  ],
  "gaps": ["外部参考中未覆盖的方面"],
  "confidence": 0.0-1.0,
  "sources": ["URL 或文档列表"]
}
```

## 维度选择决策树

```
问题类型是什么？
├── 代码/Bug 类
│   └── 必选：代码搜索 + 数据验证 + 历史经验
│       可选：业务上下文（如果涉及业务规则）
│
├── 业务决策类
│   └── 必选：业务上下文 + 历史经验
│       可选：外部参考 + 代码搜索
│
├── 架构/设计类
│   └── 必选：代码搜索 + 外部参考 + 业务上下文
│       可选：历史经验
│
├── 数据问题类
│   └── 必选：数据验证 + 代码搜索 + 业务上下文
│       可选：历史经验
│
└── 综合/复杂类
    └── 全部 5 个维度
```

## 并行执行方式

按以下三档优先级并行派出 agent，差别只在并发度，信息覆盖不变：

**首选：动态 Workflow 的并行编排**（宿主平台提供 Workflow/CreateWorkflow 类多 agent 编排能力且用户已 opt-in 时）

按宿主平台的 workflow API 将各维度作为并行子任务派出，每个维度绑定统一的结果 schema；API 形态以当前平台文档为准，能力等价即可。

**默认：同一轮并行派发多个 Agent 工具调用**（Workflow 不可用或未 opt-in 时）

各维度互不依赖，把多个 Agent 调用放在同一轮一次性发出，不要串行 await。每个 Agent 的 prompt 用本文件上方的模板，约束同下。

**兜底：串行逐维度搜集**（Agent 工具也不可用时）

按维度选择决策树依次执行，每个维度结果格式不变，最后统一汇总。

**注意**：
- 每个 agent 独立运行，互不依赖
- 并行度受宿主平台并发限制（通常 10 个上下）；默认档同理，一轮内并行 Agent 调用数也受平台并发限制
- 如果某个 agent 返回 null（失败或被跳过），不影响其他 agent
- 所有 agent 完成后，汇总结果进入 Phase 2

## 结果汇总

所有 agent 返回后，汇总为统一的事实基线：

```text
## 搜集结果汇总

### 确认事实（有代码/数据支撑）
- [来自 Code Search] ...
- [来自 Data Verification] ...

### 业务约束
- [来自 Business Context] ...

### 历史经验
- [来自 Historical Experience] ...

### 外部参考
- [来自 External Reference] ...

### 信息缺口（所有 agent 共同发现）
- [缺口 1]：需要补充 {具体内容}
- [缺口 2]：需要补充 {具体内容}

### 置信度评估
| 维度 | 置信度 | 说明 |
|------|--------|------|
| 代码搜索 | X.X | ... |
| 业务上下文 | X.X | ... |
| ... | ... | ... |
```
