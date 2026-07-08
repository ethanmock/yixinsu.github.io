# 维护手册 · Updating this site

个人主页托管在 **GitHub Pages**（用户主站，仓库 `ethanmock/ethanmock.github.io`，`main` 分支根目录），线上地址 **https://ethanmock.github.io/** 。无自定义域名、无 CNAME。

页面 `index.html` 是 Claude Design 导出的**自包含打包产物**（内含模板 + React + 样式）。**所有日常修改都通过 `data/` 下的文件完成，然后跑一次构建脚本，切勿手改 `index.html` 里的内容。**

---

## 0. 核心工作流（先记这一条）

```
改 data/ 里的文件  →  python3 scripts/build.py  →  git add / commit / push
```

推送后 GitHub Pages 1–3 分钟自动生效。浏览器看不到更新时按 Ctrl/Cmd + Shift + R 强刷。

- `python3 scripts/build.py` —— 把 `data/` 内容注入 `index.html`。
- `python3 scripts/build.py --check` —— 只检查是否已同步，不改文件（可用于提交前自检）。

> 环境要求：只需要 `python3`（macOS 自带）。无需 Node、无需安装任何依赖。

---

## 1. 目录结构

| 路径 | 说明 | 是否手改 |
|------|------|----------|
| `index.html` | 发布用的自包含页面 | ❌ 由脚本生成 |
| `data/news.json` | 新闻 / 动态 | ✅ **在这里改** |
| `data/publications.json` | 论文列表 | ✅ **在这里改** |
| `data/config.json` | 站点设置（主题色 / 语言 / demo 等） | ✅ **在这里改** |
| `scripts/build.py` | 构建脚本（注入 data → index.html） | 一般不动 |
| `assets/fonts/` | 自托管子集化字体（懒加载） | ❌ 自动生成 |
| `demo.html`（可选） | 你自己的交互 demo 页面 | ✅ 需要时自建 |

---

## 2. 日常更新之一：加/改**新闻动态**

编辑 `data/news.json`，它是一个数组，**最新的放最前面**。每条格式：

```json
{ "date": "2025.08", "en": "One paper accepted by Cell Reports (SCI-Q1, IF 8.1).", "zh": "一篇论文被 Cell Reports 接收（SCI 一区，IF 8.1）。" }
```

| 字段 | 说明 |
|------|------|
| `date` | 显示用日期，格式随意，惯例 `YYYY.MM` |
| `en` | 英文文本（英文界面显示） |
| `zh` | 中文文本（中文界面显示） |

**例：在最前面加一条**
```json
[
  { "date": "2026.07", "en": "New paper accepted by NeurIPS 2026.", "zh": "一篇论文被 NeurIPS 2026 接收。" },
  { "date": "2025.08", "en": "One paper accepted by Cell Reports (SCI-Q1, IF 8.1).", "zh": "一篇论文被 Cell Reports 接收（SCI 一区，IF 8.1）。" }
]
```
然后 `python3 scripts/build.py` → 提交。

---

## 3. 日常更新之二：加/改**论文**

编辑 `data/publications.json`，数组，一般按年份从新到旧。每条格式：

```json
{
  "year": 2025,
  "title": "IEDR: A Context-aware Intrinsic and Extrinsic Disentangled Recommender System",
  "authors": "Yixin Su#, Wei Jiang#, ..., Rui Zhang*",
  "venue": "ACM TOIS 2025",
  "badges": ["CCF-A"],
  "links": [{ "label": "paper", "url": "https://arxiv.org/abs/..." }],
  "topics": ["rec"]
}
```

| 字段 | 说明 |
|------|------|
| `year` | 数字年份，用于分组显示 |
| `title` | 论文标题 |
| `authors` | 作者串。`#` = 共同一作，`*` = 通讯作者（页面底部有图例） |
| `venue` | 会议/期刊 + 年份，如 `AAAI 2025`、`IEEE TKDE 2025` |
| `badges` | 徽章数组，如 `["CCF-A"]`、`["SCI Q1 · IF 8.1"]`；无则 `[]` |
| `links` | 链接数组，每项 `{ "label": "paper", "url": "..." }`；`label` 常用 `paper` / `code`；无则 `[]` |
| `topics` | 分类标签数组，决定"分类筛选"按钮里出现在哪一类（见下表） |

