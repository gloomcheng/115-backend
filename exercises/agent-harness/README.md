# Agent Harness — 從單元 10 到期末專題

這不是一堂課的作業。**從單元 10 開始，每一個單元的 backend 主題同時就是 harness 的一塊；到期末專題發表時，它是一個跑得起來的系統。**

每一個單元都在同一個目錄 `exercises/agent-harness/` 裡加東西。加到最後，那個目錄就是你的期末專題。

## 為什麼要這樣排

Harness 是「把模型放進一個會產生機率性輸出的系統」裡的那個系統。它不是聊天框，是迴圈：收事件、驗證、記錄、重播、給下一輪。

而這個迴圈的每一段，本來就是 backend 的基本功：

| 單元 | 課程主題 | 這個單元 harness 長出什麼 | 這個單元要守住的規則 | 狀態 |
|---|---|---|---|---|
| 單元 10 | 驗證與錯誤 | `harness/validation.py`、`harness/events.py` | 進來的形狀先驗證再落盤；壞的結果永遠進不了事件記錄 | 完成 |
| 單元 11 | 登入與 JWT | `harness/authz.py` | 誰有權限寫事件、誰有權限讀狀態 | 完成 |
| 單元 12 | 中介軟體 | `harness/host.py`、`harness/state.py` | 驗證 → 權限 → 落盤 → 重播，每次呼叫走同一條鏈 | 完成 |
| 單元 13 | 測試 | `tests/test_state.py` | 重播規則的三條不變式寫成斷言 | 完成 |
| 單元 14 | API 家族 | `harness/tools.py` | 工具呼叫的介面與協定 | 完成 |
| 單元 15 | log | `harness/trace.py` | 一個 request id 貫穿 agent turn 與事件記錄 | 完成 |
| 單元 16 | Docker | `Dockerfile` | 把 harness 打包成一個映像 | 完成 |
| 單元 17 | VPS 上線 | `deploy/` | 讓 harness 在機器上活著，不只是一份程式碼 | 完成 |
| 期末專題 | 續接 | `harness/checkpoint.py`、`harness/appendix.py` | 續接之後，計畫不遺失 | 完成 |

每一課的講義都有一節「把它接回 harness」，指回這個目錄。

---

## 先把服務跑起來

```bash
cd exercises/agent-harness
pip install -r requirements.txt -r requirements-dev.txt
export HARNESS_SECRET='test-secret-not-for-production'
fastapi dev main.py --port 8010
```

`HARNESS_SECRET` 是簽章用的密鑰。整個 harness 從單元 11 開始都需要它，少了它就連第一個 token 都簽不出來。

---

# 單元 10：事件記錄，和擋在它前面的那道檢查

第 10 課講的是「檢查寫在哪裡，決定 Client 拿到什麼」。同一件事搬到 harness 身上：**模型送來的 tool result 是外部輸入**，它跟任何一個 request body 一樣，可能形狀不對。

這個單元的 harness 有兩件事：

1. `harness/validation.py` —— 一個 Pydantic 模型，站在入口，檢查 tool result 的形狀。
2. `harness/events.py` —— 一個 append-only 的事件記錄，一行一個 JSON 物件。

**這個單元的規則一句話：檢查不過的結果，永遠不會出現在事件記錄裡。**

> 單元 11 之後，請求還要多帶一個 token。下面的指令在單元 10 階段是原樣可跑的；到了單元 11，請照那一節的方式先把 token 準備好。

## 一、送一個 tool result 進去

```bash
curl -i -X POST http://127.0.0.1:8010/events/tool-result \
  -H 'Content-Type: application/json' \
  -d '{"tool_call_id":"call_1","tool_name":"todowrite","details":{"todos":[{"content":"write the replay tests","status":"pending"}]}}'
```

`201 Created`，body 是一個事件：

```json
{
  "event_id": "e3406a8ab325433798037f0258b83f05",
  "observed_at": "2026-10-24T10:03:06Z",
  "op": "tool_result",
  "payload": {
    "tool_call_id": "call_1",
    "tool_name": "todowrite",
    "is_error": false,
    "details": {"todos": [{"content": "write the replay tests", "status": "pending"}]}
  },
  "meta": {"subject": "root", "role": "admin", "trace_id": "63f37b5d32ba4882"}
}
```

