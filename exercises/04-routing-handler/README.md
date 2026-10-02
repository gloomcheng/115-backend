# 04 — 路由與 Handler

**先寫預測，再送出。** 路由表是資料，所以任何 `(method, path)` 的結果都能事先算出來。

## 一、四個出口各跑一次

```bash
# 出口 1：命中並執行
curl -i http://127.0.0.1:8000/users/alice
# 出口 3：路由表裡沒有這條
curl -i http://127.0.0.1:8000/nowhere
# 出口 2：method 沒登記
curl -i -X DELETE http://127.0.0.1:8000/users/alice
curl -i http://127.0.0.1:8000/users
# 出口 4：Body 在比對路由之前就壞掉
curl -i -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' \
  -d '{"name": "bob"'
```

## 二、兩個 404 並排

```bash
curl -i http://127.0.0.1:8000/users/ghost
curl -i http://127.0.0.1:8000/nowhere
```

| 路徑 | Status Code | Body 的 `detail` | 是誰寫的 |
| --- | --- | --- | --- |
| `/users/ghost` | | | |
| `/nowhere` | | | |

## 三、兩個 405 並排

```bash
curl -i -X DELETE http://127.0.0.1:8000/users/alice
curl -i http://127.0.0.1:8000/users
```

兩次的 `allow` 各是什麼？為什麼會不同？

## 繳交

1. 五張截圖，每張都要有 Request Line、Status Line 與完整 Body。
2. 預測與實際不符的組別，額外截 Terminal 1 的 access log。
3. 一句話：兩個 `404` 為什麼 Body 的 `detail` 不一樣？寫出「是誰寫的」。
4. 一句話：這次的 `POST`（Body 壞掉）有沒有查到路由？證據在哪裡？