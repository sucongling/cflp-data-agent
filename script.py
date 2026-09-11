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

# ========== 6. 分线路运价数据（下载图片 + OCR识别） ==========
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

    # 2. 下载图片
    article_resp = requests.get(latest_url, headers=headers, timeout=30)
    article_resp.encoding = "utf-8"
    article_soup = BeautifulSoup(article_resp.text, "html.parser")

    images = article_soup.find_all("img")
    for i, img in enumerate(images):
        src = img.get("src", "") or img.get("data-src", "")
        if not src:
            continue
        full_url = urljoin(latest_url, src)
        if i + 1 == 5:  # 第5张是表1
            try:
                img_resp = requests.get(full_url, headers=headers, timeout=30)
                if img_resp.status_code == 200:
                    table_img_path = "data/route_images/route_table_5.png"
                    with open(table_img_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"  ✅ 表1图片已下载: {table_img_path}")
            except Exception as e:
                print(f"  ⚠️ 图片下载失败: {e}")

    # 3. OCR 识别
    if os.path.exists("data/route_images/route_table_5.png"):
        print("  正在 OCR 识别表1...")
        from rapidocr_onnxruntime import RapidOCR

        engine = RapidOCR()
        result, _ = engine("data/route_images/route_table_5.png")

        if not result:
            raise Exception("OCR 未识别到任何文字")

        # 提取文本块及中心坐标
        blocks = []
        for box, text, score in result:
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            blocks.append({
                "text": text.strip(),
                "x": sum(xs) / 4,
                "y": sum(ys) / 4,
            })

        # 按 y 坐标分组为行
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

        # 构建 DataFrame
        table_data = [[cell["text"] for cell in row] for row in rows]
        # 补齐列数
        max_cols = max(len(r) for r in table_data) if table_data else 0
        table_data = [r + [""] * (max_cols - len(r)) for r in table_data]

        route_df = pd.DataFrame(table_data)
        f = "data/route_price.csv"
        route_df.to_csv(f, index=False, encoding='utf-8-sig')
        success_files.append(f)

        print(f"✅ 分线路数据 OCR 成功，共 {len(route_df)} 行")
        print(route_df.to_string())
    else:
        print("⚠️ 表1图片未下载，跳过 OCR")

except Exception as e:
    print(f"❌ 分线路数据获取失败: {e}")