`observed_at` 是 UTC，格式固定成 `2026-10-24T10:03:06Z`。時間格式不固定，之後第 15 課追 log 的時候就沒得追。

`payload` 是呼叫端給的資料，`meta` 是 host 自己的筆記（誰送的、屬於哪個 trace）。兩個分開放，讀 log 的人才不用猜哪一段是別人寫的。

## 二、同一個請求，少一個欄位

```bash
curl -i -X POST http://127.0.0.1:8010/events/tool-result \
  -H 'Content-Type: application/json' \
  -d '{"tool_name":"todowrite"}'
```

`422 Unprocessable Entity`，body 指出缺哪裡：

```json
{"detail":[{"type":"missing","loc":["body","tool_call_id"],"msg":"Field required","input":{"tool_name":"todowrite"}}]}
```

`loc` 是 `["body","tool_call_id"]`。這正是第 10 課第 02、03 節講的東西：驗證失敗要能指出**位置**，否則 Sender 只能整包重猜。

## 三、它有沒有寫進去？

```bash
curl -s http://127.0.0.1:8010/events
```

```json
{"count":1,"events":[{...}]}
```

`count` 是 **1**，不是 2。第一個請求被接受了，第二個被拒絕，而被拒的那個**沒有留下任何痕跡**——不是寫進去再標記失敗，是根本沒寫。

## 四、檔案長什麼樣

```bash
cat events.jsonl
```

```json
{"event_id": "04e5f86cac7a4afd827ade3272efa3d9", "meta": {"role": "admin", "subject": "root", "trace_id": "696eb8d499a84aa1"}, "observed_at": "2026-10-24T10:03:48Z", "op": "tool_result", "payload": {"details": {"todos": [{"content": "write the replay tests", "status": "pending"}]}, "is_error": false, "tool_call_id": "call_1", "tool_name": "todowrite"}}
```

一行一個 JSON 物件。格式故意做得很樸素：出事時你要能用 `cat`、`grep` 和文字編輯器直接看。

`events.jsonl` 已經進 `.gitignore`。這是本機的執行痕跡，不是原始碼。

---

# 單元 11：權限 — 誰可以寫事件，誰可以讀狀態

第 11 課講 JWT，形狀是三段、base64url、HMAC 簽章。harness 用的就是同一個形狀，而且**沒有套任何函式庫**，整個簽章流程在 `harness/authz.py` 裡只有二十幾行。

**這個單元的規則一句話：每個請求帶著一個角色，寫與讀都要先對角色。**

## 一、三個角色

| 角色 | 可以做什麼 |
|---|---|
| `reader` | 讀重播出來的狀態。不能寫事件。 |
| `writer` | 寫事件、讀狀態。 |
| `admin` | writer 做得到的都做得到，外加簽發新 token。 |

角色是分級的：`writer` 讀得到，`reader` 寫不了。權限表在 `ROLE_RANK` 裡，一張表就看完。

## 二、簽第一個 token

第一個 token 是用命令列簽的，不是在 API 裡簽的——因為簽 token 這件事本身需要權限。

```bash
export HARNESS_SECRET='test-secret-not-for-production'
export TOKEN=$(python -m harness.authz root admin)
echo "$TOKEN"
```

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkhBUk5FU1MifQ.eyJleHAiOjE3OTI4Mzk1OTAsInJvbGUiOiJhZG1pbiIsInN1YiI6InJvb3QifQ.<signature>
```

第三段是簽章，這裡用 `<signature>` 代替：把真的簽章貼進文件，等於教人把憑證貼進文件。

三段：中間那段 base64url 解開就是 `{"exp":...,"role":"admin","sub":"root"}`。

## 三、沒有 token 會怎樣

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8010/events
```

```text
401
```

`401` 的意思是「我還不知道你是誰」。簽章對不上也是 `401`，因為對呼叫端來說這是同一個問題：這個 token 不能用。

權限不夠是 `403`，那是另一件事：

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:8010/events/tool-result \
  -H "Authorization: Bearer $READER_TOKEN" -H 'Content-Type: application/json' \
  -d '{"tool_call_id":"call_1","tool_name":"todowrite"}'
