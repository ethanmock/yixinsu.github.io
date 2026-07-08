# 维护指南 · Updating this site

个人主页托管在 GitHub Pages（`main` 分支根目录的 `index.html`）。仓库为用户主站 `ethanmock.github.io`，线上地址 `https://ethanmock.github.io/`。

## 目录结构

| 路径 | 说明 |
|------|------|
| `index.html` | 发布用的自包含页面（**自动生成，勿手改内容数据**） |
| `data/news.json` | 新闻/动态（**在这里改**） |
| `data/publications.json` | 论文列表（**在这里改**） |
| `scripts/build.py` | 把 `data/*.json` 注入 `index.html` 的构建脚本 |
| `assets/fonts/` | 自托管子集化字体（Newsreader + Noto Serif SC，按需懒加载） |

## 更新新闻或论文（最常见）

1. 编辑 `data/news.json` 或 `data/publications.json`。
2. 运行构建：
   ```bash
   python3 scripts/build.py
   ```
3. 提交：
   ```bash
   git add -A && git commit -m "Update publications" && git push
   ```
   推送后 GitHub Pages 几分钟内生效。

> 提示：`python3 scripts/build.py --check` 可检查 `index.html` 是否与 `data/*.json` 一致（用于 CI / 提交前自检），不修改文件。

### 字段说明

**`data/news.json`** — 每条：
```json
{ "date": "2025.08", "en": "English text.", "zh": "中文文本。" }
```
最新的放最前面。

**`data/publications.json`** — 每条：
```json
{
  "year": 2025,
  "title": "论文标题",
  "authors": "Yixin Su#, Co-Author*, ...",
  "venue": "AAAI 2025",
  "badges": ["CCF-A"],
  "links": [{ "label": "paper", "url": "https://..." }],
  "topics": ["rec", "gnn"]
}
```
- `#` 表示共同一作，`*` 表示通讯作者（页面底部有图例）。
- `badges`：如 `CCF-A`、`SCI Q1 · IF 8.1`，可留空 `[]`。
- `links`：`label` 常用 `paper` / `code`，可留空 `[]`。
- `topics`：用于分类筛选，取值 `llm` `rec` `fi`（特征交互）`gnn` `bio` `nlp`（对应导航里的类别按钮）。

## 改其它内容（简介、导航、招生、教学等）

这些文本目前内联在 `index.html` 的模板里（双语）。少量修改可以直接搜索英文原文替换；较多改动建议告知维护者从设计源重新生成。**注意**：`index.html` 是打包产物，字体、脚本、样式都在其中，除内容数据外不要随意手改。

## 换头像

页面右上角当前是占位（`portrait`）。放真实照片的方式：把照片放到 `assets/`，再在模板中把占位块替换为 `<img>`。若不确定，交给维护者处理。

## 字体说明（为什么这么快）

原始导出是单个 8.8MB 文件（整套中文衬线字体以 base64 内嵌）。现已：
- 字体子集化并拆成按 `unicode-range` 懒加载的 `assets/fonts/*.woff2`；
- `index.html` 降到约 340KB，首屏英文只额外加载约 180KB 字体，切到中文再按需加载所需字块。

`assets/fonts/` 由构建时生成，日常更新内容**无需**重建字体。若将来新增了很生僻、当前字体子集未覆盖的汉字，该字会回退到系统字体——如需扩充子集，联系维护者重跑字体子集脚本。
