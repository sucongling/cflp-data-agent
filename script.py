import akshare as ak
import pandas as pd
from datetime import datetime
import os

# 创建 data 文件夹
os.makedirs("data", exist_ok=True)

print("=" * 50)
print("开始测试 akshare 接口...")
print("=" * 50)

# 测试1：运价指数
try:
    print("\n[测试] 获取公路物流运价指数 (月指数)...")
    df_price = ak.index_price_cflp(symbol="月指数")
    print(f"✅ 成功！数据条数: {len(df_price)}")
    print(df_price.tail())
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试2：运量指数
try:
    print("\n[测试] 获取公路物流运量指数 (月指数)...")
    df_volume = ak.index_volume_cflp(symbol="月指数")
    print(f"✅ 成功！数据条数: {len(df_volume)}")
    print(df_volume.tail())
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试3：PMI（备选）
try:
    print("\n[测试] 获取制造业PMI...")
    df_pmi = ak.macro_china_pmi()
    print(f"✅ 成功！数据条数: {len(df_pmi)}")
    print(df_pmi.tail())
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
