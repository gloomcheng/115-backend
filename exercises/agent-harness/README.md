# Agent Harness — 從單元 10 到期末專題

這不是一堂課的作業。**從單元 10 開始，每一個單元的 backend 主題同時就是 harness 的一塊；到期末專題發表時，它是一個跑得起來的系統。**

每一個單元都在同一個目錄 `exercises/agent-harness/` 裡加東西。加到最後，那個目錄就是你的期末專題。

## 為什麼要這樣排

Harness 是「把模型放進一個會產生機率性輸出的系統」裡的那個系統。它不是聊天框，是迴圈：收事件、驗證、記錄、重播、給下一輪。

而這個迴圈的每一段，本來就是 backend 的基本功：

| 單元 | 課程主題 | 這個單元 harness 長出什麼 | 這個單元要守住的規則 |
|---|---|---|---|
| 單元 10 | 驗證與錯誤 | `harness/validation.py`、`harness/events.py` | 進來的形狀先驗證再落盤；壞的結果永遠進不了事件記錄 |
| 單元 11 | 登入與 JWT | `harness/authz.py` | 誰有權限寫事件、誰有權限讀狀態 |
| 單元 12 | 中介軟體 | `harness/host.py`、`harness/state.py` | 驗證 → 權限 → 落盤 → 重播，每次呼叫走同一條鏈 |
| 單元 13 | 測試 | `tests/test_state.py` | 重播規則的三條不變式寫成斷言 |
| 單元 14 | API 家族 | `harness/tools.py` | 工具呼叫的介面與協定 |
| 單元 15 | log | `harness/trace.py` | 一個 request id 貫穿 agent turn 與事件記錄 |
| 單元 16 | Docker | `Dockerfile` | 把 harness 打包成一個映像 |
| 單元 17 | VPS 上線 | `deploy/` | 讓 harness 在機器上活著，不只是一份程式碼 |
| 期末專題 | `harness/checkpoint.py`、`harness/appendix.py` | 續接之後，計畫不遺失 |

單元 10 到單元 17，每一課的講義都會有一節「把它接回 harness」，指回這個目錄。期末專題把八個單元的東西收成一份可以發表的專題。

---

# 單元 10：事件記錄，和擋在它前面的那道檢查

第 10 課講的是「檢查寫在哪裡，決定 Client 拿到什麼」。同一件事搬到 harness 身上：**模型送來的 tool result 是外部輸入**，它跟任何一個 request body 一樣，可能形狀不對。

所以這個單元的 harness 有兩件事：

1. `harness/validation.py` —— 一個 Pydantic 模型，站在入口，檢查 tool result 的形狀。
2. `harness/events.py` —— 一個 append-only 的事件記錄，一行一個 JSON 物件。

**這個單元的規則一句話：檢查不過的結果，永遠不會出現在事件記錄裡。** 記錄檔只裝被接受的東西，所以讀它的人不必猜某一行可不可信。

## 啟動

```bash
cd exercises/agent-harness
fastapi dev main.py --port 8010
```

## 一、送一個 tool result 進去

```bash
curl -i -X POST http://127.0.0.1:8010/events/tool-result \
  -H 'Content-Type: application/json' \
  -d '{"tool_call_id":"call_1","tool_name":"todowrite","details":{"todos":[{"content":"write the replay tests","status":"pending"}]}}'
```

`201 Created`，body 是一個事件：

```json
{
  "event_id": "45712ffb6e20453baeb09507eaed6609",
  "observed_at": "2026-10-24T02:55:48Z",
  "op": "tool_result",
  "payload": {
    "tool_call_id": "call_1",
    "tool_name": "todowrite",
    "is_error": false,
    "details": {"todos": [{"content": "write the replay tests", "status": "pending"}]}
  }
}
```

注意 `observed_at` 是 UTC，格式固定成 `2026-10-24T02:55:48Z`。時間格式不固定，之後第 15 課追 log 的時候就沒得追。

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

這是這個單元唯一要記住的事。事件記錄是 harness 的記憶；記憶裡混著「其實失敗過」的東西，之後每一次重播都要先懷疑它。

## 四、檔案長什麼樣

```bash
cat events.jsonl
```

```json
{"event_id": "45712ffb6e20453baeb09507eaed6609", "observed_at": "2026-10-24T02:55:48Z", "op": "tool_result", "payload": {"details": {"todos": [{"content": "write the replay tests", "status": "pending"}]}, "is_error": false, "tool_call_id": "call_1", "tool_name": "todowrite"}}
```

一行一個 JSON 物件。格式故意做得很樸素：出事時你要能用 `cat`、`grep` 和文字編輯器直接看。

`events.jsonl` 已經進 `.gitignore`。這是本機的執行痕跡，不是原始碼。

## 五、測試

```bash
pytest -q
```

十條測試，全部在講同一件事：被拒的結果不會落盤。

```bash
pytest -q -k rejected
```

只看那兩條。`test_a_rejected_result_never_reaches_the_log` 是這個單元的證據。

## 這個單元你要交的

1. `curl` 送出那個少 `tool_call_id` 的請求，截圖必須包含 `422` 與 `loc`。
2. `curl -s http://127.0.0.1:8010/events` 截圖，`count` 必須是 `1`。
3. `cat events.jsonl` 截圖。
4. `pytest -q` 截圖，必須是 `10 passed`。
5. 回答一句話：**如果把驗證拿掉，只保留寫檔，會發生什麼事？**（提示：先想想第 08 課 `POST /users` 沒驗證 `admin` 欄位時，那個欄位去哪了。）
