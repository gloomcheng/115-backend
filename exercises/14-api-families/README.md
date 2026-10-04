# 14 — API 家族：SOAP、REST、GraphQL、gRPC、tRPC 怎麼讀

五個家族都在回答同一個問題：怎麼把型別與錯誤交給 Client。差別在契約放在哪裡。

## 啟動

```bash
# Terminal 1
cd exercises/14-api-families
fastapi dev main.py --port 8007
```

這支 API 同時提供 REST 和 GraphQL，資料是 `welcome` 和 `api` 兩筆筆記。

## 一、REST 給的欄位由 Server 決定

```bash
curl -s http://127.0.0.1:8007/notes
```

`tags` 出現在裡面，即使你根本不需要。**回應形狀由 Server 決定** — 這叫 over-fetching。

## 二、GraphQL 的回應形狀由你決定

```bash
curl -s -X POST http://127.0.0.1:8007/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ notes { name title } }"}'
```

`tags` 不見了。

## 三、問一個不存在的欄位

```bash
curl -i -X POST http://127.0.0.1:8007/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ notes { name nickname } }"}'
```

三件事：訊息指名欄位並建議 `Did you mean 'name'?`、`data` 是 `null`、**狀態碼是 `200`**。

串接別人的 GraphQL 時，`curl -f` 沒用，要檢查 Body 裡有沒有 `errors`。

## 四、同一個錯誤，REST 的答案

```bash
curl -i -X POST http://127.0.0.1:8007/notes \
  -H 'Content-Type: application/json' \
  -d '{"name":"t1","title":"T","is_admin":true,"colour":"red"}'
```

`200`，`is_admin` 和 `colour` 被安靜丟掉。**REST 對「多」的錯誤完全沉默。**

## 五、找不到資源

```bash
curl -i http://127.0.0.1:8007/notes/ghost      # 404 Note not found
curl -i http://127.0.0.1:8007/nothing-here    # 404 Not Found
curl -s -X POST http://127.0.0.1:8007/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ note(name: \"ghost\") { name } }"}'   # {"data":{"note":null}}
```

GraphQL 的 `null` **沒有 `errors`**。因為 schema 寫的是 `note(...): Note` 而不是 `Note!`。改成 `Note!` 之後，爆炸半徑會從一個欄位變成整個查詢。

## 六、三個數字

```bash
curl -s http://127.0.0.1:8007/notes | wc -c                                    # 161
curl -s -X POST http://127.0.0.1:8007/graphql -H 'Content-Type: application/json' \
  -d '{"query":"{ notes { name title } }"}' | wc -c                            # 119
curl -s -X POST http://127.0.0.1:8007/graphql -H 'Content-Type: application/json' \
  -d '{"query":"{ notes { name title tags } }"}' | wc -c                       # 170
```

省下 42 個位元組，毫無意義。重點是**誰決定回應形狀**。

## 七、WebSocket：不用任何函式庫

```bash
python websocket_demo.py key      # 握手裡那一行數學
python websocket_demo.py frame    # 一則訊息在線上長什麼樣
python websocket_demo.py serve    # 純 socket 的 Server，8014
python websocket_demo.py client   # 手動講協定的 Client
```

前兩個模式直接印，不需要開任何東西。`serve` 和 `client` 要分兩個 Terminal。

握手會回：

```
HTTP/1.1 101 Switching Protocols
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**這個值裡沒有密碼。**它證明的是「對方看得懂 HTTP」，不是「對方是誰」。權限要自己在第一則訊息裡帶。

最值得看的是 frame：Server 送 `81 05 68 65 6c 6c 6f`，Client 送 `81 82 01 02 03 04 69 6b`。**payload 都可以是文字，但第二個位元組差了一個 mask bit。**

## 契約檔（讀，不跑）

- `notes.proto` — gRPC 的契約
- `trpc-contract.ts` — tRPC 的契約

這兩個檔案在這一課**不執行**。gRPC 走 Protobuf 二進位編碼跑在 HTTP/2 上；tRPC 走 JSON 但要求 Client 和 Server 在同一個 TypeScript 專案。

## 繳交

1. `GET /notes`（含 `tags`）+ GraphQL 只要 `name title`（無 `tags`）。回應形狀分別由誰決定？
2. 三個 `wc -c` 數字 + 42 個位元組在實務上什麼時候會變成幾百 KB？
3. 查 `nickname` 的完整截圖（`200 OK`、`data` 為 `null`、`Did you mean`）+ 為什麼不用 `4xx`？
4. 送多餘欄位的 REST 截圖（`200`、Body 沒有 `is_admin`）+ 和第 3 步並排 + `extra="forbid"` 在這裡會發生什麼事？
5. `GET /notes/ghost`（`404 Note not found`）與 GraphQL `null`（無 `errors`）+ schema 改成 `Note!` 之後結果會變成什麼？
6. `GET /nothing-here`（`404 Not Found`）+ 和第 5 步第一張並排，兩個 `404` 語意差在哪、Client 該如何分辨？
7. `notes.proto` 和 `trpc-contract.ts` 各寫一句：為什麼這一課不執行它們？哪一個是原始碼、哪一個是產生物？
8. SOAP 的 WSDL 和 gRPC 的 `.proto` 都能產生 stub，差別在哪？tRPC 放棄了什麼、換來了什麼？

## 繳交前

`main.py`、`notes.proto`、`trpc-contract.ts` 都是教材，不要修改。
