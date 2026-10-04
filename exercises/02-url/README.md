# 02 — URI / URL、Header 與 Body

先不要看框架。用 `curl -v` 找出 URL 哪些部分真的進了 Request。

```bash
curl -v 'https://httpbin.org/get?course=115&topic=uri#fragment'
```

## 檔案上傳：Body 的第四種形狀

前四個模式**不需要安裝任何東西**，可以直接跑：

```bash
python multipart_demo.py show      # 原始 body 長什麼樣
python multipart_demo.py boundary  # 為什麼 JSON 不需要、檔案需要
python multipart_demo.py parse     # 不用框架解析一次
python multipart_demo.py filename  # 唯一絕對不能相信的欄位
```

要看真的在線上跑的樣子：

```bash
printf 'line one\nline two\n' > /tmp/a.txt
python multipart_demo.py serve
```

```bash
curl -s -F "note=hello" -F "file=@/tmp/a.txt" http://127.0.0.1:8011/raw
curl -s -F "note=hello" -F "file=@/tmp/a.txt" http://127.0.0.1:8011/upload
```

兩條路由打的是同一份表單，回來的不一樣。`/raw` 宣告了什麼都沒有，所以框架不動 body，你看得見原始 bytes；`/upload` 宣告了 `Form`，框架就自己讀走並解析。

**在 `/upload` 裡再呼叫 `await request.body()` 會得到 `RuntimeError: Stream consumed`。**要除錯就用 `/raw` 那條路徑。

## 作業

1. 在 `> GET` 的 Request Line 標出 `path` 與 `query`。
2. 在 `> Host` Header 標出 `host`。
3. 在你輸入的完整 URL 上標出 `scheme` 與 `fragment`。
4. 說明為什麼 `fragment` 沒有出現在送給 Server 的 Request Target。

再執行一次：

```bash
curl -i -X POST 'https://httpbin.org/anything/users' \
  -H 'Content-Type: application/json' \
  -d '{"name":"alice"}'
```

在輸出中分別標出 Header 與 Body。截圖要同時保留執行的指令、`> Request` 與 `< Response`。
