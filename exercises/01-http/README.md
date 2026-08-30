# 01 — HTTP 方法與狀態碼

用 `curl` 看，不要用猜的。

```bash
# 綠色
curl -i https://httpbin.org/status/200

# 紅色 — 這不是成功
curl -i https://httpbin.org/status/404

# 黃色 — 看 Location
curl -i https://httpbin.org/status/301

```

作業：截圖 `200`、`404`、`301` 三次回應的 Status Line，並在 `301` 截圖中標出 `Location`，放到這個資料夾。

提示：`404` 要當失敗處理，不要當成 `200` 空陣列。
