# Log Troubleshooting Playbook

> 使用判据：触发条件 = 按所属 SKILL.md 进入本 reference 时；动作要求 = 按本 reference 的步骤、模板或清单执行；判断标准 = 输出满足所属 SKILL.md 的完成标准；失败处理 = 信息缺失时暂停并说明缺失项，不得跳过或伪造。

> 通用生产排查命令与模板，配合 `SKILL.md` 使用。所有命令默认只读；涉及写操作前必须获得用户明确授权。
> `<...>` 为占位符，执行时替换为当前环境的值。不要把密码、Token、连接串写入命令历史或文档。

## 1. 先对齐环境 [S-PTS-R1-01]

> 触发条件：执行本节流程时。
> 动作要求：按本节步骤、约束和示例执行；涉及用户确认、写操作、外部调用或其他状态变更时先满足前置条件。
> 判断标准：本节要求的步骤、输出或检查项全部完成，并能定位到实际产物或证据；未完成项标明阻断。
> 失败或例外处理：前置条件不满足或信息缺失时暂停并说明缺失项，不得跳过或伪造结果。

确认日志、进程、数据和部署版本属于同一个环境：

```bash
# 运行配置/环境标识（按项目实际文件调整）
grep -RIn "active\|profile\|environment" config/ 2>/dev/null | head

# 进程
ps -ef | grep java | grep -v grep
pgrep -a java

# 容器
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
kubectl get pods -n <namespace>

# 部署版本/启动时间
ls -l <应用目录>/<jar或可执行文件>
```

检查点：

- 日志中的进程 ID / 容器名 / 启动时间是否与当前运行实例一致；
- 日志中的业务数据能否在当前配置的数据源中查到；
- 本地快照的截止时间是否覆盖失败时间；不覆盖时标注“生产当前值需复核”。

## 2. 日志盘点 [S-PTS-R1-02]

```bash
LOG_DIR="<日志目录>"

find "$LOG_DIR" -maxdepth 3 -type f \
  \( -name "*.log" -o -name "*.log.gz" -o -name "*.gz" \) | sort
```

> 已经 `cd` 到日志目录时，`find` 的第一个参数用 `.`，不要写 `find logs`，否则会找 `logs/logs`。

## 3. 搜当前日志 [S-PTS-R1-03]

> 触发条件：执行本节流程时。
> 动作要求：按本节步骤、约束和示例执行；涉及用户确认、写操作、外部调用或其他状态变更时先满足前置条件。
> 判断标准：本节要求的步骤、输出或检查项全部完成，并能定位到实际产物或证据；未完成项标明阻断。
> 失败或例外处理：前置条件不满足或信息缺失时暂停并说明缺失项，不得跳过或伪造结果。

```bash
KEYWORD="<接口名/任务名/异常类名>"

# 带文件名、行号
grep -a -n -H "$KEYWORD" "$LOG_DIR"/*.log

# 只看最后 20 条
grep -a "$KEYWORD" "$LOG_DIR"/*.log | tail -20

# 实时跟踪（-F 可在轮转后继续跟随）
tail -F "$LOG_DIR"/*.log | grep --line-buffered "$KEYWORD"

# 全词匹配，避免相似名称误命中
grep -a -w -n -H "$KEYWORD" "$LOG_DIR"/*.log
```

- `-a`：按文本处理，避免“二进制文件”提示；
- `-n`：行号；
- `-H`：输出文件名；
- `-w`：全词匹配。

如果系统有 `rg`，大目录下更快：

```bash
rg -n --no-heading "$KEYWORD" "$LOG_DIR"
```

## 4. 搜轮转/压缩日志 [S-PTS-R1-04]

