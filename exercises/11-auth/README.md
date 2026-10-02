# 11 — 登入：身份認證與 JWT

401 問「你是誰」，403 問「你能不能做」。這堂課要把兩者分開，並且看懂 JWT 到底是不是加密的。

```bash
# Terminal 1
cd exercises/11-auth
fastapi dev main.py --port 8004
```

## 一、把 token 存起來

```bash
# Terminal 2
export TOKEN=$(curl -s -X POST http://127.0.0.1:8004/login \
  -H 'Content-Type: application/json' \
  -d '{"name":"iris","password":"lesson"}' \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

echo "$TOKEN"
```

數一下三段，分別是什麼？

## 二、沒有金鑰也能讀

```bash
python -c "
import base64, json, sys
p = sys.argv[1].split('.')[1]
print(json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p) % 4))))
" "$TOKEN"
```

`role`、`iat`、`exp` 全都看得見，而這個指令沒有用到任何金鑰。**JWT 的 payload 有加密嗎？**

## 三、改一個欄位試試

```bash
python - > /tmp/tampered.txt <<'PY'
import base64, json, os

head, payload, sig = os.environ["TOKEN"].split(".")
data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
data["role"] = "admin"
tampered_payload = (
    base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode())
    .rstrip(b"=")
    .decode()
)
print(f"{head}.{tampered_payload}.{sig}")
PY

curl -i http://127.0.0.1:8004/admin -H "Authorization: Bearer $(cat /tmp/tampered.txt)"
```

`401` 加 `Bad signature`。Server 是用什麼方法發現被改過的？

## 四、401 與 403 的 Header 差異

```bash
curl -i http://127.0.0.1:8004/private

curl -i http://127.0.0.1:8004/admin -H "Authorization: Bearer $TOKEN"

curl -i http://127.0.0.1:8004/private -H "Authorization: Bearer $TOKEN"
```

第一個 `401` 帶 `WWW-Authenticate`，第二個 `403` 不帶，第三個 `200`。把三個 Header 差異寫下來。

## 五、過期的 token

```bash
EXPIRED=$(curl -s -X POST http://127.0.0.1:8004/login-expired \
  -H 'Content-Type: application/json' -d '{"name":"iris"}' \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

curl -i http://127.0.0.1:8004/private -H "Authorization: Bearer $EXPIRED"
```

`401` 加 `Token expired`。簽名有效和 token 還能用，是同一件事嗎？

## 繳交

1. 完整三段 token 的截圖 + 三段分別是什麼。
2. 解出 payload 的截圖（要含 `role`／`iat`／`exp`）+ JWT 有沒有加密。
3. 沒有 token 的 `401` 截圖，**必須含 `WWW-Authenticate`**。
4. 改過 role 之後的 `401 Bad signature` 截圖 + Server 怎麼發現的。
5. 學生 token 打 `/admin` 的 `403` 截圖 + 和第 3 步的 Header 差異。
6. 過期 token 的 `401 Token expired` 截圖 + 簽名有效 ≠ 還能用。
7. 一句話：`401` 與 `403` 各自在問什麼？寫成「誰該去修什麼」。
8. 如果把 `{"user_id": 7, "is_admin": true}` 放進 payload，`is_admin` 會怎樣？這和第 10 課最後那個未宣告欄位是同一個問題嗎？

## 繳交前

`main.py` 裡的 `SECRET` 只是課堂練習用的字串，不是真的機密。不要把它換成你在用的任何密鑰，也不要 commit 任何真實憑證。