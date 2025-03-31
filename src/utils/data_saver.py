"""
数据保存模块

负责将API返回的数据保存到不同格式的文件中，如CSV和JSON。
支持自定义输出目录和文件名。
"""
import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class DataSaver:
    """
    数据保存器
    
    用于将API返回的数据保存到不同格式的文件中。
    """
    
    def __init__(self, global_settings: Dict = None):
        """
        初始化数据保存器
        
        Args:
            global_settings: 全局设置字典
        """
        self.global_settings = global_settings or {}
        
        # 设置输出目录和时间格式
        self.base_output_dir = self.global_settings.get('output_dir', 'data')
        self.add_timestamp = self.global_settings.get('add_timestamp', True)
        self.time_format = self.global_settings.get('time_format', '%Y%m%d_%H%M')
        
        # 创建时间戳子目录
        self.timestamp = datetime.now().strftime(self.time_format)
        self.output_dir = os.path.join(self.base_output_dir, self.timestamp)
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_data(self, data: List[Dict], output_config: Dict, task_name: str = None) -> Dict[str, str]:
        """
        保存数据到指定格式的文件
        
        Args:
            data: 要保存的数据列表
            output_config: 输出配置字典，包含文件名前缀和格式列表
            task_name: 任务名称，用于日志输出
            
        Returns:
            已保存文件的路径字典，键为格式，值为文件路径
        """
        if not data:
            print(f"警告: 没有数据要保存 (任务: {task_name or '未命名'})")
            return {}
        
        # 准备文件名
        filename_prefix = output_config.get('filename_prefix', 'poi_data')
        formats = output_config.get('formats', ['csv'])
        
        # 添加文件名时间戳
        file_timestamp = ''
        if self.add_timestamp:
            file_timestamp = f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存不同格式的文件
        saved_files = {}
        for fmt in formats:
            filename = os.path.join(self.output_dir, f"{filename_prefix}{file_timestamp}.{fmt}")
            if fmt.lower() == 'csv':
                self._save_to_csv(data, filename)
            elif fmt.lower() == 'json':
                self._save_to_json(data, filename)
            else:
                print(f"警告: 不支持的文件格式: {fmt}")
                continue
            
            saved_files[fmt] = filename
        
        return saved_files
    
    def _save_to_csv(self, data: List[Dict], filename: str) -> None:
        """
        保存数据到CSV文件
        
        Args:
            data: 要保存的数据列表
            filename: 输出文件名
        """
        try:
            # 确定所有字段名
            all_fields = set()
            for item in data:
                all_fields.update(self._flatten_dict(item).keys())
            
            # 将所有字段排序，确保一致的列顺序
            fields = sorted(list(all_fields))
            
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                
                for item in data:
                    # 扁平化嵌套字典
                    flat_item = self._flatten_dict(item)
                    writer.writerow(flat_item)
            
            print(f"数据已保存到CSV文件: {filename}")
        except Exception as e:
            print(f"保存CSV文件时出错: {str(e)}")
    
    def _save_to_json(self, data: List[Dict], filename: str) -> None:
        """
        保存数据到JSON文件
        
        Args:
            data: 要保存的数据列表
            filename: 输出文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"数据已保存到JSON文件: {filename}")
        except Exception as e:
            print(f"保存JSON文件时出错: {str(e)}")
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """
        将嵌套字典扁平化，便于保存到CSV
        
        Args:
            d: 要扁平化的字典
            parent_key: 父键名
            sep: 键名分隔符
            
        Returns:
            扁平化后的字典
        """
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                # 递归处理嵌套字典
                items.update(self._flatten_dict(v, new_key, sep))
            elif isinstance(v, list):
                # 处理列表类型数据
                if all(isinstance(x, dict) for x in v):
                    # 如果列表中都是字典，则记录数量和第一个元素的内容
                    items[new_key + '_count'] = len(v)
                    if v:
                        items.update(self._flatten_dict(v[0], new_key + '_0', sep))
                else:
                    # 其他类型的列表，转为字符串
                    items[new_key] = ';'.join(str(x) for x in v)
            else:
                # 原始类型，直接保存
                items[new_key] = v
        
        return items


def save_to_file(data: List[Dict], output_path: str, format: str = 'json') -> bool:
    """
    简单的辅助函数，用于直接保存数据到文件
    
    Args:
        data: 要保存的数据
        output_path: 输出文件路径
        format: 文件格式，支持'json'和'csv'
        
    Returns:
        保存是否成功
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format.lower() == 'csv':
            if not data:
                return False
                
            # 确定所有字段名
            all_fields = set()
            for item in data:
                all_fields.update(item.keys())
            
            fields = sorted(list(all_fields))
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for item in data:
                    writer.writerow({k: item.get(k, '') for k in fields})
        else:
            print(f"不支持的文件格式: {format}")
            return False
        
        return True
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")
        return False


# 测试函数
def test_saver():
    """测试数据保存器"""
    # 测试数据
    test_data = [
        {
            "id": "poi_001",
            "name": "测试充电站1",
            "location": "121.123,31.456",
            "business": {
                "open_time": "09:00-22:00",
                "rating": 4.8
            },
            "photos": [
                {"url": "http://example.com/photo1.jpg", "title": "外观"},
                {"url": "http://example.com/photo2.jpg", "title": "内部"}
            ]
        },
        {
            "id": "poi_002",
            "name": "测试充电站2",
            "location": "121.234,31.567",
            "business": {
                "open_time": "24小时",
                "rating": 4.5
            },
            "children": [
                {"id": "sub_001", "name": "充电桩1"},
                {"id": "sub_002", "name": "充电桩2"}
            ]
        }
    ]
    
    # 测试配置
    global_settings = {
        "output_dir": "data/test",
        "add_timestamp": True
    }
    
    output_config = {
        "filename_prefix": "test_data",
        "formats": ["csv", "json"]
    }
    
    # 创建保存器并保存数据
    saver = DataSaver(global_settings)
    saved_files = saver.save_data(test_data, output_config, "测试任务")
    
    print("\n测试完成！")
    print("已保存文件:")
    for fmt, path in saved_files.items():
        print(f"  {fmt}: {path}")


if __name__ == "__main__":
    # 如果直接运行该模块，则执行测试
    test_saver() 