```bash
# 单个压缩包
zgrep -a -n -H "$KEYWORD" "$LOG_DIR/archives/xxx.log.gz"

# 所有压缩包
find "$LOG_DIR" -type f -name "*.gz" -print0 \
  | xargs -0 zgrep -a -n -H "$KEYWORD"

# 当前日志 + 压缩包
find "$LOG_DIR" -type f \
  \( -name "*.log" -o -name "*.log.gz" -o -name "*.gz" \) \
  -exec zgrep -a -n -H "$KEYWORD" {} + 2>/dev/null
```

按日期/最近几天过滤：

```bash
# 文件名包含某一天
find "$LOG_DIR" -type f -name "*2026-10-20*" \
  \( -name "*.log" -o -name "*.log.gz" -o -name "*.gz" \) \
  -exec zgrep -a -n -H "$KEYWORD" {} + 2>/dev/null

# 最近 3 天修改过的日志
find "$LOG_DIR" -type f -mtime -3 \
  \( -name "*.log" -o -name "*.log.gz" -o -name "*.gz" \) \
  -exec zgrep -a -n -H "$KEYWORD" {} + 2>/dev/null
```

## 5. 时间窗口 [S-PTS-R1-05]

日志行通常以 `日期 时间` 开头：

```bash
zcat "$LOG_DIR/archives/xxx.log.gz" \
  | awk '$1=="2026-10-20" && $2>="15:40:00" && $2<="15:50:00"'
```

统计并保存：

```bash
zgrep -a -n -H "$KEYWORD" "$LOG_DIR"/archives/*.gz \
  | tee /tmp/${KEYWORD}_result.log \
  | wc -l
```

## 6. 大文件与编码 [S-PTS-R1-06]

> 触发条件：执行本节流程时。
> 动作要求：按本节步骤、约束和示例执行；涉及用户确认、写操作、外部调用或其他状态变更时先满足前置条件。
> 判断标准：本节要求的步骤、输出或检查项全部完成，并能定位到实际产物或证据；未完成项标明阻断。
> 失败或例外处理：前置条件不满足或信息缺失时暂停并说明缺失项，不得跳过或伪造结果。

需要多次分析时，先解压一次：

```bash
gzip -dc "xxx.log.gz" > /tmp/xxx.log
```

文件名带空格要加引号：

```bash
gunzip -c "app - 2026-10-20 10_59_19.log.gz" \
  > "app - 2026-10-20 10_59_19.log"
```

中文乱码先确认编码，再转码：

```bash
file some.log
iconv -f GBK -t UTF-8 some.log | grep "<中文关键字>"
```

即使中文乱码，ASCII 的接口路径、异常类名、线程名、ORM 标记仍然可搜。

## 7. 串一次请求 [S-PTS-R1-07]

> 触发条件：执行本节流程时。
> 动作要求：按本节步骤、约束和示例执行；涉及用户确认、写操作、外部调用或其他状态变更时先满足前置条件。
> 判断标准：本节要求的步骤、输出或检查项全部完成，并能定位到实际产物或证据；未完成项标明阻断。
> 失败或例外处理：前置条件不满足或信息缺失时暂停并说明缺失项，不得跳过或伪造结果。

1. **找入口**：前端按钮/定时任务 → 请求 URL/方法名 → Controller/Consumer/Job。
2. **找开始/结束**：请求日志的 start/end、线程、requestId/traceId、操作人。
3. **算耗时**：几毫秒通常是取数/校验/组装；几百毫秒到数秒可能是附件/文件/网络；10 秒以上重点看超时。
4. **拿业务 ID**：ORM 的 `Preparing`/`Parameters`、请求体、消息头、日志埋点。
5. **查数据**：用业务 ID 查失败行之前使用的字段。

常见 ORM 日志：

```text
==>  Preparing: SELECT ... FROM <table> WHERE id = ?
==> Parameters: <businessId>(String)
```

跨归档追同一个 requestId/traceId：

```bash
zgrep -a -n -H "<requestId>" "$LOG_DIR"/archives/*.gz
```

## 8. 异常映射 [S-PTS-R1-08]

