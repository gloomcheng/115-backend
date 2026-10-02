# 04 — 路由與你的第一條程式

這一課你要**先寫，再讀**。路由表只有在你親手加過一筆、又親手改錯一次之後，才會變成可以拿來預測的工具。

```bash
# Terminal 1
cd 115-backend
source venv/bin/activate
fastapi dev examples/http-api/main.py
```

## 一、寫下你自己的兩條路由

在 `main.py` 的 `health()` **上方**加這兩條（加在上方是為了讓它們比 `/users/{name}` 先被比對到）：

```python
@app.get("/notes")
def list_notes():
    return {"notes": ["buy milk"]}


@app.get("/notes/{note_id}")
def read_note(note_id: int):
    return {"id": note_id, "text": "buy milk"}
```

```bash
# Terminal 2
curl -i http://127.0.0.1:8000/notes
```

你剛剛寫了第一條路由。三行函式加一個裝飾器，這就是後端最小的形狀。

## 二、path 是鍵，不是裝飾

把 `@app.get("/notes")` 改名成 `"/todos"`，然後：

```bash
curl -i http://127.0.0.1:8000/notes
curl -i http://127.0.0.1:8000/todos
```

**改完要改回來。**

## 三、你的路由怎麼被擋掉

```bash
curl -i 'http://127.0.0.1:8000/notes/abc'
curl -i -X POST http://127.0.0.1:8000/notes
```

第一個回 `422`，`loc` 指向 `note_id`。這次的路由有沒有被查到？第二個回 `405` 加上 `allow: GET`。

## 四、預測別人的路由

先寫下預測再送出。任選五組：

| 候選組合 | 你的預測 Status Code | 你的預測 Body |
| --- | --- | --- |
| `GET /users/alice` | | |
| `GET /users/ghost` | | |
| `GET /nowhere` | | |
| `DELETE /users/alice` | | |
| `PUT /users/alice` | | |
| `GET /users` | | |
| `POST /users`（合法 JSON） | | |

```bash
curl -i http://127.0.0.1:8000/users/alice
curl -i http://127.0.0.1:8000/users/ghost
curl -i http://127.0.0.1:8000/nowhere
curl -i -X DELETE http://127.0.0.1:8000/users/alice
curl -i http://127.0.0.1:8000/users
```

`/users/ghost` 與 `/nowhere` 都是 `404`，但 Body 的 `detail` 不一樣。寫出「是誰寫的」。

## 五、把 `/health` 改壞一次

```bash
# 先改壞
curl -i http://127.0.0.1:8000/health

python -c "
import urllib.request, json
r = urllib.request.urlopen('http://127.0.0.1:8000/health')
print('status ok:', r.status == 200)
print('body ok  :', json.load(r).get('ok') is True)
"
```

要看見 `status ok: True` 配上 `body ok: False`。**改完立刻改回 `{"ok": True}`。**

```bash
cd examples/http-api
python -m pytest tests/test_main.py -q
```

那個改動會讓哪一條斷言失敗？寫下來。

```bash
curl -f http://127.0.0.1:8000/health; echo "exit=$?"
curl -f http://127.0.0.1:8000/healthz; echo "exit=$?"
curl -I http://127.0.0.1:8000/health
```

## 繳交

1. 你新增的兩條路由程式碼截圖，加上 `curl -i /notes` 的 `200`。
2. `/notes` 與 `/todos` 並排截圖，證明 path 是鍵。
3. `/notes/abc` 的 `422` 與 `POST /notes` 的 `405` 截圖，回答路由有沒有被查到。
4. 五組預測的截圖；不符的組別加附 Terminal 1 的 access log。
5. `{"ok":"yes"}` 版本的三張截圖，以及改回來之後的截圖。
6. `pytest` 截圖，全數通過。寫出第五步為什麼會被擋下來。
7. `curl -f` 兩次的 exit status，加上 `curl -I` 的 `405` 與 `allow: GET`。
8. 一句話：為什麼 `/health` 不應該檢查資料庫？寫成「重啟之後會發生什麼」。
9. `git status` 截圖，確認 `main.py` 已改回 `{"ok": True}` 且路由已改回 `/notes`。