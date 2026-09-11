# 中国物流数据看板

自动采集中国物流与采购联合会公开数据，通过 GitHub Actions 定时运行，结果展示在 GitHub Pages。

🔗 看板地址：https://sucongling.github.io/cflp-data-agent/
[![Scrape Task](https://github.com/sucongling/cflp-data-agent/actions/workflows/scrape_task.yml/badge.svg)](https://github.com/sucongling/cflp-data-agent/actions/workflows/scrape_task.yml)


## 数据源

| 数据 | 采集方式 | 更新频率 |
| :--- | :--- | :--- |
| 制造业 PMI | akshare 接口 | 每月 |
| 公路物流运价指数（月度） | akshare 接口 | 每月 |
| 公路物流运价指数（周度） | akshare 接口 | 每周 |
| 公路物流运量指数 | akshare 接口 | 已停更（截至 2020-08） |
| 物流景气指数 | akshare 接口 | 每月 |
| 中国仓储指数 | 网页抓取 | 每月 |
| 分线路运价表 | 网页抓取 + OCR 识别 | 每周（累积） |

## 项目结构

- `script.py` — 数据采集脚本
- `.github/workflows/scrape_task.yml` — 定时任务配置
- `data/` — 采集到的原始 CSV
  - `pmi_manufacturing.csv` — 制造业 PMI
  - `price_index_month.csv` — 月度运价指数
  - `price_index_week.csv` — 周度运价指数
  - `volume_index_month.csv` — 月度运量指数
  - `lpi.csv` — 物流景气指数
  - `warehouse_index.csv` — 中国仓储指数
  - `route_price.csv` — 分线路运价（累积）
  - `route_images/` — OCR 用的表格图片
- `docs/` — GitHub Pages 看板
  - `index.html` — 页面结构
  - `style.css` — 样式
  - `app.js` — 数据加载与图表
  - `data/` — 看板读取的 CSV（Actions 自动同步）

## 运行方式

- **自动**：每周六 UTC 9:00（北京时间 17:00）自动运行
- **手动**：Actions → Scrape Task → Run workflow

## 技术栈

- **数据采集**：Python + akshare + requests + BeautifulSoup
- **OCR**：RapidOCR（识别周报图片中的表格）
- **自动化**：GitHub Actions
- **可视化**：GitHub Pages + Chart.js