> 触发条件：从日志中识别到异常类型、需要判断失败阶段时。

| 异常 | 常见阶段 | 下一步 |
|---|---|---|
| `NullPointerException` | 取数/组装，对象或字段为空 | 用业务 ID 查字段 |
| `IllegalArgumentException` | 参数/空 ID | 查请求参数 |
| `BadSqlGrammarException` | SQL/映射 | 查 Mapper、表结构 |
| `MailException` / `SendFailedException` / `Invalid Addresses` | SMTP/收件人/附件 | 查 To/Cc、SMTP 账号、附件 |
| `ConnectException` / `SocketTimeoutException` | 下游/网络 | 查目标地址、端口、超时 |
| `NoClassDefFoundError` | 构建/依赖 | 查打包产物、classpath |
| `OutOfMemoryError` | 内存 | dump、堆分析 |

包装异常不保留原因时（例如自定义异常重写了 `getMessage()`），要取 cause 的消息，或查看标准输出/控制台里的完整堆栈。

## 9. 数据核对 [S-PTS-R1-09]

> 触发条件：执行本节流程时。
> 动作要求：按本节步骤、约束和示例执行；涉及用户确认、写操作、外部调用或其他状态变更时先满足前置条件。
> 判断标准：本节要求的步骤、输出或检查项全部完成，并能定位到实际产物或证据；未完成项标明阻断。
> 失败或例外处理：前置条件不满足或信息缺失时暂停并说明缺失项，不得跳过或伪造结果。

先读失败代码行，列出它在此之前使用的字段，再查数据：

```sql
SELECT <失败行之前使用的字段>
FROM <table>
WHERE <主键> = '<businessId>';
```

检查：

- 字段是否为空、是否为默认值；
- 关联主数据是否存在（合同、客户、用户、附件记录）；
- 状态值是否在允许范围内；
- 同一业务 ID 是否存在多条/重复数据；
- 失败时间前后是否有其他写入。

数据问题不要只凭一条 `SELECT` 下结论；对照代码分支和业务规则。

## 10. 容器与系统日志 [S-PTS-R1-10]

> 触发条件：执行本节流程时。
> 动作要求：按本节步骤、约束和示例执行；涉及用户确认、写操作、外部调用或其他状态变更时先满足前置条件。
> 判断标准：本节要求的步骤、输出或检查项全部完成，并能定位到实际产物或证据；未完成项标明阻断。
> 失败或例外处理：前置条件不满足或信息缺失时暂停并说明缺失项，不得跳过或伪造结果。

```bash
# Docker
docker logs --since 2026-10-20T15:00:00 <container> 2>&1 | grep -a "<keyword>"

# Kubernetes
kubectl logs <pod> -n <namespace> --since=1h | grep -a "<keyword>"
kubectl logs <pod> -n <namespace> --previous | grep -a "<keyword>"

# systemd
journalctl -u <service> --since "2026-10-20 15:00:00" | grep -a "<keyword>"
```

`printStackTrace()` 往往只写标准输出；应用日志文件里没有堆栈时，优先查容器/系统日志。

## 11. 定时任务 [S-PTS-R1-11]

```bash
crontab -l
ls /etc/cron.d/
grep -r "<keyword>" /etc/cron* 2>/dev/null

# 所有用户的 crontab
for user in $(cut -f1 -d: /etc/passwd); do
  echo "=== $user ==="
  crontab -u "$user" -l 2>/dev/null
done
```

检查：调度时间、执行用户、工作目录、环境变量、脚本权限、上一次执行结果。

## 12. 数据库侧（谨慎） [S-PTS-R1-12]

> 触发条件：执行本节流程时。
> 动作要求：按本节步骤、约束和示例执行；涉及用户确认、写操作、外部调用或其他状态变更时先满足前置条件。
> 判断标准：本节要求的步骤、输出或检查项全部完成，并能定位到实际产物或证据；未完成项标明阻断。
> 失败或例外处理：前置条件不满足或信息缺失时暂停并说明缺失项，不得跳过或伪造结果。

