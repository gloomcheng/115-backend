# 05 — 寫出第一個 GET /health

這一課的作業是**故意把服務弄壞一次**，看程式會不會發現。

```bash
# Terminal 1
cd 115-backend
source venv/bin/activate
fastapi dev examples/http-api/main.py
```

## 一、人看不出來，程式看得出來

把 `main.py` 裡的 `health()` 改成 `return {"ok": "yes"}`，存檔等重載，然後：

```bash
# Terminal 2
curl -i http://127.0.0.1:8000/health

python -c "
import urllib.request, json
r = urllib.request.urlopen('http://127.0.0.1:8000/health')
body = json.load(r)
print('status ok:', r.status == 200)
print('body ok  :', body.get('ok') is True)
"
```

`curl` 看到 `200`，探測程式看到 `body ok: False`。**截完立刻改回 `{"ok": True}`。**

## 二、測試會擋下來

```bash
cd examples/http-api
python -m pytest tests/test_main.py -q
```

第 1 步那個改動會讓哪一條斷言失敗？寫下來。

## 三、三種失敗的表達方式

```bash
curl -f http://127.0.0.1:8000/health;  echo "exit=$?"
curl -f http://127.0.0.1:8000/healthz; echo "exit=$?"
curl -I http://127.0.0.1:8000/health
```

第一條成功、第二條 exit 22、第三條 `405` 加 `allow: GET`。

## 四、它有多快

```bash
for i in $(seq 10); do
  curl -s -o /dev/null -w '%{time_total}\n' http://127.0.0.1:8000/health
done | sort -n | tail -3
```

最慢一次大約 `0.08s`。`compose.yaml` 的 `timeout: 3s` 跟這個數字有什麼關係？

## 繳交

1. `{"ok":"yes"}` 版本的 `curl -i` 與探測程式截圖，要同時看得到 `200` 和 `body ok: False`。加上改回 `{"ok": True}` 之後的截圖。
2. `pytest` 截圖，全數通過。寫出第 1 步為什麼會被擋下來。
3. `curl -f` 兩次的 exit status 截圖，加上 `curl -I` 的 `405` 與 `allow: GET`。
4. 十次量測中最慢一次的秒數截圖。
5. 一句話：為什麼 `/health` 不應該檢查資料庫？寫成「重啟之後會發生什麼」。
6. `git status` 截圖，確認 `main.py` 已經改回 `{"ok": True}`。