**`topics` 取值 ↔ 页面分类按钮**

| topics 值 | 对应类别 |
|-----------|----------|
| `llm` | LLM & Foundation |
| `rec` | Recommender |
| `fi`  | Feature Interaction |
| `gnn` | Graph NN |
| `bio` | AI × Bio/Med |
| `nlp` | NLP |

一篇论文可属多类，如 `"topics": ["gnn", "llm"]`。

---

## 4. 日常更新之三：**站点设置** `data/config.json`

```json
{
  "accent": "#1a3a5c",
  "defaultLang": "en",
  "showResearchDemo": true,
  "demoUrl": ""
}
```

| 字段 | 作用 | 可选值 |
|------|------|--------|
| `accent` | 主题强调色 | `#7a1f2b`(酒红) / `#1a3a5c`(藏蓝, 当前) / `#2f5d4f`(墨绿) / `#333333`(近黑)，或任意十六进制色 |
| `defaultLang` | 打开页面时的默认语言 | `"en"` 或 `"zh"` |
| `showResearchDemo` | 是否显示 "Research / Live demo" 整个区块 | `true` / `false` |
| `demoUrl` | Research 区嵌入的页面地址；当前是 `demo.html`（研究亮点卡片） | 见第 5 节 |

改完同样：`python3 scripts/build.py` → 提交。

---

## 5. **Research 亮点 / Demo**（重点）

主页 "Research" 区通过 `<iframe>` 嵌入 `data/config.json` 里 `demoUrl` 指向的页面：**`demoUrl` 非空就把它当作网页嵌进来**；为空则显示占位。

### 5.1 当前内容：研究亮点卡片 `demo.html`

现在 `demoUrl` 指向 `demo.html`——一个**可翻页的"研究亮点"卡片**（中英双语、左右翻页、每张一句话通俗解读 + 链接），目的是让访客 30 秒看懂代表工作。

**加/改/删亮点卡片** = 编辑 `demo.html` 顶部的 `CARDS` 数组，每张卡片：
```js
{
  badge: "AAAI 2021 · CCF-A",              // 会场 · 徽章
  topic: { en: "Feature Interaction", zh: "特征交互" },
  title: "Detecting Beneficial Feature Interactions for Recommender Systems",
  authors: "Yixin Su, Rui Zhang, Sarah Erfani*, Zhenghua Xu*",
  summary: { en: "一句话英文解读", zh: "一句话中文解读" },
  note: { en: "亮点/收录说明(可选)", zh: "..." },   // 无则写 null
  image: "",                                // 配图：留空则用主题矢量图；填真实图见下
  art: "fi",                                // 无配图时的主题图: fi(特征交互)/rec(推荐)/bio(医工)
  links: [ { label: "paper", url: "https://..." } ]  // 无则写 []
}
```

**给某篇配真实论文图**：把图片（框架图/teaser）放到 `assets/highlights/`（如 `assets/highlights/sign.png`），再把该卡片的 `image` 设成 `"assets/highlights/sign.png"` 即可（会自动替换主题矢量图）。桌面端图在左、文字在右；手机端自动只显示文字。
> **点卡片会跳到主页发表列表里对应的论文并高亮**——靠"卡片 `title` 与 `data/publications.json` 里该论文 `title` 完全一致"来定位。所以改卡片标题时，务必和发表列表里的标题保持一字不差（否则跳转会失效）。
>
> `demo.html` 是独立文件，改完**无需**跑 `build.py`，直接 `git commit && git push` 即可（`build.py` 只负责把 `demoUrl` 这个地址写进主页，不碰 demo 内容）。改完想本地看：`python3 -m http.server 4599` 然后开 `http://localhost:4599/demo.html`。

如果之后想改标题"Research Highlights / 研究亮点"这行小标题文案，它在 `index.html` 模板的 `research:` 文案块里（中英各一处）。

