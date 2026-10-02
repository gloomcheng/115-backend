# 16 — 用 Docker 包起來

容器不是一個比較小的電腦，它是一個自己的 `127.0.0.1`。這個差別決定了健康檢查該寫哪個位址、log 裡會出現誰的 IP。

## 建 image

```bash
# Terminal 1
cd examples/http-api
docker build --target base -t lesson16-base .
```

第一次 build 會花幾分鐘下載套件。跑完之後：

```bash
# Terminal 2
docker images lesson16-base
```

大約 306MB。

## 一、容器有自己的 127.0.0.1

```bash
docker rm -f l16
docker run -d --name l16 -p 127.0.0.1:8016:8000 lesson16-runtime
docker port l16
```

`8000/tcp -> 127.0.0.1:8016` — 把容器的 8000 發布成主機的 8016。

從主機打，**成功**：

```bash
curl -s -i http://127.0.0.1:8016/health
```

從容器內打同一個位址，**被拒絕**：

```bash
docker exec l16 python -c "
import urllib.request
try:
    urllib.request.urlopen('http://127.0.0.1:8016/health', timeout=3)
except Exception as e:
    print('port 8016 ->', type(e).__name__)
print('port 8000 ->', urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status)
"
```

`port 8016 -> URLError` / `port 8000 -> 200`

**容器的網路和主機的網路不是同一個。**`127.0.0.1` 永遠只指「我現在所在的這台機器」。

## 二、log 裡的 IP

```bash
docker logs l16
```

會看到 `192.168.215.1:xxxxx` — 不是你的筆電 IP，是 docker 網路的閘道。

拿真實來源要靠 proxy Header：

```bash
curl -s http://127.0.0.1:8016/request-info
curl -s -H 'X-Forwarded-For: 203.0.113.9' -H 'X-Forwarded-Proto: https' \
  http://127.0.0.1:8016/request-info
```

第二個會回 `{"client":"203.0.113.9",...}`。這個 Header 我是隨便 curl 出來的 — 所以 `--proxy-headers` 是信任宣告，只有後面有可信 proxy 時才安全。

## 三、兩個 ENV

```bash
docker exec l16 python -c "
import os
print('PYTHONUNBUFFERED =', os.environ.get('PYTHONUNBUFFERED'))
print('PYTHONDONTWRITEBYTECODE =', os.environ.get('PYTHONDONTWRITEBYTECODE'))
"
```

沒有 `PYTHONUNBUFFERED=1`，`print()` 會被緩衝，`docker logs` 會看起來像壞掉。

log 是容器的標準輸出，不是檔案。寫進檔案會讓 log 脫離 `docker logs`。

## 四、非 root

```bash
docker build --target runtime -t lesson16-runtime .
docker run --rm lesson16-base whoami      # root
docker run --rm lesson16-runtime whoami   # appuser
```

runtime image 裡**沒有 pytest**，因為它繼承 `base` 而不是 `test`。

## 五、容器裡只有 COPY 進去的東西

```bash
docker exec l16 ls /app        # main.py  requirements.txt
docker exec l16 ls /app/tests  # No such file or directory
```

`.dockerignore` 擋掉 `.env` — 和 `.gitignore` 是同一個原則的兩個出口。

## 六、健康檢查

```bash
docker inspect lesson16-runtime --format '{{json .Config.Healthcheck}}'
```

回 `null` — Dockerfile 沒有 `HEALTHCHECK`，這份是 `compose.yaml` 提供的。

確認它抓得到壞掉的狀態：

```bash
docker exec l16 python -c "
import urllib.request
try:
    urllib.request.urlopen('http://127.0.0.1:9999/health', timeout=2)
except Exception as e:
    print('dead port ->', type(e).__name__)
"
```

**判斷標準：把 port 改錯，它會不會紅？**

## 繳交

1. `docker build` 完整輸出（含 `DONE`）+ `docker images` 大小。目標機器沒有 Python 時，那 306MB 扮演什麼角色？
2. `docker run` + `docker port`（含 `8000/tcp -> 127.0.0.1:8016`）。`8016` 是誰決定的？改成 `9000:8000` 會影響容器裡的程式嗎？
3. 主機 `curl 127.0.0.1:8016/health` 得 `200`、容器內同一個位址得 `URLError`，**兩張並排**。用「網路命名空間」回答為什麼意思不同。
4. `docker logs` 的 `192.168.x.x` + `X-Forwarded-For` 證明。這個 Header 可以被誰偽造？Dockerfile 為什麼敢開 `--proxy-headers`？
5. `whoami` 在 base（`root`）與 runtime（`appuser`）兩張截圖。程式被塞住時這保護了什麼？
6. `ls /app` 與 `ls /app/tests` 失敗的截圖。`.env` 被 `docker build` 送進 image 和被 `git add` 進 repo，是同一個問題的兩個出口嗎？
7. 把 `compose.yaml` 的 healthcheck 埠從 `8000` 改成 `8016`，`docker compose up` 後 `docker compose ps` 的 STATUS 變成什麼？截圖。**改回去。** 說明 `start_period` 存在的原因。
8. `.git/`、`__pycache__/`、`.env`、你的作業截圖資料夾 — 各該不該進 `.dockerignore`？其中一個的答案取決於它是什麼，你怎麼分辨？

## 繳交前

`examples/http-api/Dockerfile`、`compose.yaml`、`.dockerignore` 是教材，第 7 題改完必須改回去。不要把任何真實憑證或 `.env` 加進版本控制。