```

```text
403
```

`403` 的意思是「我知道你是誰，而你的角色不能做這件事」。兩個狀態碼分開，是因為修法完全不同：前者要重新登入，後者要換角色。

## 四、管理員可以簽別人的 token

```bash
curl -s -X POST 'http://127.0.0.1:8010/tokens?subject=carol&role=reader' \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"token":"<the signed token>","subject":"carol","role":"reader","issued_by":"root"}
```

---

# 單元 12：中介軟體 — 每次呼叫走同一條鏈

第 12 課講中介軟體，講的是「同一段邏輯不該在每個 handler 裡重複寫」。harness 的版本更嚴格一點：**順序也要固定**。

**這個單元的規則一句話：驗證 → 權限 → 落盤 → 重播，每次呼叫走同一條鏈。**

這條鏈在 `harness/host.py` 的 `Host` 裡，四個步驟各一個方法：

| 步驟 | 誰在做 | 為什麼在這個位置 |
|---|---|---|
| 驗證 | `ToolResultIn.model_validate` | 形狀不對的請求沒有答案，回 422 |
| 權限 | `require_role` | 知道你是誰不代表你可以做這件事 |
| 落盤 | `EventLog.append` | 只有前兩關過了才寫 |
| 重播 | `replay` | 現在是什麼，由整份 log 算出來，不另外存一份 |

順序不能換。驗證放前面，是因為形狀不對的輸入根本不值得為它查權限；權限放落盤前面，是因為不該替沒有權限的人寫東西。

## 重播出來的狀態

```bash
curl -s http://127.0.0.1:8010/state -H "Authorization: Bearer $TOKEN"
```

```json
{
  "todos": [
    {"content": "write the replay tests", "status": "pending"},
    {"content": "design the replay rules", "status": "completed"}
  ],
  "counts": {"pending": 1, "in_progress": 0, "completed": 1, "cancelled": 0, "unknown": 0},
  "confirmed": true,
  "source_event_id": "e3406a8ab325433798037f0258b83f05",
  "updated_at": "2026-10-24T10:03:06Z",
  "last_failed_event_id": null
}
```

`source_event_id` 是這份狀態來自哪一個事件。有它，狀態就可以回頭查證。

## 失敗的寫入不是狀態

```bash
curl -s -X POST http://127.0.0.1:8010/events/tool-result \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"tool_call_id":"call_9","tool_name":"todowrite","is_error":true,"details":{"todos":[]}}'
```

再讀一次 `/state`，`todos` 還是小寫那兩筆，`last_failed_event_id` 指向剛剛那個失敗的事件。

**失敗的寫入是證據，不是狀態。** 它確實發生過，所以它進 log；但它沒有改變任何事實，所以它不改變狀態。而先前那筆確認過的寫入**仍然成立**——它還是目前為止最後一件確定發生的事。

---

# 單元 13：測試 — 把重播規則寫成斷言

第 13 課講測試。harness 的重播規則是三句話，所以測試就寫三個斷言，每一個斷言的名字就是那一條規則。

**這個單元的規則一句話：重播的三條不變式，各有一個斷言。**

| 不變式 | 測試名 |
|---|---|
| 同一份 log 永遠重播成同一個狀態 | `test_the_same_log_always_replays_to_the_same_state` |
| 追加不會改寫已經寫下的東西，所以狀態是整份歷史的函數 | `test_appending_does_not_rewrite_an_earlier_event` |
| 失敗的寫入不是狀態 | `test_a_failed_write_after_a_confirmed_one_leaves_the_confirmed_state_standing` |

```bash
pytest -q
```

```text
60 passed
```

```bash
pytest -q -k state
```

只看那三條不變式。

---

# 單元 14：API 家族 — 工具呼叫的介面與協定

第 14 課講 API 家族：一組服務共用同一個形狀，呼叫端才猜得到會拿到什麼。harness 的每一個工具都寫在同一個協定上。

**這個單元的規則一句話：加一個工具是加一筆 entry，不是在 host 裡加一個分支。**

呼叫與結果是兩個形狀，這是刻意的：

```json
// 呼叫：想做什麼
{"tool_call_id": "call_1", "tool_name": "todowrite", "arguments": {"todos": [...]}}

