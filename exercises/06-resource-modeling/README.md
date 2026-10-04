# 06 — 資源建模與 REST：集合、成員與 201

先啟動練習 API（Terminal 1），另一個 Terminal 送指令（Terminal 2）。

```bash
# Terminal 1
cd 115-backend
source venv/bin/activate
fastapi dev examples/http-api/main.py
```

## 一、建立之後讀得到

```bash
# Terminal 2
curl -i -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"s112306001","role":"student"}'

curl -i http://127.0.0.1:8000/users/s112306001
```

截圖要同時包含 `201` Status Line 與 `200` Status Line。請用英文小寫當 `name`：中文要百分比編碼才放得進 path。

## 二、method 決定 Server 做什麼

```bash
curl -i -X DELETE http://127.0.0.1:8000/users/s112306001
curl -i http://127.0.0.1:8000/users
```

兩次都是 `405`，而且帶 `allow` Header。截圖要能讀到 `allow: GET` 與 `allow: POST`。

## 三、動作寫進網址的下場

```bash
curl -i 'http://127.0.0.1:8000/users/delete?id=s112306001'
```

回 `404` 與 `{"detail":"User not found"}`。`delete` 被當成一個 username。

## 四、讀三次，建立兩次

```bash
for i in 1 2 3; do curl -s http://127.0.0.1:8000/users/alice; echo; done

curl -s -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' -d '{"name":"carol","role":"student"}'
curl -s -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' -d '{"name":"carol","role":"ta"}'
curl -s http://127.0.0.1:8000/users/carol
```

讀三次要三行完全相同。POST 兩次都是 `201`，但最後只剩一份 `carol`，而且是第二次那份。

## 五、N+1：數語句，不要數時間

```bash
python n_plus_one.py small     # 20 個作者，21 條語句，結果完全相同
python n_plus_one.py scale     # 500 個作者 → 501 條
python n_plus_one.py indexed   # 加了索引，還是 501 條
python n_plus_one.py latency   # 本機時間為什麼不算數
```

`small` 最後那行是重點：

```
identical result: True
```

**同一份資料，一種問 21 次，一種問 1 次。**

`latency` 那一段要特別注意：`ms local` 是本機真的量到的那個很小的數字，**它證明不了任何事**；`if each cost 1 ms` 是明確標示出來的模擬。

## 繳交

1. 四組截圖，每組都要看得到指令本身與 `<` 開頭的 Response。
2. 一句話回答：為什麼 `GET /users` 現在回 `405`，而不是回一個空的 users 清單？
3. 指出上面五個結果各是 `4xx` 還是 `5xx`，責任在 Client 還是 Server。