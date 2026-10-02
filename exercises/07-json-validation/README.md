# 07 — JSON 與執行期驗證：422 是怎麼來的

兩台 Server 同時開著，才能看出責任歸屬。

```bash
# Terminal 1
cd 115-backend
source venv/bin/activate
fastapi dev examples/http-api/main.py        # 8000
```

```bash
# Terminal 2
cd 115-backend/exercises/07-json-validation
fastapi dev boom.py --port 8001              # 刻意會壞的那台
```

`boom.py` 只有一條路由 `/boom`，而且它會在處理時拋出例外。這是為了讓你看清楚 `500` 的樣子，不是要留到正式環境。

## 一、三種壞資料都是 422

```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' -d '{"role":"student"}'
curl -i -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' -d '{"name":""}'
curl -i -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' -d '{"name": "bob"'
```

三次都是 `422`。注意 JSON 格式錯那次的 `detail` 裡有 `loc: ["body", 14]`——數一下 Body 的字元，第 14 個就是那個沒被閉合的引號。

## 二、格式宣告錯，也是 422

```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: text/plain' -d '{"name":"bob"}'
```

Body 一個字都沒變，只有 `Content-Type` 變了。回 `422`，`detail` 的 `type` 是 `dict_type`。

## 三、Server 還活著

```bash
curl -i http://127.0.0.1:8000/health
```

`200` 加 `{"ok":true}`。這是分辨 `422` 與 `500` 最快的一條指令。

## 四、500 與它的線索

```bash
curl -i http://127.0.0.1:8001/boom
curl -i http://127.0.0.1:8001/health
```

第一個回 `500`，Body 只有一行 `Internal Server Error`。第二個回 `404`，代表同一個 process 還在回答，只是沒有 `/health` 這條路由。

線索在 Terminal 2：traceback 會指出 `boom.py` 的行號與 `ZeroDivisionError: division by zero`。

## 五、同一個錯參數，兩種狀態碼

```bash
curl -i 'http://127.0.0.1:8001/page?size=abc'
curl -i 'http://127.0.0.1:8001/manual-page?size=abc'
```

`/page` 的簽名是 `size: int`，框架在進 handler 之前就擋下來 → `422`，`loc` 是 `["query","size"]`。
`/manual-page` 的簽名是 `size: str`，`int(size)` 在 handler 裡拋例外 → `500`，Body 只有純文字。

兩次 Request 一模一樣。差別是型別宣告寫在哪裡。

## 六、錯誤 Body 的形狀來自框架

```bash
curl -s http://127.0.0.1:8000/openapi.json
```

找出 `components.schemas.HTTPValidationError` 與它底下的 `ValidationError`。Client 若直接讀 `detail[0].loc`，就綁死了這套框架；Status Line 上的 reason phrase `Unprocessable Entity` 連 OpenAPI 都沒有記錄。

## 繳交

1. 六組截圖，分別對應上面六節。
2. Terminal 2 的 traceback 截圖，要看得到檔名與行號。
3. 一句話回答：`422` 與 `500` 各自要動的是誰的什麼？寫成「動哪一邊的什麼」。
4. 一句話回答：為什麼 Client 不能只靠 Status Code 判斷「名稱重複」？寫成一個你可以真的執行的檢查方式。