// 結果：發生了什麼
{"tool_call_id": "call_1", "tool_name": "todowrite", "is_error": false, "details": {...}}
```

分開的好處在於**失敗寫進去時看得出來**。

## 目錄

```bash
curl -s http://127.0.0.1:8010/tools -H "Authorization: Bearer $TOKEN"
```

每個工具都帶著自己的參數 schema，呼叫端在呼叫之前就知道要給什麼。

## 呼叫一個工具

```bash
curl -s -X POST http://127.0.0.1:8010/tools \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"tool_call_id":"call_1","tool_name":"todowrite","arguments":{"todos":[{"content":"write the replay tests","status":"pending"}]}}'
```

## 兩種失敗不一樣

| 失敗 | 發生在哪裡 | 會不會進 log |
|---|---|---|
| 形狀不對 | 進 handler 之前 | **不會**。這是單元 10 的規則。 |
| 執行失敗 | 工具跑了，但是失敗了 | **會**，而且標成 `is_error: true` |

執行失敗要進 log，因為「那個工具失敗了」是關於世界的一件事，而 log 就是放事實的地方。它只是**不是狀態**。

---

# 單元 15：log — 一個 request id 貫穿整條鏈

第 15 課講 log。第一個問題永遠是「這筆是哪個請求的？」沒有答案的 log 只是一堆東西。

**這個單元的規則一句話：一個請求一個 id，那個 id 落在這個請求產生的每一個事件上。**

## 每一個回應都帶著 id

```bash
curl -s -i http://127.0.0.1:8010/health | grep -i trace
```

```text
x-trace-id: be1606826d85467a
```

## 呼叫端可以帶自己的 id

```bash
curl -s -i -X POST http://127.0.0.1:8010/events/tool-result \
  -H "Authorization: Bearer $TOKEN" \
  -H 'X-Trace-Id: 0123456789abcdef' \
  -H 'Content-Type: application/json' \
  -d '{"tool_call_id":"call_1","tool_name":"todowrite"}' | grep -i trace
```

```text
x-trace-id: 0123456789abcdef
```

呼叫端帶來的 id 只有形狀對才會被採用。id 完全由呼叫端控制，兩個請求就可能撞到同一個 id，所以形狀不對的會被丟掉換一個新的，而不是「修正」成原來那個——改了等於連結斷了。

## 事件上也有 id

```bash
curl -s http://127.0.0.1:8010/events -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

```json
"meta": {"role": "admin", "subject": "root", "trace_id": "63f37b5d32ba4882"}
```

有了它，一個數字就能把整個請求從 log 裡撈出來。

---

# 單元 16：Docker — 把 harness 打包成一個映像

第 16 課講容器。容器不是一台比較小的電腦，它是一個自己的 `127.0.0.1`，這件事決定了健康檢查要寫哪個位址。

**這個單元的規則一句話：映像是換得掉的，log 不是——所以 log 不在映像裡。**

## 建 image

```bash
cd exercises/agent-harness
docker build --target runtime -t harness-runtime .
```

三個 stage：`base` 裝 runtime 相依套件、`test` 多裝 pytest、`runtime` 是一個沒有 root 權限的使用者。

## 在容器裡跑測試

```bash
docker build --target test -t harness-test .
docker run --rm harness-test
```

```text
............................................................             [100%]
60 passed in 0.16s
```

## 起服務

```bash
docker volume create harness-log
docker run -d --name harness \
  -p 127.0.0.1:8011:8010 \
  -v harness-log:/var/lib/agent-harness \
  -e HARNESS_SECRET='test-secret-not-for-production' \
  harness-runtime
```

```bash
curl -s http://127.0.0.1:8011/health
```

```json
{"ok":true}
```

## log 落在 volume 上

```bash
docker exec harness cat /var/lib/agent-harness/events.jsonl
```

```json
{"event_id": "04e5f86cac7a4afd827ade3272efa3d9", "meta": {"role": "admin", "subject": "root", "trace_id": "696eb8d499a84aa1"}, "observed_at": "2026-10-24T10:03:48Z", "op": "tool_result", "payload": {"details": {"todos": [{"content": "write the replay tests", "status": "pending"}]}, "is_error": false, "tool_call_id": "call_1", "tool_name": "todowrite"}}
```

容器用 `docker rm` 刪掉之後，這一行還在。**那才是重點**：映像可以換，log 不能。

---

# 單元 17：VPS 上線 — 讓 harness 在機器上活著

第 17 課講上 VPS。交付的不是「網頁打得開」這句話，而是 Request 通過每一關的證據。