### 5.2 换成别的 demo（比如某篇论文的交互可视化）

若将来做了真正可跑的交互 demo，把它做成独立页面替换即可。逻辑很简单：**`demoUrl` 一旦非空，该区就把它当作网页用 `<iframe>` 嵌进来**；为空时显示占位。

### 步骤

1. **做一个独立的 demo 网页**，命名为 `demo.html`，放到仓库**根目录**（和 `index.html` 同级）。
   - 它是一个完整、可独立打开的页面（自带所需的 HTML/CSS/JS）。
   - 内容不限：推荐/特征交互模型的可视化、一个小的交互工具等。
   - 想放多文件的复杂 demo，就建个文件夹，比如 `demo/index.html` + 它的资源，然后把 `demoUrl` 设为 `"demo/"`。
2. **在 `data/config.json` 里把 `demoUrl` 指过去**：
   ```json
   "demoUrl": "demo.html"
   ```
   （用文件夹形式则写 `"demo/"`。用相对路径，不要写成 `/demo.html` 开头的绝对路径。）
3. **构建并发布**：
   ```bash
   python3 scripts/build.py
   git add -A && git commit -m "Add research demo" && git push
   ```
4. 打开 https://ethanmock.github.io/ ，Research 区就会内嵌你的 demo。

### 本地预览 demo（可选，推荐发布前先看）
```bash
cd /Users/yixinsu-hust/code/yixinsu.github.io
python3 -m http.server 4599
# 浏览器打开 http://localhost:4599/index.html 看整体，
# 或 http://localhost:4599/demo.html 单独看 demo
```

### 撤下 demo
把 `demoUrl` 改回 `""`（或把 `showResearchDemo` 设为 `false` 整块隐藏），再构建、提交即可。

> demo 页面本身之后随便改：它是独立文件，改完直接 `git commit && git push`，**无需**再跑 `build.py`（build.py 只管把 `demoUrl` 这个"地址"写进 index.html，不碰 demo 内容）。

---

## 6. 改其它文字（简介 / 导航 / 招生 / 教学等）

这些双语文案目前**内联在 `index.html` 的模板里**，没有抽成 data 文件。少量改动可以直接在 `index.html` 里搜索英文原文替换（中英两处都要改）。**注意**：`index.html` 是打包产物，除内容外的结构/字体/脚本不要动；改完用 `python3 scripts/build.py --check` 确认没破坏结构（应显示 in sync）。改动较多时建议找维护者从设计源重新生成，更安全。

> **Teaching / Students 区当前已隐藏**（连同导航里的 Teaching 链接一起移除了，因为暂无内容）。等你有课程/学生信息了告诉我，我从 git 历史恢复并做成和 Publications 一样的数据驱动形式（改 JSON 即可更新）。

---

## 7. 换头像

右上角当前是占位（斜纹 "portrait"）。放真实照片：把照片放进 `assets/`（如 `assets/portrait.jpg`），再在 `index.html` 模板中把占位块替换为 `<img src="assets/portrait.jpg" ...>`。不确定就交给维护者。

---

## 8. 字体说明（为什么这么快）

原始导出是单个 8.8MB 文件（整套中文衬线字体以 base64 内嵌）。现已子集化拆成按 `unicode-range` 懒加载的 `assets/fonts/*.woff2`：`index.html` 约 340KB，英文首屏只额外加载 ~180KB 字体，切中文再按需取所需字块。

`assets/fonts/` 由字体子集脚本一次性生成，**日常更新内容无需重建字体**。若将来新增了当前子集未覆盖的生僻字（会回退成系统字体），联系维护者重跑子集脚本扩充即可。

---

## 9. 命令速查

```bash
cd /Users/yixinsu-hust/code/yixinsu.github.io

# 改 data/*.json 后构建
python3 scripts/build.py

# 提交前自检是否同步
python3 scripts/build.py --check

# 本地预览
python3 -m http.server 4599   # 打开 http://localhost:4599/index.html

# 发布上线
git add -A
git commit -m "Update content"
git push
```

线上：**https://ethanmock.github.io/**
