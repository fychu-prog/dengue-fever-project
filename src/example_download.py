"""
登革熱資料下載範例
示範如何使用 download_dengue_data.py 中的函數
"""

from download_dengue_data import download_from_url, get_dengue_data_info
from pathlib import Path

# 設定資料儲存路徑
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def example_download():
    """
    範例：如何下載登革熱資料
    """
    print("=== 登革熱資料下載範例 ===\n")
    
    # 1. 顯示資料來源資訊
    get_dengue_data_info()
    
    # 2. 如果您有直接的資料下載連結，可以使用以下方式下載
    # 範例（請替換為實際的資料連結）：
    # download_url = "https://example.com/dengue_data.csv"
    # download_from_url(download_url, filename="dengue_latest.csv")
    
    print("\n=== 使用說明 ===")
    print("1. 前往政府資料開放平台或疾病管制署網站")
    print("2. 找到登革熱資料的下載連結")
    print("3. 使用 download_from_url() 函數下載")
    print("\n範例程式碼：")
    print("  from download_dengue_data import download_from_url")
    print("  download_from_url('資料連結', filename='dengue_data.csv')")


if __name__ == "__main__":
    example_download()

