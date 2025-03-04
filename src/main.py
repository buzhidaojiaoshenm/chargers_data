import csv
import json
import os
from datetime import datetime

from src.api.gaode import GaodeAPI


def load_api_key():
    """加载API密钥"""
    with open('config/api.token', 'r') as f:
        return f.read().strip()


def save_to_csv(pois: list, filename: str):
    """
    将POI数据保存为CSV文件
    
    Args:
        pois: POI数据列表
        filename: 输出文件名
    """
    if not pois:
        return
    
    # 定义要提取的字段
    fields = [
        'id', 'name', 'type', 'typecode', 'address', 'pname', 'cityname',
        'adname', 'location', 'tel', 'business_area', 'biz_ext.open_time',
        'biz_ext.rating', 'biz_ext.cost'
    ]
    
    # 创建目录
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # 写入表头
        writer.writerow(fields)
        
        # 写入数据
        for poi in pois:
            row = []
            for field in fields:
                if '.' in field:
                    # 处理嵌套字段
                    parent, child = field.split('.')
                    value = poi.get(parent, {}).get(child, '')
                else:
                    value = poi.get(field, '')
                row.append(value)
            writer.writerow(row)


def main():
    # 加载API密钥
    api_key = load_api_key()
    
    # 初始化API客户端
    api = GaodeAPI(key=api_key)
    
    try:
        # 设置搜索参数
        search_params = {
            'keywords': '充电站|充电桩',
            'types': '011100|011102|011103|073000|073001|073002',  # 使用原始代码中的类型代码
            'city': '北京',  # 改用 city 参数
            'city_limit': True,
            'extensions': 'all'
        }
        
        print("正在获取北京市充电设施数据...")
        poi_list = api.get_poi_total_list(
            search_type='keywords',
            **search_params
        )
        
        if not poi_list:
            print("警告：未获取到任何数据，请检查搜索参数")
            return 1
            
        # 创建输出文件名（包含时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/charging_stations_{timestamp}.csv'
        json_file = f'data/charging_stations_{timestamp}.json'
        
        # 保存为CSV格式
        save_to_csv(poi_list, csv_file)
        print(f"CSV数据已保存到: {csv_file}")
        
        # 同时保存原始JSON数据
        os.makedirs('data', exist_ok=True)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(poi_list, f, ensure_ascii=False, indent=2)
        print(f"JSON数据已保存到: {json_file}")
        
        print(f"共获取到 {len(poi_list)} 个充电设施位置")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 