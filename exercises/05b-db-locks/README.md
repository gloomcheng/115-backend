# 05b — 兩個請求同時搶 DB lock 會怎樣

同學的問題是：兩個請求同時進來，假設真的同時搶到資料庫鎖，會怎樣？

答案是那個假設不成立。SQLite 的寫鎖只有一個持有者，第二個請求會收到 `database is locked` 拒絕訊息。資料不會被安靜蓋掉。

## 一、跑一次真實的競爭

```bash
cd exercises/05b-db-locks
rm -f locks.db
python retry_the_lock.py
```

預期輸出：

```text
holder: BEGIN EXCLUSIVE -> write lock acquired
loser: attempt 1 -> database is locked
loser: attempt 2 -> database is locked
holder: COMMIT -> lock released
loser: attempt 3 -> committed
replay: same loser id inserted again -> rows for loser = 1
winner rows: 1, loser rows: 1
```

截圖必須包含兩次 `database is locked`、`COMMIT -> lock released` 與最後兩行。

## 二、輸出在說什麼

holder 從 `BEGIN EXCLUSIVE` 到 `COMMIT` 之間持有寫鎖。loser 兩次都在 `busy_timeout` 到期後收到拒絕。holder 釋放鎖之後，loser 第三次才成功。

## 三、為什麼重送不會寫出兩筆

表格的 `id` 是 `PRIMARY KEY`。`INSERT ... ON CONFLICT(id) DO NOTHING` 讓同一筆重送只留下一列。`rows for loser = 1` 就是證據。

## 四、跑測試

```bash
python -m unittest -v test_retry_the_lock.py
```

測試用暫存資料庫，不會動到 `locks.db`。

## 五、自己改參數

1. 把 `hold_seconds` 改成 `0.1`，重跑。回答：loser 還會收到拒絕嗎？
2. 把 `ON CONFLICT(id) DO NOTHING` 改成普通 `INSERT`，重跑。回答：最後有幾筆 `loser`？
3. 回答：如果重試用完還是拿不到鎖，API 應該回什麼狀態碼？

本機產生的 `locks.db` 已被 `.gitignore` 排除，不要提交。
