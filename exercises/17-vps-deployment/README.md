# 17 — 把 VPS 變成公開服務

交付的不是「網頁打得開」這句話，而是 Request 通過每一關的證據。

## 驗收環境

- Ubuntu 24.04 或 26.04 LTS VPS
- 一個 DNS `A` record
- FastAPI container 綁定 `127.0.0.1:8000`
- Nginx 提供 `80/443`
- Certbot 管理 TLS 憑證

## 收集證據

在開發電腦執行：

```bash
bun run setup:hooks
bun run test:api
bun run test:security
bun run security:scan
bun run check:deployment
```

在 VPS 執行：

```bash
sudo ufw status numbered
sudo ss -ltnp
sudo nginx -t
sudo docker compose ps
sudo certbot renew --dry-run
```

在另一台電腦執行：

```bash
dig +short A "$DOMAIN"
curl -I "http://$DOMAIN/health"
curl -v "https://$DOMAIN/health"
curl -sS "https://$DOMAIN/request-info"
bun run check:deployment -- --url="https://$DOMAIN" --expected-ip="$SERVER_IP"
```

## 通過條件

- DNS 查詢結果是 VPS public IP。
- `8000` 只綁定 `127.0.0.1`，防火牆也沒有公開 `8000`。
- HTTP 轉向 HTTPS。
- HTTPS 回 `200`，憑證驗證沒有錯誤。
- `/request-info` 的 `scheme` 是 `https`，`host` 是你的網域。
- Certbot 測試更新通過。
- API tests、secret scan、deployment contract 與 live deployment harness 全部回傳 exit status `0`。
- Repository 沒有追蹤 `.env`、private key、password、API key 或 Token。

截圖要同時保留執行的指令與輸出。遮住公司 IP、SSH 使用者名稱、email、Token 與密鑰。
