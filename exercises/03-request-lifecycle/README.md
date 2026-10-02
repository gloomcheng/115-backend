# 03 — 後端怎麼接一個請求

兩個 Terminal 都開著。這一課的每一項證據都要同時看到兩邊。

```bash
# Terminal 1
cd 115-backend
source venv/bin/activate
fastapi dev examples/http-api/main.py
```

```bash
# Terminal 2
curl -v http://127.0.0.1:8000/health
```

## 一、五個階段各留一次證據

```bash
# 步驟 1：連線
curl -v http://127.0.0.1:8000/health 2>&1 | head -3
# 步驟 2：讀取（找那個孤立的 > 空行）
curl -v http://127.0.0.1:8000/health 2>&1 | grep -A1 'Accept'
# 步驟 3：解析
curl -i http://127.0.0.1:8000/request-info
# 步驟 4：比對
curl -i -X DELETE http://127.0.0.1:8000/health
# 步驟 5：執行
curl -s http://127.0.0.1:8000/health | wc -c
```

## 二、自己驗證位元組數

```bash
curl -s http://127.0.0.1:8000/health | wc -c
curl -i http://127.0.0.1:8000/health
```

`wc -c` 的輸出必須等於 Response 裡的 `content-length`。這個數字是框架數出來的，不是我寫的。

## 三、比對階段不會讓函式執行

```bash
curl -i -X DELETE http://127.0.0.1:8000/health
```

回 `405` 與 `allow: GET`。接著看 Terminal 1：只有一行 access log，沒有 traceback。

## 繳交

1. 完整 `curl -v` 截圖，必須包含 `*` 連線行、Request 的空行、`<` Status Line 與 `{ [11 bytes data]`，並在圖上標出五個階段各對應哪一行。
2. `wc -c` 與 `curl -i` 兩張截圖，證明 `11` 一致。寫出這個數字是誰算出來的。
3. `curl -i http://127.0.0.1:8000/request-info` 截圖，指出 `host` 在 Request 裡對應哪一個 Header。
4. `curl -i -X DELETE http://127.0.0.1:8000/health` 截圖，含 `405` 與 `allow: GET`。回答：這是在五個階段的哪一步決定的？函式有沒有執行？
5. Terminal 1 的 access log 截圖，四行，依時間順序標出各自的 Status Code。
6. 一句話：你寫的函式決定了 Response 的哪些部分？框架決定了哪些部分？