import json
import os
from datetime import datetime

from src.api.gaode import GaodeAPI


def load_api_key():
    """加载API密钥"""
    with open('config/api.token', 'r') as f:
        return f.read().strip()


def main():
    # 加载API密钥
    api_key = load_api_key()
    
    # 初始化API客户端
    api = GaodeAPI(key=api_key)
    
    try:
        # 获取POI数据
        print("正在获取POI数据...")
        poi_list = api.get_poi_total_list()
        
        # 创建输出文件名（包含时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'data/poi_data_{timestamp}.json'
        
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        # 保存数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(poi_list, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {output_file}")
        print(f"共获取到 {len(poi_list)} 条POI数据")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 