# 08 — CRUD

五個 method，五條 SQL。每一列的 Status Code 都是那條 SQL 執行完的結果，不是你挑的。

```bash
# Terminal 1
cd exercises/08-crud
rm -f users.db
fastapi dev main.py --port 8002
```

## 一、空集合和查不到，是兩件事

```bash
curl -i http://127.0.0.1:8002/users
```

回 `200` 加 `[]`。**路由存在，資料真的沒有。** 對照 `curl -i http://127.0.0.1:8002/users/iris` 會回 `404`——那是「這個東西不存在」。

## 二、建立兩次

```bash
curl -i -X POST http://127.0.0.1:8002/users \
  -H 'Content-Type: application/json' -d '{"name":"iris","role":"student"}'

curl -i -X POST http://127.0.0.1:8002/users \
  -H 'Content-Type: application/json' -d '{"name":"iris"}'
```

第一個 `201`，第二個 **`409`**。Request 本身完全合法，問題是那筆已經在那裡。

```bash
sqlite3 users.db ".schema users"
```

`name TEXT PRIMARY KEY NOT NULL` — 這個規則住在檔案裡。`409` 是 SQLite 丟出來的，不是 Python 檢查的。

## 三、成員與集合

```bash
curl -s http://127.0.0.1:8002/users/iris
curl -s http://127.0.0.1:8002/users
```

一個物件、一個陣列。差別在 path 有沒有帶 `{name}`。

## 四、PUT 與 PATCH

```bash
curl -s -X PUT http://127.0.0.1:8002/users/iris \
  -H 'Content-Type: application/json' -d '{"name":"iris","role":"ta"}'

curl -s -X PATCH http://127.0.0.1:8002/users/iris \
  -H 'Content-Type: application/json' -d '{"role":"student"}'
```

**再試一次 PUT，這次省略 `role`：**

```bash
curl -s -X PUT http://127.0.0.1:8002/users/iris \
  -H 'Content-Type: application/json' -d '{"name":"iris"}'

sqlite3 users.db "SELECT name, role FROM users;"
```

`role` 變成什麼了？這就是 `PUT` 與 `PATCH` 最重要的差別。

## 五、刪兩次，再讀

```bash
curl -i -X DELETE http://127.0.0.1:8002/users/iris
curl -i -X DELETE http://127.0.0.1:8002/users/iris
curl -i http://127.0.0.1:8002/users/iris
sqlite3 users.db "SELECT COUNT(*) FROM users;"
```

兩個 `204`、一個 `404`、`0`。**`204` 是「我沒 Body 給你」，不是「我沒做事」。**

## 六、集合路徑的 allow 變了

```bash
curl -s -o /dev/null -w 'GET /users -> %{http_code}\n' http://127.0.0.1:8002/users
curl -i -X PUT http://127.0.0.1:8002/users -H 'Content-Type: application/json' -d '{"name":"x"}'
```

`405` 加上 `allow: GET, POST`。第 06 課時這裡只有 `allow: POST`。

## 七、欄位名不能綁參數，所以要自己擋

`injection.py` 不需要啟動 Server，直接跑：

```bash
python injection.py value       # ' OR '1'='1 讀出整張表
python injection.py delete      # 同一個錯誤，但資料沒了
python injection.py identifier  # 欄位名沒有 ? 可以用
```

`delete` 那段會印出 `deleted 2, 0 left`：**一個請求刪掉兩列，Server 回的是乾淨的 `204`。**

## 八、拿掉白名單，看它怎麼壞

停掉 Server，把 `main.py` 裡的 `if key in {"name", "role"}` 改成 `if isinstance(key, str)`，重啟：

```bash
curl -i -X PATCH http://127.0.0.1:8002/users/iris \
  -H 'Content-Type: application/json' \
  -d '{"role = '"'"'admin'"'"', name":"x"}'

sqlite3 users.db "SELECT name, role FROM users;"
```

回 `500`，但 `iris` 變成 `admin`。**做完記得改回去。**

## 繳交

1. `.schema users` 的截圖。回答：`409` 是 Python 的檢查還是 SQLite 的規則？
2. 兩個 `201` 加一個 `409` 的截圖（含完整 Body）。
3. 成員與集合並排截圖，回答為什麼一個是物件、一個是陣列。
4. `PUT` 與 `PATCH` 各一次的截圖，加上資料庫裡的結果。兩條 SQL 的差別在哪？
5. 省略 `role` 的 `PUT` 截圖。`role` 變成什麼？
6. 兩個 `204` 加一個 `404` 加 `COUNT(*)` 的截圖。
7. `PUT /users` 的 `405` 與 `allow` 截圖。和第 06 課那個相比，多了什麼？
8. 完成第 06 節的對照表，「目標不存在時」那一欄全部填滿。`DELETE` 那格是本課的選擇，不是唯一答案——寫出你的理由。
9. `python injection.py value` 的截圖，要同時看得到 `WHERE name = '' OR '1'='1'` 和回傳兩筆。
10. `python injection.py delete` 的截圖，含 `deleted 2, 0 left`。Server 回什麼狀態碼？Client 有辦法知道被刪了兩列嗎？
11. `python injection.py identifier` 的截圖，含 `You can only execute one statement at a time.` 和 `ORDER BY 1`。哪一段傷害比較大？
12. 第八步的 `500` 與 `sqlite3` 輸出截圖。回答：只看得到 `500`，你怎麼判斷攻擊有沒有成功？
13. `grep -n 'f"' main.py` 的輸出。列出每一處接進 SQL 的地方，寫下每一處靠什麼維持安全。

## 繳交前

`users.db` 與 `injection.db` 是練習產生的檔案，**不要 commit 進去**。`git status` 應該看不到它。