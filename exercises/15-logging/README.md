# 15 — 怎麼看 log

Client 拿到 500 只會得到五個字。真正的線索在 Server 終端機，而它和 access log 之間隔著一個 request id。

## 啟動

```bash
# Terminal 1
cd exercises/15-logging
fastapi dev main.py --port 8008
```

**Terminal 1 不要捲動太多。**看不見就會以為沒東西。

## 一、Client 拿到的全部

```bash
curl -i http://127.0.0.1:8008/boom
```

`500` 與 `Internal Server Error`。沒有檔名、沒有行號、沒有例外型別。

## 二、Terminal 1 裡的兩段文字

access log 那行：

```
INFO:     127.0.0.1:49945 - "GET /boom HTTP/1.1" 500 Internal Server Error
```

traceback 結尾（**倒數第三行才是答案**）：

```
  File ".../exercises/15-logging/main.py", line 55, in boom
    raise ValueError("something the handler could not handle")
ValueError: something the handler could not handle
```

看 traceback 從下往上讀，跳過所有不是你寫的檔案。

## 三、兩段沒有共用任何東西

access log 知道路徑和狀態碼，traceback 知道檔案和行號。**traceback 完全沒提到這次請求。**

數一下這兩行之間隔了多少行。這就是 debug 會變成不可能的原因。

## 四、request id 把它們接起來

沒有中介軟體時，應用程式 log 的 `request_id` 是 `-`：

```
2026-10-03 00:12:01,971 INFO  notes listing users count=1 request_id=-
```

`main.py` 已經寫好中介軟體，重啟後：

```bash
curl -i http://127.0.0.1:8008/users
```

回應有 `x-request-id: r0001`，Terminal 1 的 log 也有 `request_id=r0001`。**兩個地方同一個編號。**

## 五、query string 會把憑證寫進 log

用自訂 log 設定啟動一份（query string 預設就會被印出來）：

```bash
cat > /tmp/uvicorn-log.json <<'JSON'
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {"default": {"format": "%(asctime)s %(levelname)s %(message)s"}},
  "handlers": {"default": {
    "class": "logging.StreamHandler",
    "formatter": "default",
    "stream": "ext://sys.stdout"
  }},
  "loggers": {
    "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": false}
  }
}
JSON

uvicorn main:app --port 8009 --log-config /tmp/uvicorn-log.json
```

```bash
curl -s -o /dev/null 'http://127.0.0.1:8009/users?token=SECRETVALUE&page=2'
```

Terminal 會出現：

```
INFO 127.0.0.1:50183 - "GET /users?token=SECRETVALUE&page=2 HTTP/1.1" 200
```

**憑證已經在 log 裡了，而且不是刻意的。**憑證不該放在 query string，請用 `Authorization` Header。

## 六、一行危險的 log

```bash
curl -s -o /dev/null http://127.0.0.1:8008/admin
```

Terminal 1：

```
2026-10-03 00:12:52,872 INFO  notes admin viewed with token=Bearer eyJhbGciOiJIUzI1NiJ9.demo
```

**這行不能上線。**改成記 `request_id` 和 `sub` 就好。

## 繳交

1. `/boom` 的 `curl -i` 截圖（`500` + `Internal Server Error`）+ Terminal 的 access log 那一行 + traceback 結尾兩行（`main.py line 55` + `ValueError`）。Client 拿三個英文單字、21 個字元，Server 拿幾十行，中間少的是什麼？
2. 數出那兩行之間隔了幾行。API 每分鐘 800 個請求時會夾著幾行？為什麼這讓 debug 變成不可能？
3. `GET /users` 的 `x-request-id` 與 Terminal 對應 log 的截圖。這個 Header 和 access log 的存在理由有什麼不同？
4. `curl -i http://127.0.0.1:8008/users/iris` 記下 `x-request-id`，再 `grep` 那個編號，截圖必須是 0 筆。這條路由沒 log 是問題嗎？
5. `/admin` 含 token 的 log 截圖 + 你改寫後的版本。改寫後還剩多少診斷價值？丟掉的是什麼？
6. 自己寫一條 log，包含「發生了什麼、一個 request id、一個數量」，放在 `/users` 上，截圖必須含那一行和對應的 `x-request-id`。
7. `password`、`/users/iris` 這種資源路徑、`count=1` 這種數量、完整 request body — 各該不該寫進 log？哪一個會讓你猶豫？
8. 第五節的 `SECRETVALUE` 截圖 + 回答：token 搬到 `Authorization` Header 之後，log 會變成什麼？

## 繳交前

不要把你自己的 token、密碼或任何真實憑證寫進 `main.py` 或任何會被提交的檔案。`main.py` 必須維持原狀（第 1 步的狀態）。
