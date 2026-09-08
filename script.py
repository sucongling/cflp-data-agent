import akshare as ak
import pandas as pd
from datetime import datetime

# 1. 获取中国公路物流运价指数（月指数）
print("正在获取公路物流运价指数...")
df_price = ak.index_price_cflp(symbol="月指数")

# 2. 获取中国公路物流运量指数（月指数）
print("正在获取公路物流运量指数...")
df_volume = ak.index_volume_cflp(symbol="月指数")

# 3. 打印数据摘要
print("\n--- 公路物流运价指数 (月) ---")
print(df_price.tail())
print("\n--- 公路物流运量指数 (月) ---")
print(df_volume.tail())

# 4. 保存为CSV文件，文件名带时间戳
timestamp = datetime.now().strftime("%Y%m%d")
df_price.to_csv(f"data/price_index_{timestamp}.csv", index=False)
df_volume.to_csv(f"data/volume_index_{timestamp}.csv", index=False)

print(f"\n✅ 数据已保存，时间戳: {timestamp}")