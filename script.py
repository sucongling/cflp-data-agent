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

# ========== 6. 分线路运价数据 ==========
try:
    print("\n[6/6] 获取分线路运价数据...")
    import re
    import requests
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0"}

    # 使用中物联官网的周报列表页
    list_url = "http://www.chinawuliu.com.cn/zt/jtbzwltj/list.shtml"
    resp = requests.get(list_url, headers=headers, timeout=30)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # 调试：打印页面中所有链接的文本和href
    print("  调试：页面中找到的链接：")
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if text and ("周指数" in text or "运价" in text):
            print(f"    - 文本: {text} | href: {a['href']}")

    # 查找包含“中国公路物流运价周指数报告”的链接
    links = soup.find_all("a", string=re.compile(r"中国公路物流运价周指数报告"))
    if links:
        latest_url = links[0].get("href")
        if not latest_url.startswith("http"):
            # 处理相对路径
            if latest_url.startswith("/"):
                latest_url = "http://www.chinawuliu.com.cn" + latest_url
            else:
                latest_url = "http://www.chinawuliu.com.cn/zt/jtbzwltj/" + latest_url
        print(f"  找到周报链接: {latest_url}")

        article_resp = requests.get(latest_url, headers=headers, timeout=30)
        article_resp.encoding = "utf-8"
        article_soup = BeautifulSoup(article_resp.text, "html.parser")

        # 调试：打印文章页中所有表格
        tables = article_soup.find_all("table")
        print(f"  调试：文章页中找到 {len(tables)} 个表格")
        for i, table in enumerate(tables):
            rows = table.find_all("tr")
            print(f"    表格{i+1}: {len(rows)} 行")

        if tables:
            # 尝试取第一个表格（通常是表1）
            route_df = pd.read_html(str(tables[0]))[0]
            f = "data/route_price.csv"
            route_df.to_csv(f, index=False, encoding='utf-8-sig')
            success_files.append(f)
            print(f"✅ 分线路数据获取成功，共 {len(route_df)} 行")
        else:
            print("⚠️ 未找到HTML表格")
    else:
        print("⚠️ 未找到周报链接")
except Exception as e:
    print(f"❌ 分线路数据获取失败: {e}")
