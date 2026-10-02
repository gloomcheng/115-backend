# 13 — 測試：讓契約每次都被檢查

測試的價值不是「通過」，是「程式碼改錯時會失敗」。所以這個練習的核心是一場故意製造的失敗。

不需要開 `fastapi dev`。

```bash
cd exercises/13-testing
pytest -q
```

## 一、基準：還沒動過的樣子

```bash
pytest -q
pytest -v
```

`pytest -v` 會列出七條測試的名稱。這七行是第 05 節那張契約表的證據來源，先截圖。

## 二、故意改壞

把 `main.py` 裡 `health()` 的回傳值從 `{"ok": True}` 改成 `{"ok": "yes"}`。

```bash
pytest -q
```

`.F.....`，然後是：

```
AssertionError: assert {'ok': 'yes'} == {'ok': True}
```

**路由沒有壞** — 路徑、方法、狀態碼都還是原來的。只有 Body 那一列的承諾沒兌現。

## 三、最重要的一張截圖

```bash
pytest -v
```

看第 1 行和第 2 行：

```
tests/test_contract.py::test_health_returns_200 PASSED                   [ 14%]
tests/test_contract.py::test_health_body_is_exactly_ok_true FAILED       [ 28%]
```

兩條測試看的是同一個 process 裡的同一份壞掉的程式碼。一條說沒事，一條說壞了。差別只有一行斷言。

再單獨跑那條狀態碼測試：

```bash
pytest -q -k test_health_returns_200
```

`1 passed`。**API 是壞的。**

## 四、反方向實驗

把 `tests/test_contract.py` 裡的 `test_health_body_is_exactly_ok_true` 整條刪掉，`main.py` 保持壞的，然後：

```bash
pytest -q
```

`6 passed`。壞掉的 API，全綠的套件。

**這跟沒有測試有差別嗎？**

把 `main.py` 還原，把測試寫回去，確認回到 `7 passed`。

## 五、沒有 pytest 也會失敗

```bash
python -c "assert {'ok': 'yes'} == {'ok': True}"
```

`AssertionError`。`assert` 是 Python 的關鍵字，不是 pytest 的功能。

## 繳交

1. `pytest -q` 綠燈截圖（`7 passed`）+ `pytest -v` 詳細截圖（七行名稱）。
2. 改壞後的 `pytest -q` 截圖，含 `.F.....` 與 `AssertionError`。
3. 壞掉的程式碼上的 `pytest -v` 截圖，**同時**含 `test_health_returns_200 PASSED` 與 `test_health_body_is_exactly_ok_true FAILED`。為什麼同一個壞掉的 API，一條說好一條說壞？
4. 只跑狀態碼測試（`1 passed`）+ 刪掉 Body 斷言後全套件（`6 passed`）。第 04 節說「綠色代表行為沒變」，這兩張分別證明了什麼？
5. 自己寫一條新測試，斷言 `GET /notes` 的 `count` 是整數且不小於 `len(items)`。通過後把 `count` 改成字串 `"1"`，截圖必須含 `1 failed`。
6. 寫一條測試斷言 `POST /notes` 缺 `name` 時**狀態碼是 `422`**，而且 `content-type` 是 `application/json`——**兩條都要寫**。通過後把 `raise HTTPException(...)` 改成 `return {"detail": ...}`，截圖必須含失敗。狀態碼變 `200` 時是哪一條發現的？`content-type` 有沒有跟著變？
7. 為什麼 `test_list_reports_a_count_that_matches_the_items` 斷言 `count == len(items)` 而不是 `count == 1`？各自在什麼情況下會誤報？
8. 為什麼 `pytest` 取代不了 `curl`，`curl` 取代不了 `pytest`？用課本第 06 節那張表回答。

## 繳交前

`main.py` 必須維持第 1 步的狀態（`{"ok": True}`），`tests/test_contract.py` 必須是完整的七條。被改壞的 `main.py` 或缺斷言的測試檔都不該進版本控制。
