import akshare as ak
import pandas as pd
from datetime import datetime
import os

# 创建 data 文件夹
os.makedirs("data", exist_ok=True)

print("=" * 50)
print("开始获取数据...")
print("=" * 50)

# 1. 获取运价指数
print("\n获取公路物流运价指数...")
df_price = ak.index_price_cflp(symbol="月指数")
print(f"✅ 运价指数获取成功，共 {len(df_price)} 条")

# 2. 获取运量指数
print("\n获取公路物流运量指数...")
df_volume = ak.index_volume_cflp(symbol="月指数")
print(f"✅ 运量指数获取成功，共 {len(df_volume)} 条")

# 3. 获取制造业 PMI
print("\n获取制造业 PMI...")
df_pmi = ak.macro_china_pmi()
print(f"✅ PMI 获取成功，共 {len(df_pmi)} 条")

# 4. 保存文件
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
price_file = f"data/price_index_{timestamp}.csv"
volume_file = f"data/volume_index_{timestamp}.csv"
pmi_file = f"data/pmi_{timestamp}.csv"

df_price.to_csv(price_file, index=False, encoding='utf-8-sig')
df_volume.to_csv(volume_file, index=False, encoding='utf-8-sig')
df_pmi.to_csv(pmi_file, index=False, encoding='utf-8-sig')

# 5. 强制创建一个文件，确保有变化可以提交
with open("data/_SUCCESS", "w") as f:
    f.write(f"Scrape completed at {datetime.now().isoformat()}\n")
    f.write(f"Files created: {price_file}, {volume_file}, {pmi_file}\n")

print("\n" + "=" * 50)
print("✅ 数据已保存：")
print(f"  - {price_file}")
print(f"  - {volume_file}")
print(f"  - {pmi_file}")
print("=" * 50)
