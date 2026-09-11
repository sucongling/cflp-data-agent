import akshare as ak
import pandas as pd
from datetime import datetime
import os

# 创建 data 文件夹
os.makedirs("data", exist_ok=True)

print("=" * 60)
print(f"开始采集数据: {datetime.now().isoformat()}")
print("=" * 60)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
success_files = []

# ========== 1. 月度整体运价指数 ==========
try:
    print("\n[1/6] 获取公路物流运价指数（月指数）...")
    df_price = ak.index_price_cflp(symbol="月指数")
    f = f"data/price_index_{timestamp}.csv"
    df_price.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df_price)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# ========== 2. 月度整体运量指数 ==========
try:
    print("\n[2/6] 获取公路物流运量指数（月指数）...")
    df_volume = ak.index_volume_cflp(symbol="月指数")
    f = f"data/volume_index_{timestamp}.csv"
    df_volume.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df_volume)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# ========== 3. 周度整体运价指数 ==========
try:
    print("\n[3/6] 获取公路物流运价指数（周指数）...")
    df_week = ak.index_price_cflp(symbol="周指数")
    f = f"data/price_week_{timestamp}.csv"
    df_week.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df_week)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# ========== 4. 制造业PMI ==========
try:
    print("\n[4/6] 获取制造业PMI...")
    df_pmi = ak.macro_china_pmi()
    f = f"data/pmi_{timestamp}.csv"
    df_pmi.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df_pmi)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# ========== 5. 综合PMI（含制造业/非制造业/综合） ==========
try:
    print("\n[5/6] 获取综合PMI产出指数...")
    df_pmi_monthly = ak.macro_china_pmi_monthly()
    f = f"data/pmi_composite_{timestamp}.csv"
    df_pmi_monthly.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df_pmi_monthly)} 条")
    print(df_pmi_monthly.tail(3))
except Exception as e:
    print(f"❌ 失败: {e}")

# ========== 6. 物流景气指数（作为电商物流的补充） ==========
try:
    print("\n[6/6] 获取物流景气指数...")
    df_lpi = ak.macro_china_lpi_index()
    f = f"data/lpi_{timestamp}.csv"
    df_lpi.to_csv(f, index=False, encoding='utf-8-sig')
    success_files.append(f)
    print(f"✅ 成功，共 {len(df_lpi)} 条")
except Exception as e:
    print(f"❌ 失败: {e}")

# ========== 生成成功标记文件 ==========
print("\n" + "=" * 60)
print(f"采集完成，共成功 {len(success_files)} 项")
for f in success_files:
    print(f"  ✅ {f}")
print("=" * 60)

with open("data/_SUCCESS", "w", encoding="utf-8") as fp:
    fp.write(f"Scrape completed at {datetime.now().isoformat()}\n")
    fp.write(f"Successful files ({len(success_files)}):\n")
    for f in success_files:
        fp.write(f"  - {f}\n")
