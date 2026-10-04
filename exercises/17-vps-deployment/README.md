# 17 — 把 VPS 變成公開服務

交付的不是「網頁打得開」這句話，而是 Request 通過每一關的證據。

## Pipeline 是什麼（不需要 VPS）

這支程式**不需要**任何 VPS、任何憑證，也不需要安裝套件：

```bash
python pipeline_demo.py gate    # 為什麼「門禁」不等於「會顯示紅字」
python pipeline_demo.py env     # 同一段程式碼，兩種環境，兩種結果
python pipeline_demo.py steps   # pipeline 的四個部分
```

`env` 那一段是本單元最重要的連結：

```bash
env -u SIGNING_KEY python pipeline_demo.py env   # RuntimeError
SIGNING_KEY=demo python pipeline_demo.py env     # App started
```

**你的電腦有這個變數，所以你看不見這個錯誤。**CI 是一台沒有你的 shell 設定的機器，那才是它存在的理由。

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
