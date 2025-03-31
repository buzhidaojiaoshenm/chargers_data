"""
API工厂模块

用于创建和管理不同的API客户端，如高德地图API等。
支持通过配置动态选择API类型和版本。
"""
import importlib
import os
from typing import Dict, Any, Optional, Type


class APIFactory:
    """
    API工厂类
    
    用于创建和管理不同的API客户端实例。
    """
    
    # 已注册的API类型
    _registered_apis = {
        'gaode': ('src.api.gaode', 'GaodeAPI'),
        'gaode2': ('src.api.gaode2', 'GaodeAPI2'),
        # 可以在这里添加更多API类型
    }
    
    @classmethod
    def get_api_instance(cls, api_type: str, api_key: str = None, **kwargs) -> Any:
        """
        获取指定类型的API实例
        
        Args:
            api_type: API类型名称
            api_key: API密钥
            **kwargs: 传递给API构造函数的其他参数
            
        Returns:
            API实例
            
        Raises:
            ValueError: 如果API类型未注册
            ImportError: 如果无法导入API模块
        """
        if api_type not in cls._registered_apis:
            raise ValueError(f"未注册的API类型: {api_type}")
        
        module_path, class_name = cls._registered_apis[api_type]
        
        try:
            module = importlib.import_module(module_path)
            api_class = getattr(module, class_name)
            
            # 创建API实例
            if api_key:
                return api_class(api_key, **kwargs)
            else:
                # 尝试从配置文件中加载API密钥
                try:
                    # 优先尝试从api.token加载
                    api_token_path = os.path.join('config', 'api.token')
                    if os.path.exists(api_token_path):
                        with open(api_token_path, 'r') as f:
                            key = f.read().strip()
                            return api_class(key, **kwargs)
                    
                    # 如果api.token不存在，尝试根据API类型加载特定token
                    base_api_type = api_type.split('_')[0]  # 提取基本API名称
                    specific_token_path = os.path.join('config', f'{base_api_type}.token')
                    if os.path.exists(specific_token_path):
                        with open(specific_token_path, 'r') as f:
                            key = f.read().strip()
                            return api_class(key, **kwargs)
                    
                    raise FileNotFoundError(f"未找到API密钥文件: {api_token_path} 或 {specific_token_path}")
                except FileNotFoundError as e:
                    raise ValueError(f"未提供API密钥，且无法从配置中加载密钥: {str(e)}")
                
        except ImportError as e:
            raise ImportError(f"无法导入API模块 {module_path}: {str(e)}")
        except AttributeError:
            raise ImportError(f"API模块 {module_path} 中没有类 {class_name}")
    
    @classmethod
    def register_api(cls, api_type: str, module_path: str, class_name: str) -> None:
        """
        注册新的API类型
        
        Args:
            api_type: API类型名称
            module_path: API模块路径
            class_name: API类名
        """
        cls._registered_apis[api_type] = (module_path, class_name)
        print(f"已注册API类型: {api_type} -> {module_path}.{class_name}")
    
    @classmethod
    def get_registered_apis(cls) -> Dict[str, tuple]:
        """
        获取所有已注册的API类型
        
        Returns:
            已注册的API类型字典
        """
        return cls._registered_apis.copy()


def get_api_for_task_group(group_config: Dict[str, Any]) -> Any:
    """
    根据任务组配置获取对应的API实例
    
    Args:
        group_config: 任务组配置字典
        
    Returns:
        API实例
        
    Raises:
        ValueError: 如果配置中没有指定API类型
    """
    api_type = group_config.get('api')
    if not api_type:
        raise ValueError("任务组配置中未指定API类型")
    
    # 获取API实例
    return APIFactory.get_api_instance(api_type)


# 测试函数
def test_api_factory():
    """测试API工厂"""
    try:
        # 注册测试API
        APIFactory.register_api('test_api', 'src.utils.api_factory', 'TestAPI')
        
        # 获取已注册的API类型
        apis = APIFactory.get_registered_apis()
        print("已注册的API类型:")
        for api_type, (module, cls) in apis.items():
            print(f"  {api_type}: {module}.{cls}")
        
        print("\n注意: 此测试将尝试导入已注册的API模块，但不会实际创建实例")
    except Exception as e:
        print(f"测试时出错: {str(e)}")


# 测试用API类
class TestAPI:
    """测试用API类"""
    def __init__(self, api_key, **kwargs):
        self.api_key = api_key
        self.kwargs = kwargs
        
    def search(self, **params):
        """测试搜索方法"""
        return {"status": "ok", "message": "This is a test API", "params": params}


if __name__ == "__main__":
    # 如果直接运行该模块，则执行测试
    test_api_factory() 