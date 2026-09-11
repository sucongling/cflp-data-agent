import akshare as ak
import pandas as pd
from datetime import datetime
import os
import re
import requests
from bs4 import BeautifulSoup

os.makedirs("data", exist_ok=True)

print("=" * 60)
print(f"开始采集数据: {datetime.now().isoformat()}")
print("=" * 60)

success_files = []

# 1. 月度整体运价指数
try:
    print("\n[1/6] 获取公路物流运价指数（月指数）...")
    df = ak.index_price_cflp(symbol="月指数")
    f = "data/price_index_month.csv"
    df.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# 2. 月度整体运量指数
try:
    print("\n[2/6] 获取公路物流运量指数（月指数）...")
    df = ak.index_volume_cflp(symbol="月指数")
    f = "data/volume_index_month.csv"
    df.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# 3. 周度整体运价指数
try:
    print("\n[3/6] 获取公路物流运价指数（周指数）...")
    df = ak.index_price_cflp(symbol="周指数")
    f = "data/price_index_week.csv"
    df.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# 4. 制造业PMI（含非制造业）
try:
    print("\n[4/6] 获取制造业PMI...")
    df = ak.macro_china_pmi()
    f = "data/pmi_manufacturing.csv"
    df.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# 5. 物流景气指数
try:
    print("\n[5/6] 获取物流景气指数...")
    df = ak.macro_china_lpi_index()
    f = "data/lpi.csv"
    df.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")
# ========== 6. 分线路运价数据（下载图片 + OCR识别 + 纵向累积） ==========
try:
    print("\n[6/6] 获取分线路运价数据...")
    import re
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    import shutil

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://www.chinawuliu.com.cn/",
    }

    if os.path.exists("data/route_images"):
        shutil.rmtree("data/route_images")
    os.makedirs("data/route_images", exist_ok=True)

    # 1. 找最新周报
    list_url = "http://www.chinawuliu.com.cn/zt/jtbzwltj/list.shtml"
    resp = requests.get(list_url, headers=headers, timeout=30)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    links = soup.find_all("a", string=re.compile(r"中国公路物流运价周指数报告"))
    if not links:
        raise Exception("未找到周报链接")

    latest_url = links[0].get("href")
    if not latest_url.startswith("http"):
        latest_url = urljoin("http://www.chinawuliu.com.cn", latest_url)
    print(f"  最新周报: {latest_url}")

    # 2. 提取发布日期
    m = re.search(r"/(\d{6})/(\d{2})/", latest_url)
    if m:
        publish_date = f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(2)}"
    else:
        publish_date = datetime.now().strftime("%Y-%m-%d")
    print(f"  发布日期: {publish_date}")

    # 3. 去重检查
    f = "data/route_price.csv"
    existing_df = pd.DataFrame()
    if os.path.exists(f):
        existing_df = pd.read_csv(f, encoding='utf-8-sig', dtype=str)
        print(f"  已存在数据库，共 {len(existing_df)} 行")
        if "发布日期" in existing_df.columns and publish_date in existing_df["发布日期"].values:
            print(f"  ⏭️ {publish_date} 数据已存在，跳过")
            success_files.append(f)
            raise StopIteration()

    # 4. 下载表1图片
    article_resp = requests.get(latest_url, headers=headers, timeout=30)
    article_resp.encoding = "utf-8"
    article_soup = BeautifulSoup(article_resp.text, "html.parser")

    images = article_soup.find_all("img")
    table_img_path = None
    for i, img in enumerate(images):
        src = img.get("src", "") or img.get("data-src", "")
        if not src:
            continue
        if i + 1 == 5:
            full_url = urljoin(latest_url, src)
            try:
                img_resp = requests.get(full_url, headers=headers, timeout=30)
                if img_resp.status_code == 200:
                    table_img_path = "data/route_images/route_table_5.png"
                    with open(table_img_path, "wb") as fp:
                        fp.write(img_resp.content)
                    print(f"  ✅ 表1图片已下载")
            except Exception as e:
                print(f"  ⚠️ 图片下载失败: {e}")

    if not table_img_path or not os.path.exists(table_img_path):
        raise Exception("表1图片未下载")

    # 5. OCR 识别
    print("  正在 OCR 识别...")
    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR()
    result, _ = engine(table_img_path)

    if not result:
        raise Exception("OCR 未识别到任何文字")

    # 6. 按 y 坐标分组为行
    blocks = []
    for box, text, score in result:
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        blocks.append({"text": text.strip(), "x": sum(xs) / 4, "y": sum(ys) / 4})

    blocks.sort(key=lambda b: b["y"])
    rows = []
    current_row = []
    last_y = None
    for b in blocks:
        if last_y is None or abs(b["y"] - last_y) < 15:
            current_row.append(b)
        else:
            rows.append(sorted(current_row, key=lambda x: x["x"]))
            current_row = [b]
        last_y = b["y"]
    if current_row:
        rows.append(sorted(current_row, key=lambda x: x["x"]))

    table_data = [[cell["text"] for cell in row] for row in rows]
    max_cols = max(len(r) for r in table_data) if table_data else 0
    table_data = [r + [""] * (max_cols - len(r)) for r in table_data]

    # 7. 转换为纵向记录
    if len(table_data) < 3:
        raise Exception("OCR 结果行数不足")

    header = table_data[0]
    data_rows = table_data[1:]

    # 表头：["线路", "单位", "西安-成都", "长沙-厦门", "宁波-深圳"]
    route_names = header[2:]
    print(f"  识别到 {len(route_names)} 条线路: {route_names}")

    new_records = []
    i = 0
    while i < len(data_rows) - 1:
        price_row = data_rows[i]
        change_row = data_rows[i + 1]

        # 判断是否是价格-环比配对
        if len(price_row) < 3 or len(change_row) < 3:
            i += 1
            continue

        vehicle_type = price_row[0]
        unit = price_row[1]

        for j, route in enumerate(route_names):
            col_idx = j + 2
            if col_idx < len(price_row) and col_idx < len(change_row):
                price = price_row[col_idx]
                change = change_row[col_idx]
                new_records.append({
                    "发布日期": publish_date,
                    "线路": route,
                    "车型": vehicle_type,
                    "单位": unit,
                    "价格": price,
                    "环比(%)": change,
                })
        i += 2  # 跳到下一对价格-环比

    if not new_records:
        raise Exception("未生成任何记录")

    new_df = pd.DataFrame(new_records)
    print(f"  本次新增: {len(new_df)} 条记录")

    # 8. 合并新旧数据，按 (发布日期, 线路, 车型) 去重
    if not existing_df.empty:
        merged_df = pd.concat([existing_df, new_df], ignore_index=True)
        merged_df = merged_df.drop_duplicates(
            subset=["发布日期", "线路", "车型"], keep="last"
        )
    else:
        merged_df = new_df

    merged_df.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 分线路数据累积成功")
    print(f"   数据库总计: {len(merged_df)} 行")
    print(f"   已包含 {merged_df['发布日期'].nunique()} 个发布日期")
    print(merged_df.tail(10).to_string())