**這個單元的規則一句話：服務要活著，而且要在重開機之後還活著。**

## 安裝

```bash
sudo bash deploy/install.sh
```

安裝腳本做這些事：建立 `harness` 系統使用者、把程式裝到 `/opt/agent-harness`、建立 virtual environment、準備 `/var/lib/agent-harness`、在 `/etc/agent-harness/env` 產生一組隨機密鑰、裝上 systemd unit、啟用服務。

密鑰是隨機產生而且**不會被印出來**。它在一個只有 root 讀得到（`0640`）的檔案裡，由 `EnvironmentFile` 讀進去，不在命令列上——命令列是全世界讀得到的。

## systemd unit

```bash
systemctl status harness
systemctl restart harness
journalctl -u harness -f
```

unit 裡的加固不是裝飾：

| 設定 | 擋掉什麼 |
|---|---|
| `ProtectSystem=strict` | 除了明講的路徑，檔案系統全部唯讀 |
| `ReadWritePaths=/var/lib/agent-harness` | 唯一能寫的地方就是 log 的目錄 |
| `NoNewPrivileges=true` | 拿不到比啟動時更高的權限 |
| `PrivateTmp=true` | 看不到別人的 `/tmp` |
| `ProtectHome=true` | 看不到 `/home` |

服務只綁 `127.0.0.1`，對外由 nginx 進來。`deploy/nginx.conf` 是那份設定。

## 驗收

```bash
curl -fsS http://127.0.0.1:8010/health
sudo systemctl is-enabled harness
sudo systemctl is-active harness
```

---

# 期末專題：續接之後，計畫不遺失

一個 session 結束之後，下一個 session 怎麼接上，而且不用把整份逐字稿重讀一遍？

直覺答案是「寫一段摘要」。那個答案是錯的，原因要講準確：**摘要是散文，而散文是副本。同一件事的兩份副本會開始分歧，一旦有人改其中一份，沒有人能說得清哪一份才對。**

所以這裡的 checkpoint 分成兩半：

- **散文**說工作要去哪裡，並指向附錄。它**不列**任務。
- **附錄**放任務清單，版本化的結構化格式，程式讀得懂。

**期末專題的規則一句話：任務清單只存在一份，在附錄裡，散文指向它。**

## 看看它長什麼樣

```bash
curl -s 'http://127.0.0.1:8010/checkpoint?goal=ship%20the%20replay%20tests' \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

```json
{
  "prose": "Goal: ship the replay tests\n\nThe task list is in the appendix below. That appendix is the only copy of it.",
  "appendix": "<harness-context version=\"1\">\n  <task-state confirmed=\"true\" source-event-id=\"e3406a8ab325433798037f0258b83f05\" updated-at=\"2026-10-24T10:03:06Z\">\n    <todo status=\"pending\">write the replay tests</todo>\n    <todo status=\"completed\">design the replay rules</todo>\n  </task-state>\n</harness-context>"
}
```

散文裡**沒有**任務清單。清單只在附錄裡，而且附錄有版本號——不知道版本的讀者，不知道自己在看什麼。

## 附錄讀得回來

```python
from harness.appendix import parse_appendix

parsed = parse_appendix(appendix)
```

```python
{'version': 1, 'confirmed': True, 'source_event_id': 'e3406a8ab325433798037f0258b83f05', 'updated_at': '2026-10-24T10:03:06Z', 'todos': [{'status': 'pending', 'content': 'write the replay tests'}, {'status': 'completed', 'content': 'design the replay rules'}]}
```

附錄是寫給程式看的，那程式就得讀得回去。這個往返測試就是防止格式慢慢變成只有人看得懂的最後一道保險。

## 這個專題要交的

1. `curl -s http://127.0.0.1:8010/checkpoint` 的輸出截圖，必須同時看得到散文與附錄。
2. 回答一句話：**為什麼附錄要有版本號？**
3. `pytest -q -k checkpoint` 截圖。
4. 回答一句話：**如果散文也把任務清單列出來，會發生什麼事？**
5. 用 `python -m harness.authz` 簽一個 `reader` token，證明 reader 讀得到 `/state` 但寫不了 `/events/tool-result`，兩張截圖並排。
6. `docker build --target test -t harness-test . && docker run --rm harness-test` 的截圖，必須是 `60 passed`。
7. `systemctl status harness` 的截圖。
