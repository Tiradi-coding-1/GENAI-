# Phase 4: K 線圖趨勢分析 Implementation Plan

**Goal:** 使用 Gemini 3 Pro 視覺 AI 分析 K 線圖，產出結構化趨勢分析報告

**Architecture:** AI 視覺分析任務，無程式碼產出

**Tool:** Gemini 3 Pro

---

## Task 1: 準備分析 Prompt

**Step 1: 設計通用分析 Prompt 模板**

```
你現在是一位台股技術分析師。

我提供你一張 K 線圖，這是台灣[族群名稱]族群的走勢圖，
包含 MA5、MA20 均線與成交量副圖，時間範圍為近 6 個月。

請依照以下格式分析：

## [族群名稱] 趨勢分析
### 整體趨勢
### 均線訊號
### 量價關係
### 族群內個股強弱
### 結論
```

**Step 2: 確認 Prompt 要素完整**

- 角色設定：台股技術分析師
- 輸入描述：K 線圖圖片 + 族群名稱
- 分析維度：5 個（趨勢/均線/量價/強弱/結論）
- 輸出格式：Markdown 標題層級

---

## Task 2: 分析族群一 — AI 散熱與電源管理

**Step 1: 上傳 charts/ai_cooling.png 至 Gemini 3 Pro**

**Step 2: 輸入 Prompt（替換族群名稱為「AI 散熱與電源管理」）**

**Step 3: 審核 AI 分析結果**

審核要點：
- 趨勢判斷是否與圖表一致
- 均線交叉描述是否正確
- 個股強弱排序是否合理
- 結論是否有可操作性

Expected: 取得族群一的分析文字

---

## Task 3: 分析族群二 — AI 伺服器與 ODM 代工

**Step 1: 上傳 charts/ai_server.png 至 Gemini 3 Pro**

**Step 2: 輸入 Prompt（替換族群名稱為「AI 伺服器與 ODM 代工」）**

**Step 3: 審核 AI 分析結果**

Expected: 取得族群二的分析文字

---

## Task 4: 分析族群三 — 晶圓代工與先進封裝

**Step 1: 上傳 charts/wafer_foundry.png 至 Gemini 3 Pro**

**Step 2: 輸入 Prompt（替換族群名稱為「晶圓代工與先進封裝」）**

**Step 3: 審核 AI 分析結果**

Expected: 取得族群三的分析文字

---

## Task 5: 彙整分析報告

**Files:**
- Create: `docs/analysis.md`

**Step 1: 將三個族群的分析結果彙整為單一報告**

結構：
```markdown
# 台股 AI 與半導體族群 K 線圖趨勢分析報告

> 分析日期：2026年4月
> 資料來源：近 6 個月 OHLCV 數據
> 分析工具：Gemini 視覺 AI

## 1. AI 散熱與電源管理族群
（分析內容）

## 2. AI 伺服器與 ODM 代工族群
（分析內容）

## 3. 晶圓代工與先進封裝族群
（分析內容）
```

**Step 2: Commit**

```bash
git add docs/analysis.md && git commit -m "docs: 完成 Phase 4 - K線圖趨勢分析報告"
```

---

## Task 6: 驗收檢查

1. docs/analysis.md 存在且格式正確
2. 三個族群均有完整的 5 段分析
3. 分析內容與 K 線圖實際走勢一致
4. 結論具備可操作性的建議
5. 備註包含免責聲明