except StopIteration:
    pass
except Exception as e:
    print(f"❌ 分线路数据获取失败: {e}")

# ========== 7. 中国仓储指数 ==========
try:
    print("\n[7/7] 获取中国仓储指数...")
    import re
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://www.chinawuliu.com.cn/",
    }

    # 1. 获取中物联统计信息列表页
    list_url = "http://www.chinawuliu.com.cn/lhhzq/tjxx/index.shtml"
    resp = requests.get(list_url, headers=headers, timeout=30)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # 2. 找到最新一篇“中国仓储指数为”文章
    links = soup.find_all("a", string=re.compile(r"中国仓储指数为"))
    if not links:
        raise Exception("未找到仓储指数文章链接")

    latest_url = links[0].get("href")
    if not latest_url.startswith("http"):
        latest_url = urljoin("http://www.chinawuliu.com.cn", latest_url)
    print(f"  最新文章: {latest_url}")

    # 3. 进入文章页，提取综合指数值
    article_resp = requests.get(latest_url, headers=headers, timeout=30)
    article_resp.encoding = "utf-8"
    article_soup = BeautifulSoup(article_resp.text, "html.parser")
    text = article_soup.get_text()

    # 提取“2026年8月份为48.5%”这类模式
    m = re.search(r"(\d{4})年(\d{1,2})月份为([\d.]+)%", text)
    if not m:
        raise Exception("未识别到仓储指数值")

    year, month, index_value = m.group(1), m.group(2).zfill(2), m.group(3)
    period = f"{year}-{month}"
    print(f"  期数: {period}，综合指数: {index_value}")

    # 4. 去重检查
    f = "data/warehouse_index.csv"
    existing_df = pd.DataFrame()
    if os.path.exists(f):
        existing_df = pd.read_csv(f, encoding='utf-8-sig', dtype=str)
        if "期数" in existing_df.columns and period in existing_df["期数"].values:
            print(f"  ⏭️ {period} 数据已存在，跳过")
            success_files.append(f)
            raise StopIteration()

    # 5. 构建记录（可扩展分项指数）
    new_record = {
        "期数": period,
        "综合指数": index_value,
        "发布日期": datetime.now().strftime("%Y-%m-%d"),
    }

    # 尝试提取分项指数（新订单、期末库存、平均库存周转次数等）
    for item_name in ["新订单指数", "期末库存指数", "平均库存周转次数指数", "企业员工指数", "业务活动预期指数"]:
        pattern = rf"{item_name}为([\d.]+)%"
        item_m = re.search(pattern, text)
        if item_m:
            new_record[item_name] = item_m.group(1)

    new_df = pd.DataFrame([new_record])

    # 6. 合并
    if not existing_df.empty:
        merged_df = pd.concat([existing_df, new_df], ignore_index=True)
        merged_df = merged_df.drop_duplicates(subset=["期数"], keep="last")
    else:
        merged_df = new_df

    merged_df.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 仓储指数累积成功，数据库共 {len(merged_df)} 行")

except StopIteration:
    pass
except Exception as e:
    print(f"❌ 仓储指数获取失败: {e}")
