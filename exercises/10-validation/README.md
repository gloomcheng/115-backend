# 10 — 驗證與錯誤

同一份 Body，送進兩條路由，得到兩個答案。整堂課就在比較這件事。

```bash
# Terminal 1
cd exercises/10-validation
fastapi dev main.py --port 8003
```

## 一、一份 Body，兩個答案

```bash
curl -i -X POST http://127.0.0.1:8003/strict \
  -H 'Content-Type: application/json' -d '{"name":123}'

curl -i -X POST http://127.0.0.1:8003/loose \
  -H 'Content-Type: application/json' -d '{"name":123}'
```

**一個 `422`，一個 `500`。Body 逐字相同。** 接著回 Terminal 1 看 `loose` 那條的 traceback，Client 永遠看不到那一行。

## 二、形狀的四種錯法

```bash
curl -s -X POST http://127.0.0.1:8003/strict \
  -H 'Content-Type: application/json' -d '{"role":"student"}'

curl -s -X POST http://127.0.0.1:8003/strict \
  -H 'Content-Type: application/json' -d '{"name":123}'

curl -s -X POST http://127.0.0.1:8003/strict \
  -H 'Content-Type: application/json' -d '{"name":""}'

curl -s -X POST http://127.0.0.1:8003/strict \
  -H 'Content-Type: application/json' -d '{"name":"xxxxx...45"}'
```

整理一張表：`type` 值、錯在 Body 的哪裡、Client 該做什麼。

## 三、loc 會指進陣列

```bash
curl -s -X POST http://127.0.0.1:8003/post-strict \
  -H 'Content-Type: application/json' \
  -d '{"title":"week 8","tags":[{"label":"a","weight":1},{"label":"b","weight":"heavy"}]}'
```

`loc` 要逐字等於 `["body","tags",1,"weight"]`。中間那個 `1` 是什麼？

## 四、Body 本身壞掉

```bash
curl -s -X POST http://127.0.0.1:8003/strict \
  -H 'Content-Type: application/json' -d '[1,2,3]'

curl -s -X POST http://127.0.0.1:8003/strict \
  -H 'Content-Type: application/json' -d '{"name":'

curl -s -X POST http://127.0.0.1:8003/strict -H 'Content-Type: application/json'
```

第二個的 `loc` 最後一個成員是數字還是字串？這兩種 `loc` 差在哪？

## 五、沒有人擋的欄位

```bash
curl -s -X POST http://127.0.0.1:8003/strict \
  -H 'Content-Type: application/json' -d '{"name":"iris","admin":true}'
```

沒有 `422`，沒有 `409`。`admin` 去哪裡了？形狀沒擋（沒宣告就忽略），規則也沒擋（根本沒人問）。

## 危險字串 vs 危險輸出

```bash
python xss_server.py --check     # 不用瀏覽器，先看 HTML 長什麼樣
python xss_server.py             # 起在 8009，用瀏覽器看真的會不會執行
```

瀏覽器打開 `http://127.0.0.1:8009/raw?name=<script>alert(1)</script>`，alert 會跳出來。換成 `/escaped`，畫面上出現的是字面的那幾個字。

最值得看的是 `/naive-attr`：它**有**跳脫尖括號，輸出裡一個 `<` 都沒有，但注入一樣成功——因為它沒跳脫引號。

## 繳交

1. 第一節兩份並排截圖 + Terminal 1 的 traceback。
2. 第二節四個 `422` 的完整 Body + 你整理的那張表。
3. 第三節的 `loc` 截圖 + 一句話解釋索引 `1`。
4. 第四節三個 `detail` 截圖 + 兩種 `loc` 形狀的差異。
5. 第五節的 `admin` 截圖 + 一句話：兩種驗證都沒擋，這說明什麼？
6. 一句話：判斷該回 `422` 還是 `409`，你的標準是什麼？用「改完資料重送一次會不會成功」回答。
7. 在你自己的 `main.py` 加一條 route，用 Pydantic 宣告 `name` 與 `role`，送一份壞資料截圖（要含 `422` 與 `loc`），再用一行 diff 說明型別宣告放在哪裡。