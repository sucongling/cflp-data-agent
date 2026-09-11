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

# ========== 6. 分线路运价数据（下载表格图片） ==========
try:
    print("\n[6/6] 获取分线路运价数据（下载图片）...")
    import re
    import requests
    from bs4 import BeautifulSoup
    import shutil

    headers = {"User-Agent": "Mozilla/5.0"}

    # 清空旧的图片文件夹
    if os.path.exists("data/route_images"):
        shutil.rmtree("data/route_images")
    os.makedirs("data/route_images", exist_ok=True)

    # 1. 获取中物联周报列表页
    list_url = "http://www.chinawuliu.com.cn/zt/jtbzwltj/list.shtml"
    resp = requests.get(list_url, headers=headers, timeout=30)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # 2. 找到最新周报链接
    links = soup.find_all("a", string=re.compile(r"中国公路物流运价周指数报告"))
    if not links:
        raise Exception("未找到周报链接")

    latest_url = links[0].get("href")
    if not latest_url.startswith("http"):
        latest_url = "http://www.chinawuliu.com.cn" + latest_url
    print(f"  最新周报: {latest_url}")

    # 3. 进入文章页，找所有图片
    article_resp = requests.get(latest_url, headers=headers, timeout=30)
    article_resp.encoding = "utf-8"
    article_soup = BeautifulSoup(article_resp.text, "html.parser")

    images = article_soup.find_all("img")
    print(f"  文章页中找到 {len(images)} 张图片")

    # 4. 下载图片
    downloaded = 0
    for i, img in enumerate(images):
        src = img.get("src", "")
        if not src:
            continue
        # 补全相对路径
        if not src.startswith("http"):
            if src.startswith("/"):
                src = "http://www.chinawuliu.com.cn" + src
            else:
                src = "http://www.chinawuliu.com.cn/lhhzq/202608/21/" + src

        try:
            img_resp = requests.get(src, headers=headers, timeout=30)
            if img_resp.status_code == 200:
                # 只保留 png/jpg 图片
                ext = os.path.splitext(src)[1].lower()
                if ext not in [".png", ".jpg", ".jpeg", ".gif"]:
                    ext = ".png"
                filename = f"data/route_images/route_table_{i+1}{ext}"
                with open(filename, "wb") as f:
                    f.write(img_resp.content)
                downloaded += 1
                print(f"    ✅ 下载: {filename}  (源: {src})")
        except Exception as e:
            print(f"    ⚠️ 下载失败: {src} - {e}")

    if downloaded > 0:
        f = "data/route_images/"
        success_files.append(f)
        print(f"✅ 分线路图片下载成功，共 {downloaded} 张")
    else:
        print("⚠️ 未下载到任何图片")

except Exception as e:
    print(f"❌ 分线路数据获取失败: {e}")
