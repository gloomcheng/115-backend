# 12 — 中介軟體、權限與密鑰邊界

這一課的主詞是一個位置：中介軟體在路由比對之前執行。它看得到這是一個 Request，看不到這要做什麼。

## 啟動

簽發金鑰從環境變數拿，所以啟動方式和前面幾課不同。

```bash
# Terminal 1
cd exercises/12-middleware
SIGNING_KEY=lesson-12-key-a fastapi dev main.py --port 8005
```

沒有 `SIGNING_KEY` 就會拒絕啟動：

```bash
$ python -c "import main"
RuntimeError: SIGNING_KEY is not set. A signing key belongs in the
environment; hardcoding one here would put it in version control.
```

## 一、沒有路由的請求也會經過中介軟體

```bash
curl -i http://127.0.0.1:8005/nope
```

`404`，但 `x-trace` 與 `x-request-id` 都在。**中介軟體有沒有執行，看那兩個 Header 就知道。**

## 二、巢狀順序

```bash
curl -i http://127.0.0.1:8005/open | rg -i '^x-trace'
```

把 `outer:in > inner:in > inner:out > outer:out` 抄下來。

## 三、把兩個中介軟體對調，看它壞掉

把 `main.py` 裡 `trace_inner` 與 `trace_outer` 兩個 block 上下互換，等重新載入後：

```bash
curl -i http://127.0.0.1:8005/open
```

Terminal 1 出現 `AttributeError: 'State' object has no attribute 'trace'`，curl 拿到 `500`。**截圖要兩邊都有**：路由是好的，壞掉的是中介軟體，而外面只看得到 `500`。

最後註冊的那個在最外面，也就是每個 Request 最先跑的那一層。對調之後 `trace_inner` 變最外層，於是它在 `request.state.trace` 建立起來之前就去讀它。

做完記得還原。

## 四、token 裡寫錯的 role 沒有用

```bash
# Terminal 2
export STUDENT=$(curl -s -X POST http://127.0.0.1:8005/login \
  -H 'Content-Type: application/json' \
  -d '{"name":"iris","password":"lesson"}' \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

export ADMIN=$(curl -s -X POST http://127.0.0.1:8005/login \
  -H 'Content-Type: application/json' \
  -d '{"name":"root","password":"lesson"}' \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

python3 -c "
import base64, json, sys
p = sys.argv[1].split('.')[1]
print(json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p) % 4))))
" "$ADMIN"
```

輸出會是 `{'sub': 'root', 'role': 'intern', ...}` — **role 這個欄位是故意寫錯的。**

```bash
curl -i http://127.0.0.1:8005/admin -H "Authorization: Bearer $ADMIN"
```

`200`，因為 `require_admin` 拿 `sub` 去 Server 自己的表查，沒有用 token 裡的 role。

```bash
curl -i http://127.0.0.1:8005/admin -H "Authorization: Bearer $STUDENT"
```

同一條路徑，學生的 token 是 `403`。兩張截圖並排，唯一的差別只有 `$ADMIN` 跟 `$STUDENT`。

## 五、未宣告欄位被指名

```bash
curl -i -X POST http://127.0.0.1:8005/profile \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $STUDENT" \
  -d '{"nickname":"iris","is_admin":true}'
```

`422`，`type` 是 `extra_forbidden`，`loc` 是 `["body","is_admin"]`。

單元 10 的同一個 `admin` 欄位是被安靜丟掉的。這裡是拒絕，並且指名。差別在於 Client 會不會知道。

## 六、哪一把金鑰在跑

```bash
curl -s http://127.0.0.1:8005/key-info
```

回應是指紋，不是金鑰。金鑰永遠不該被印出來。

## 七、換一把金鑰，全部作廢

```bash
# Terminal 3
cd exercises/12-middleware
SIGNING_KEY=lesson-12-key-b fastapi dev main.py --port 8006
```

比較兩邊的指紋，然後把 Terminal 2 的 token 送到 8006：

```bash
curl -s http://127.0.0.1:8005/key-info
curl -s http://127.0.0.1:8006/key-info

curl -i http://127.0.0.1:8006/profile -H "Authorization: Bearer $STUDENT"
```

`401` `Bad signature`。同一枚 token 在 8005 還能用，在 8006 不能。

**換金鑰會讓所有已發出的 token 同時失效**，不是只有一枚。Server 不需要保存任何狀態，代價是每個人都被迫重新登入。

## 速率限制

`main.py` 已經有一個限流中介軟體了。`rate_limit.py` 則把三種演算法並排跑給你看：

```bash
python rate_limit.py baseline   # 沒有限流會怎樣
python rate_limit.py fixed      # 固定視窗，以及它在視窗邊界的破口
python rate_limit.py sliding    # 滑動視窗，同樣 10 個請求只准 5 個
python rate_limit.py bucket     # token bucket，允許爆量
python rate_limit.py headers    # 429 與 Retry-After
```

用真的 Server 試：

```bash
for i in $(seq 1 31); do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8005/open; done | sort | uniq -c
```

**`30 200` 加 `1 429`。**接著打一個不存在的路徑 `curl -i http://127.0.0.1:8005/nope`，它也會是 `429`——因為中介軟體在路由比對之前就跑了。

## 繳交

1. 不存在路徑的 `404` 截圖，**必須含 `x-request-id` 與 `x-trace`** + 中介軟體有沒有真的執行。
2. 對調後的 `AttributeError` 與 `500` **兩張截圖** + 為什麼壞掉的是外面那個。
3. `'role': 'intern'` 的截圖，加上用它打 `/admin` 的 `200` 截圖 + 這個欄位被誰忽略了。
4. 學生的 token 打 `/admin` 的 `403` 截圖 + 和第 3 步並排，只差哪一個欄位。
5. `422` `extra_forbidden` 與 `["body","is_admin"]` 截圖 + 和單元 10 的預設行為差在哪。
6. 沒有 `SIGNING_KEY` 的 `RuntimeError` 完整訊息截圖 + 為什麼拒絕啟動而不是用預設值。
7. 兩個 `/key-info` 的**不同指紋** + `8006` 的 `401 Bad signature` 截圖 + 換金鑰讓誰失效。
8. `exp` 兩小時、使用者被開除一小時，他的 token 還能用多久？用這一堂課的兩個機制回答。

## 繳交前

`SIGNING_KEY` 是給練習用的字串，不要把它換成你在用的任何金鑰，也不要把真實憑證寫進 `main.py`、`.env` 或任何會被提交的檔案。真實的簽發金鑰由部署環境提供。
