"""
配置文件解析模块

负责解析search_config.json配置文件，并返回结构化的任务列表和全局设置。
支持多种API和多种搜索方式的配置。
"""
import os
import json
from typing import Dict, List, Any, Tuple, Optional


class ConfigParser:
    """
    配置文件解析器
    
    用于解析search_config.json文件，支持多种API和多种搜索方式。
    """
    
    def __init__(self, config_path: str = 'config/search_config.json'):
        """
        初始化配置解析器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = {}
        self.task_groups = {}
        self.global_settings = {}
    
    def load_config(self) -> Dict:
        """
        加载配置文件
        
        Returns:
            配置文件内容
        
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式错误
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                return self.config
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"配置文件 {self.config_path} 格式错误")
    
    def parse_config(self) -> Tuple[Dict[str, List[Dict]], Dict]:
        """
        解析配置文件，获取任务组和全局设置
        
        Returns:
            包含多个任务组和全局设置的元组 (task_groups, global_settings)
        """
        if not self.config:
            self.load_config()
        
        # 获取全局设置
        self.global_settings = self.config.get('global_settings', {})
        
        # 获取任务组
        task_groups = self.config.get('task_groups', {})
        if not task_groups:
            # 向后兼容，如果没有task_groups，则将顶层tasks作为默认组
            default_tasks = self.config.get('tasks', [])
            if default_tasks:
                task_groups = {
                    'default': {
                        'api': 'gaode2',  # 默认使用高德API 2.0版本
                        'tasks': default_tasks
                    }
                }
        
        self.task_groups = task_groups
        return self.task_groups, self.global_settings
    
    def get_task_group(self, group_name: str) -> Optional[Dict]:
        """
        获取指定名称的任务组
        
        Args:
            group_name: 任务组名称
            
        Returns:
            任务组配置，如果不存在则返回None
        """
        if not self.task_groups:
            self.parse_config()
        
        return self.task_groups.get(group_name)
    
    def get_all_task_groups(self) -> Dict[str, Dict]:
        """
        获取所有任务组
        
        Returns:
            所有任务组的字典
        """
        if not self.task_groups:
            self.parse_config()
        
        return self.task_groups
    
    def get_global_settings(self) -> Dict:
        """
        获取全局设置
        
        Returns:
            全局设置字典
        """
        if not self.global_settings:
            self.parse_config()
        
        return self.global_settings


def load_api_key(api_name: str = 'api') -> str:
    """
    加载指定API的密钥
    
    Args:
        api_name: API名称，默认为'api'
        
    Returns:
        API密钥
        
    Raises:
        FileNotFoundError: API密钥文件不存在
    """
    token_path = f'config/{api_name}.token'
    try:
        with open(token_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"API密钥文件 {token_path} 不存在，请确保该文件存在并包含有效的API密钥")


def get_default_config_template() -> Dict:
    """
    获取默认配置模板
    
    Returns:
        默认配置模板
    """
    return {
        "task_groups": {
            "gaode_v2_keywords": {
                "api": "gaode2",
                "search_method": "keywords",
                "tasks": [
                    {
                        "name": "示例关键字搜索任务",
                        "params": {
                            "keywords": "充电站|充电桩|充电设施",
                            "types": "011100|011101|011102|011103",
                            "region": "310101",
                            "city_limit": True,
                            "show_fields": "children,business,indoor,navi,photos",
                            "children": 1,
                            "page_size": 25
                        },
                        "output": {
                            "filename_prefix": "example_search",
                            "formats": ["csv", "json"]
                        }
                    }
                ]
            },
            "gaode_v2_polygon": {
                "api": "gaode2",
                "search_method": "polygon",
                "tasks": [
                    {
                        "name": "示例多边形搜索任务",
                        "params": {
                            "keywords": "充电站|充电桩|充电设施",
                            "types": "011100|011101|011102|011103",
                            "polygon_grid": {
                                "center_lng": 121.472644,
                                "center_lat": 31.231706,
                                "region_radius": 5000,
                                "edge_length": 500,
                                "num_sides": 6
                            },
                            "show_fields": "children,business,indoor,navi,photos",
                            "children": 1,
                            "page_size": 25
                        },
                        "output": {
                            "filename_prefix": "example_polygon_search",
                            "formats": ["csv", "json"]
                        }
                    }
                ]
            }
        },
        "global_settings": {
            "output_dir": "data",
            "add_timestamp": True,
            "time_format": "%Y%m%d_%H%M",
            "max_retries": 3,
            "retry_delay": 1.0,
            "log_level": "info"
        }
    }


def create_default_config(config_path: str = 'config/search_config.json') -> None:
    """
    创建默认配置文件
    
    Args:
        config_path: 配置文件路径
    """
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(get_default_config_template(), f, ensure_ascii=False, indent=2)
    
    print(f"已在 {config_path} 创建默认配置文件")


# 简单的测试函数
def test_parser():
    """测试配置解析器"""
    parser = ConfigParser()
    try:
        task_groups, global_settings = parser.parse_config()
        print("配置文件解析成功!")
        print(f"全局设置: {global_settings}")
        print(f"找到 {len(task_groups)} 个任务组:")
        for group_name, group_config in task_groups.items():
            api_name = group_config.get('api', 'unknown')
            tasks = group_config.get('tasks', [])
            print(f"  任务组 '{group_name}': 使用 API '{api_name}', 包含 {len(tasks)} 个任务")
    except Exception as e:
        print(f"配置解析错误: {str(e)}")


if __name__ == "__main__":
    # 如果直接运行该模块，则执行测试
    test_parser() 