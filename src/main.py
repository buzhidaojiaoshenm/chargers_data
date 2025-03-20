import csv
import json
import os
from datetime import datetime
from typing import List, Dict

from src.api.gaode import GaodeAPI
from src.utils.excel_reader import CodeReader


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


def collect_district_data(api: GaodeAPI, 
                         district_info: Dict,
                         poi_types: List[str]) -> List[Dict]:
    """
    收集特定区县的POI数据
    
    Args:
        api: GaodeAPI实例
        district_info: 区县信息
        poi_types: POI类型代码列表
    
    Returns:
        该区县的POI数据列表
    """
    print(f"正在获取{district_info['name']}的数据...")
    
    search_params = {
        'keywords': '充电站|充电桩|充电设施',
        'types': '|'.join(poi_types),
        'city': district_info['adcode'],
        'city_limit': True,
        'extensions': 'all'
    }
    
    return api.get_poi_total_list(
        search_type='keywords',
        **search_params
    )


def main():
    # 加载API密钥
    api_key = load_api_key()
    
    # 初始化API客户端和代码读取器
    api = GaodeAPI(key=api_key)
    reader = CodeReader()
    
    try:
        # 获取北京市所有区县代码
        district_codes = reader.get_district_codes('北京市')
        # 获取充电设施相关的POI类型代码
        poi_types = reader.get_poi_types('汽车服务', '充电站')
        
        print(f"找到 {len(district_codes)} 个区县")
        print(f"找到 {len(poi_types)} 个POI类型")
        
        # 存储所有数据
        all_pois = []
        
        # 遍历每个区县
        for adcode in district_codes:
            district_info = reader.get_district_info(adcode)
            district_pois = collect_district_data(api, district_info, poi_types)
            
            if district_pois:
                # 添加区县信息到每条记录
                for poi in district_pois:
                    poi['district_name'] = district_info['name']
                    poi['district_adcode'] = district_info['adcode']
                
                all_pois.extend(district_pois)
                print(f"{district_info['name']}找到 {len(district_pois)} 个充电设施")
            else:
                print(f"{district_info['name']}未找到充电设施")
        
        if not all_pois:
            print("警告：未获取到任何数据")
            return 1
            
        # 创建输出文件名（包含时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f'data/charging_stations_{timestamp}.csv'
        json_file = f'data/charging_stations_{timestamp}.json'
        
        # 保存为CSV格式
        save_to_csv(all_pois, csv_file)
        print(f"CSV数据已保存到: {csv_file}")
        
        # 同时保存原始JSON数据
        os.makedirs('data', exist_ok=True)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_pois, f, ensure_ascii=False, indent=2)
        print(f"JSON数据已保存到: {json_file}")
        
        print(f"共获取到 {len(all_pois)} 个充电设施位置")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 