`general_log` 会写大量数据，**只能在测试环境短时间开启**，用完立即关闭：

```sql
SET GLOBAL log_output = 'TABLE';
SET GLOBAL general_log = 'ON';

-- 复现后查询
SELECT event_time, command_type, argument
FROM mysql.general_log
WHERE argument LIKE '%<table>%'
  AND command_type = 'Query'
ORDER BY event_time DESC
LIMIT 100;

SET GLOBAL general_log = 'OFF';
```

只读排查：

```sql
SHOW FULL PROCESSLIST;
SHOW EVENTS FROM `<database>`;
SHOW VARIABLES LIKE 'event_scheduler';
SELECT TRIGGER_NAME, EVENT_OBJECT_TABLE, EVENT_MANIPULATION, ACTION_TIMING
FROM information_schema.TRIGGERS
WHERE EVENT_OBJECT_SCHEMA = '<database>';
```

## 13. 安全与脱敏 [S-PTS-R1-13]

> 触发条件：执行本节流程时。
> 动作要求：按本节步骤、约束和示例执行；涉及用户确认、写操作、外部调用或其他状态变更时先满足前置条件。
> 判断标准：本节要求的步骤、输出或检查项全部完成，并能定位到实际产物或证据；未完成项标明阻断。
> 失败或例外处理：前置条件不满足或信息缺失时暂停并说明缺失项，不得跳过或伪造结果。

- 不输出密码、Token、Cookie、Authorization、数据库连接串；
- 客户邮箱、手机号、身份证号用 `<masked>`；
- 分享日志前替换敏感字段；
- 生产环境禁止未经授权执行 `UPDATE`、`DELETE`、`TRUNCATE`、重启、改配置、跑迁移；
- 需要状态变更时，先说明证据、影响面、回滚方式，并等待用户明确批准。

## 14. 命令速查 [S-PTS-R1-14]

> 触发条件：需要具体日志、进程或容器命令时。

| 目的 | 命令 |
|---|---|
| 列日志 | `find "$LOG_DIR" -maxdepth 3 -type f \( -name "*.log" -o -name "*.log.gz" -o -name "*.gz" \) \| sort` |
| 搜当前日志 | `grep -a -n -H "$KEYWORD" "$LOG_DIR"/*.log` |
| 搜压缩日志 | `zgrep -a -n -H "$KEYWORD" "$LOG_DIR"/archives/*.gz` |
| 当前+归档 | `find "$LOG_DIR" -type f \( -name "*.log" -o -name "*.log.gz" -o -name "*.gz" \) -exec zgrep -a -n -H "$KEYWORD" {} + 2>/dev/null` |
| 最近 3 天 | `find "$LOG_DIR" -type f -mtime -3 \( -name "*.log" -o -name "*.gz" \) -exec zgrep -a -n -H "$KEYWORD" {} +` |
| 实时跟踪 | `tail -F "$LOG_DIR"/*.log \| grep --line-buffered "$KEYWORD"` |
| 时间窗口 | `zcat file.gz \| awk '$1=="2026-10-20" && $2>="15:00:00"'` |
| 异常上下文 | `zgrep -a -n -B5 -A40 "NullPointerException" file.gz` |
| 解压 | `gunzip -c "file.gz" > "file.log"` |
| 转码 | `iconv -f GBK -t UTF-8 file.log \| grep "<关键字>"` |
| 容器日志 | `docker logs --since 1h <container> 2>&1 \| grep -a "<keyword>"` |
| K8s 日志 | `kubectl logs <pod> -n <ns> --previous \| grep -a "<keyword>"` |
| systemd | `journalctl -u <service> --since "2026-10-20 15:00:00" \| grep -a "<keyword>"` |
| 进程 | `ps -ef \| grep java \| grep -v grep`；`pgrep -a java` |
