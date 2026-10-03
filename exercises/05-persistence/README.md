# 05 — 存資料：File 跟 SQLite 差在哪

三種存法，同樣寫入，結果三樣。這一課的重點只有一句話：**那個 `dict` 活不過一次執行。**

## 一、三種存法，先全部跑一次

```bash
cd exercises/05-persistence

python store.py dict-add
python store.py dict-list
python store.py json-add
python store.py json-list
python store.py sqlite-add
python store.py sqlite-list
```

`store.py` 每個模式只做兩件事之一——寫入或讀取——而且是**兩次不同的執行**。

**截圖必須包含全部六行的輸出。**

## 二、dict 為什麼讀不到

`dict-list` 只看到 `alice`。因為上一個 `dict-add` 的行程已經結束了。

## 三、文字檔同時寫會互相蓋掉

```bash
rm -f users.json
python store.py json-add
python json_race.py A & python json_race.py B & wait
cat users.json
```

**兩個 writer 都說自己成功了**，但檔案裡只剩 `writer-B`。

**截圖必須同時包含兩邊報成功，以及 `cat` 的輸出裡沒有 `writer-A`。**

## 四、SQLite 同時寫會擋住

```bash
python hold_the_lock.py hold
```

三秒內在另一個 Terminal 送出第二個 writer：

```bash
python hold_the_lock.py write
```

`writer B: refused -> database is locked`。

和第三格對照：文字檔是靜靜地丟資料，SQLite 是明確地說「不行」。這個差別在付款、下單、扣庫存的地方決定成敗。

## 五、看一眼兩種檔案本身

```bash
ls -l users.json notes.db
file notes.db
```

一個幾十 bytes、一個固定大小。`file` 會告訴你 `notes.db` 是什麼格式。

## 看資料庫怎麼讀

`indexes.py` 會自己建一張 5 萬列的表，不需要先啟動任何東西：

```bash
python indexes.py plan       # 沒有索引：SCAN notes
python indexes.py index      # 有索引：SEARCH notes USING INDEX
python indexes.py composite  # 怎麼讀 plan 那一行
python indexes.py cost       # 索引讓寫入變慢多少
python indexes.py unused     # 沒人用的索引讓檔案變大多少
```

`plan` 與 `index` 回傳的資料一模一樣，差的是 `SCAN`（讀完 5 萬列）變成 `SEARCH`（直接跳過去）。

**你的時間數字會跟課本不同，plan 那行字不會。**看 plan。

## 繳交

1. 六個 `store.py` 模式的輸出截圖（全部六行）+ 回答：哪一個模式在**新行程**裡讀得到資料？
2. `json_race.py` 的完整輸出 + `cat users.json`，必須同時包含「兩邊都報成功」與「檔案裡沒有 `writer-A`」。回答：**有沒有任何一行輸出告訴你資料掉了？**
3. `hold_the_lock.py hold` 與 `hold_the_lock.py write` 的兩張截圖（必須含 `database is locked`）+ `file notes.db`。回答：SQLite 做了文字檔沒做的事，是什麼？
4. `ls -l` 與 `file notes.db` 的輸出截圖。**回答：一個固定大小、一個跟著資料量長，這個差別來自哪裡？**
5. 回答：第三格和第四格，哪一個的失敗方式對「付款」這種動作比較可以接受？**用你在第 2、3 題親眼看到的那件事回答，不要寫「比較安全」。**
6. 回答：如果你的 API 跑兩個執行緒、兩個都往 `users.json` 寫，你會選第三格還是第四格的解法？寫出你根據的事實。

## 繳交前

`users.json` 與 `notes.db` 產生的檔案是這一次練習的結果，可以一起提交當紀錄。不要把任何真實資料寫進去。
