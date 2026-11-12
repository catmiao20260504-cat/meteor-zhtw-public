# Meteor Client 正體中文化

為 [Meteor Client](https://github.com/MeteorDevelopment/meteor-client) 製作的非官方正體中文化補丁。不修改 Meteor Client 的原始碼檔案內容，而是用一組小補丁加上一份翻譯表，在編譯時套用到上游原始碼，所以可以同時支援多個 Minecraft 版本，上游更新後也只需要重新編譯。

## 支援版本

| Minecraft | 上游來源 | 補丁 | Java |
| --- | --- | --- | --- |
| 26.3 | `master` | `mojang.patch` | 25 |
| 26.2 | commit `2385f7b4` | `mojang.patch` | 25 |
| 1.21.11 | `1.21.11` 分支 | `yarn.patch` | 21 |
| 1.21.10 | `1.21.10` 分支 | `yarn.patch` | 21 |
| 1.20.1 | `v0.5.4` 標籤 | `legacy-1.20.1.patch` | 17 |

已實際進遊戲測試的版本是 1.20.1、1.21.10 和 26.3，其餘版本使用同一組補丁建置，尚未逐一測試。

26.2 固定在上游升級到 26.3 之前的最後一個提交，之後上游對 26.2 沒有更新。

## 功能

- 介面翻譯：模組名稱與描述、設定名稱與選項、分類、分頁、按鈕、HUD 元件說明，共約 3000 條。
- 聊天回饋訊息翻譯：「已將 飛行 切換為 開啟。」這類訊息，包含模組名稱與開關狀態。
- 中文搜尋：模組與設定的搜尋框可以用中文，也仍然可以用英文。
- 內建中文字型：Meteor 自己的字型引擎沒有中文字形，編譯時會從 Noto Sans TC 切出只含翻譯用字的子集，放進字型貼圖。
- 標題畫面標語：中文模式下使用方塊梗標語庫，也可以在編譯時加入自己的標語。

只有在遊戲語言為繁體中文（臺灣或香港）時才會啟用翻譯，其他語言維持 Meteor 原本的樣子。

## 使用方式

### 用 GitHub Actions 編譯

1. 把這個 repo 放到你自己的 GitHub 帳號下。
2. 到 Actions 頁面，選擇 Build，按 Run workflow。
3. 編譯完成後，在該次執行的 Artifacts 下載對應版本的 jar。
4. 把 jar 放進 Minecraft 的 `mods` 資料夾，並安裝對應版本的 Fabric Loader 與 Fabric API。
5. 遊戲內到「語言」選擇「繁體中文（臺灣）」。

工作流程每週一也會自動重建一次，用來跟上上游更新。

### 在本機編譯

以 26.3 為例：

```
git clone https://github.com/MeteorDevelopment/meteor-client
cd meteor-client
git apply -C1 ../meteor-zhtw/patches/mojang.patch
mkdir -p src/main/resources/assets/meteor-client/tr
cp ../meteor-zhtw/data/zh_tw.json ../meteor-zhtw/data/splash.txt src/main/resources/assets/meteor-client/tr/
pip install fonttools
python3 ../meteor-zhtw/tools/build_cjk_font.py ../meteor-zhtw/data/zh_tw.json src/main/resources/assets/meteor-client/tr/cjk.ttf
./gradlew build
```

其他版本請先 `git checkout` 對應的分支、標籤或提交，並換用上表的補丁與 Java 版本。編譯結果在 `build/libs/`。

### 啟用與停用

- 遊戲語言是 `zh_tw` 或 `zh_hk` 時自動啟用。
- 加上 JVM 參數 `-Dmeteor.zhtw=true` 可以強制啟用，`-Dmeteor.zhtw=false` 可以強制停用。

## 專案結構

```
patches/
  mojang.patch              26.3、26.2 (Mojang 官方命名)
  yarn.patch                1.21.11、1.21.10 (Yarn 命名)
  legacy-1.20.1.patch       1.20.1
data/
  zh_tw.json                翻譯表
  splash.txt                方塊梗標語庫
  custom_splash.txt         自訂標語 (編譯時才加入)
tools/
  build_cjk_font.py         產生中文字型子集
  extract_strings.py        找出還沒翻譯的字串
licenses/
  OFL-NotoSansTC.txt        字型授權
.github/workflows/
  build.yml                 多版本編譯
```

## 補丁內容

補丁新增三個類別，並在上游原始碼上掛幾個小鉤子。

新增的類別位於 `utils/misc`：

| 類別 | 作用 |
| --- | --- |
| `Tr` | 判斷是否啟用、載入翻譯表、查詢譯文、翻譯聊天訊息的參數 |
| `CjkFont` | 載入內建中文字型，決定哪些字要放進字型貼圖 |
| `Splashes` | 管理標題畫面標語庫 |

掛上去的位置：

| 位置 | 作用 |
| --- | --- |
| `GuiRenderer.text`、`GuiTheme.textWidth` | 繪製與量測介面文字時查表翻譯 |
| `WMultiLabel` | 多行文字先翻譯，中文逐字換行 |
| `Utils.searchLevenshteinDefault` | 搜尋時同時比對英文與譯名 |
| `ChatUtils` | 聊天回饋訊息先翻譯樣板與參數再格式化 |
| `TextRenderer`、`Font` | 中文模式使用 Meteor 自己的字型引擎，並把中文字放進字型貼圖 |
| `Config` | 新增「自訂標語」開關，只在編譯時有自訂標語才顯示 |
| 標語 Mixin | 中文模式下從標語庫抽標語 |

1.21.10 與 1.21.11 另外調整了 `VanillaTextRenderer`，讓文字逐字串縮放。

## 自訂

### 翻譯

翻譯表是 `data/zh_tw.json`，鍵是英文原文，值是譯文。修改後重新編譯即可。

- 譯文要保留原文裡的佔位符，例如 `%s`、`%d`，順序也要一致。
- 聊天訊息裡的 `(highlight)`、`(default)` 是顏色標記，數量要和原文相同。
- 沒有翻譯的字串會維持英文，不會出錯。

找出還沒翻譯的字串：

```
python3 tools/extract_strings.py ../meteor-client data/zh_tw.json
```

結果會寫到 `untranslated.json`，把譯文填進去再合併回 `data/zh_tw.json` 就可以了。

### 標語

- `data/splash.txt`：預設的方塊梗標語庫，一行一句，`#` 開頭是註解，可以用 `§` 加顏色碼。
- `data/custom_splash.txt`：自訂標語，格式相同。檔案裡沒有任何實際內容時，編譯出來的版本沒有「自訂標語」選項；有內容時，設定的「視覺」區會出現「自訂標語」開關，預設開啟。

### 字型

預設只把翻譯表用到的字放進字型。`tools/build_cjk_font.py` 有選用參數：

- `--big5`：加入約 5400 個常用正體字，字型檔會變大很多，貼圖與啟動負擔也會增加。
- `--extra 檔案`：把其他檔案裡的字也放進字型。

## 已知限制

- 翻譯表以整句比對，由多段字串接起來的訊息只有前段會被翻譯。
- 聊天前綴標題（例如 Swarm、Config）與指令說明的懸停文字沒有翻譯。
- 字型貼圖只含翻譯表用到的字，輸入框裡打了表外的字，畫面上會顯示空白，但內容本身有保存。
- 在新版本上補丁可能因上游改動而套用失敗，需要依上游變化調整。

## 授權

補丁、腳本與翻譯表依 GNU General Public License v3.0 授權，見 `LICENSE`。內建字型 Noto Sans TC 依 SIL Open Font License 1.1 授權，見 `NOTICE.md`。

本專案是非官方專案，與 Meteor Development、Mojang Studios 及 Microsoft 沒有關係。使用時請遵守所在伺服器的規則。
