# 02 — URI / URL、Header 與 Body

先不要看框架。用 `curl -v` 找出 URL 哪些部分真的進了 Request。

```bash
curl -v 'https://httpbin.org/get?course=115&topic=uri#fragment'
```

作業：

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
