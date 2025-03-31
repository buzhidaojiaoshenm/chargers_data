"""
任务处理模块

用于执行各种不同类型的API任务，处理API调用、数据收集和错误处理。
"""
import time
import logging
from typing import Dict, List, Any, Callable, Optional

from src.utils.api_factory import get_api_for_task_group
from src.utils.data_saver import DataSaver
from src.utils.logger import Logger
from src.utils.polygon_grid import generate_polygon_grid, coords_to_polygon_param


class TaskProcessor:
    """
    任务处理器
    
    用于执行各种不同类型的API任务，处理API调用、数据收集和错误处理。
    """
    
    def __init__(self, global_settings: Dict = None):
        """
        初始化任务处理器
        
        Args:
            global_settings: 全局设置字典
        """
        self.global_settings = global_settings or {}
        
        # 初始化日志记录器
        self.logger = Logger.get_logger(
            name='task_processor',
            log_level=self.global_settings.get('log_level', 'info'),
            log_to_file=self.global_settings.get('log_to_file', False),
            log_dir=self.global_settings.get('log_dir', 'logs')
        )
        
        # 初始化数据保存器
        self.data_saver = DataSaver(self.global_settings)
        
        # 设置重试参数
        self.max_retries = self.global_settings.get('max_retries', 3)
        self.retry_delay = self.global_settings.get('retry_delay', 1.0)
        
        # 注册任务处理方法
        self.task_handlers = {
            'gaode2': {
                'keywords': self._handle_keywords_search,
                'around': self._handle_around_search,
                'polygon': self._handle_polygon_search,
                'id': self._handle_id_search
            }
            # 可以在这里添加更多API和搜索方法的处理函数
        }
    
    def process_task_group(self, group_name: str, group_config: Dict) -> Dict:
        """
        处理单个任务组
        
        Args:
            group_name: 任务组名称
            group_config: 任务组配置
            
        Returns:
            处理结果统计
        """
        self.logger.info(f"开始处理任务组: {group_name}")
        
        # 获取API类型和搜索方法
        api_type = group_config.get('api')
        search_method = group_config.get('search_method')
        
        if not api_type:
            self.logger.error(f"任务组 {group_name} 未指定API类型")
            return {'status': 'error', 'message': '未指定API类型'}
        
        # 获取任务列表
        tasks = group_config.get('tasks', [])
        if not tasks:
            self.logger.warning(f"任务组 {group_name} 没有任务")
            return {'status': 'warning', 'message': '没有任务'}
        
        # 获取API实例
        try:
            api = get_api_for_task_group(group_config)
        except Exception as e:
            self.logger.error(f"获取API实例失败: {str(e)}")
            return {'status': 'error', 'message': f'获取API实例失败: {str(e)}'}
        
        # 处理每个任务
        results = []
        for task_index, task in enumerate(tasks):
            task_name = task.get('name', f'Task_{task_index+1}')
            self.logger.info(f"处理任务: {task_name} ({task_index + 1}/{len(tasks)})")
            
            # 尝试获取任务处理方法
            handler = self._get_task_handler(api_type, search_method)
            if not handler:
                self.logger.error(f"不支持的API类型或搜索方法: {api_type}/{search_method}")
                results.append({
                    'task_name': task_name,
                    'status': 'error',
                    'message': f'不支持的API类型或搜索方法: {api_type}/{search_method}'
                })
                continue
            
            # 执行任务
            try:
                task_result = handler(api, task)
                results.append({
                    'task_name': task_name,
                    'status': 'success',
                    **task_result
                })
            except Exception as e:
                self.logger.error(f"执行任务 {task_name} 失败: {str(e)}")
                results.append({
                    'task_name': task_name,
                    'status': 'error',
                    'message': str(e)
                })
        
        # 返回任务组处理结果
        return {
            'group_name': group_name,
            'api_type': api_type,
            'search_method': search_method,
            'total_tasks': len(tasks),
            'successful_tasks': sum(1 for r in results if r['status'] == 'success'),
            'task_results': results
        }
    
    def _get_task_handler(self, api_type: str, search_method: str) -> Optional[Callable]:
        """
        获取任务处理方法
        
        Args:
            api_type: API类型
            search_method: 搜索方法
            
        Returns:
            处理方法，如果不支持则返回None
        """
        api_handlers = self.task_handlers.get(api_type)
        if not api_handlers:
            return None
        
        return api_handlers.get(search_method)
    
    def _handle_keywords_search(self, api: Any, task: Dict) -> Dict:
        """
        处理关键字搜索任务
        
        Args:
            api: API实例
            task: 任务配置
            
        Returns:
            任务处理结果
        """
        # 获取任务参数
        params = task.get('params', {})
        output_config = task.get('output', {})
        
        # 确保必要参数存在
        keywords = params.get('keywords')
        if not keywords:
            raise ValueError("缺少必要参数: keywords")
        
        # 执行搜索
        self.logger.info(f"执行关键字搜索: {keywords}")
        poi_list = self._execute_api_search(
            api.search_by_keywords,
            params=params
        )
        
        # 保存结果
        saved_files = self.data_saver.save_data(poi_list, output_config, task.get('name'))
        
        return {
            'poi_count': len(poi_list),
            'saved_files': saved_files
        }
    
    def _handle_around_search(self, api: Any, task: Dict) -> Dict:
        """
        处理周边搜索任务
        
        Args:
            api: API实例
            task: 任务配置
            
        Returns:
            任务处理结果
        """
        # 获取任务参数
        params = task.get('params', {})
        output_config = task.get('output', {})
        
        # 确保必要参数存在
        location = params.get('location')
        if not location:
            raise ValueError("缺少必要参数: location")
        
        # 执行搜索
        self.logger.info(f"执行周边搜索: 中心点 {location}")
        poi_list = self._execute_api_search(
            api.search_around,
            params=params
        )
        
        # 保存结果
        saved_files = self.data_saver.save_data(poi_list, output_config, task.get('name'))
        
        return {
            'poi_count': len(poi_list),
            'saved_files': saved_files
        }
    
    def _handle_polygon_search(self, api: Any, task: Dict) -> Dict:
        """
        处理多边形区域搜索任务
        
        Args:
            api: API实例
            task: 任务配置
            
        Returns:
            任务处理结果
        """
        # 获取任务参数
        params = task.get('params', {}).copy()  # 复制以避免修改原对象
        output_config = task.get('output', {})
        
        # 检查是否使用多边形网格
        polygon_grid_config = params.pop('polygon_grid', None)
        if polygon_grid_config:
            return self._handle_polygon_grid_search(api, task, polygon_grid_config)
        
        # 确保必要参数存在
        polygon = params.get('polygon')
        if not polygon:
            raise ValueError("缺少必要参数: polygon 或 polygon_grid")
        
        # 检查是否需要对多边形坐标进行格式转换
        raw_polygon = params.pop('raw_polygon', False)  # 从params中提取并移除raw_polygon参数
        
        # 如果不是原始多边形坐标，则确保多边形参数格式正确
        if not raw_polygon:
            self.logger.info("对多边形坐标进行格式转换")
            params['polygon'] = coords_to_polygon_param(polygon)
        else:
            self.logger.info("使用原始多边形坐标，不进行转换")
        
        # 执行搜索
        self.logger.info(f"执行多边形区域搜索")
        poi_list = self._execute_api_search(
            api.search_polygon,
            params=params
        )
        
        # 保存结果
        saved_files = self.data_saver.save_data(poi_list, output_config, task.get('name'))
        
        return {
            'poi_count': len(poi_list),
            'saved_files': saved_files
        }
    
    def _handle_polygon_grid_search(self, api: Any, task: Dict, grid_config: Dict) -> Dict:
        """
        处理多边形网格搜索任务
        
        Args:
            api: API实例
            task: 任务配置
            grid_config: 网格配置
            
        Returns:
            任务处理结果
        """
        # 获取任务参数
        params = task.get('params', {}).copy()  # 复制以避免修改原对象
        output_config = task.get('output', {})
        
        # 移除网格配置，避免传递给API
        if 'polygon_grid' in params:
            del params['polygon_grid']
            
        # 检查是否使用原始多边形坐标
        raw_polygon = params.pop('raw_polygon', False)  # 从params中提取并移除raw_polygon参数
        
        # 生成多边形网格
        center_lng = grid_config.get('center_lng')
        center_lat = grid_config.get('center_lat')
        region_radius = grid_config.get('region_radius')
        edge_length = grid_config.get('edge_length')
        num_sides = grid_config.get('num_sides', 6)
        
        if not all([center_lng, center_lat, region_radius, edge_length]):
            raise ValueError("多边形网格配置不完整")
        
        polygons = generate_polygon_grid(
            center_lng=center_lng,
            center_lat=center_lat,
            region_radius=region_radius,
            edge_length=edge_length,
            num_sides=num_sides
        )
        
        self.logger.info(f"生成了 {len(polygons)} 个多边形进行搜索")
        
        # 收集所有区域的POI
        all_pois = []
        unique_poi_ids = set()  # 用于去重
        
        for idx, polygon in enumerate(polygons):
            self.logger.info(f"搜索多边形 {idx + 1}/{len(polygons)}")
            
            # 更新搜索参数
            polygon_params = params.copy()
            
            # 如果不是原始多边形坐标，则确保多边形参数格式正确
            if not raw_polygon:
                polygon_params['polygon'] = polygon  # 已经是正确格式，不需要再转换
            else:
                # 由于网格生成的多边形已经是正确格式，这里仅作记录
                self.logger.info("使用原始多边形坐标模式，但网格生成的多边形已是标准格式")
                polygon_params['polygon'] = polygon
            
            # 执行搜索
            try:
                poi_list = self._execute_api_search(
                    api.search_polygon,
                    params=polygon_params
                )
                
                # 去重添加POI
                for poi in poi_list:
                    poi_id = poi.get('id')
                    if poi_id and poi_id not in unique_poi_ids:
                        unique_poi_ids.add(poi_id)
                        all_pois.append(poi)
                
                self.logger.info(f"多边形 {idx + 1} 搜索完成，找到 {len(poi_list)} 个POI")
            except Exception as e:
                self.logger.error(f"多边形 {idx + 1} 搜索失败: {str(e)}")
        
        # 保存结果
        self.logger.info(f"网格搜索完成，共找到 {len(all_pois)} 个唯一POI")
        saved_files = self.data_saver.save_data(all_pois, output_config, task.get('name'))
        
        return {
            'polygon_count': len(polygons),
            'poi_count': len(all_pois),
            'saved_files': saved_files
        }
    
    def _handle_id_search(self, api: Any, task: Dict) -> Dict:
        """
        处理ID搜索任务
        
        Args:
            api: API实例
            task: 任务配置
            
        Returns:
            任务处理结果
        """
        # 获取任务参数
        params = task.get('params', {})
        output_config = task.get('output', {})
        
        # 确保必要参数存在
        id_list = params.get('id')
        if not id_list:
            raise ValueError("缺少必要参数: id")
        
        # 执行搜索
        self.logger.info(f"执行ID搜索: {id_list}")
        poi_list = self._execute_api_search(
            api.search_by_id,
            params=params
        )
        
        # 保存结果
        saved_files = self.data_saver.save_data(poi_list, output_config, task.get('name'))
        
        return {
            'poi_count': len(poi_list),
            'saved_files': saved_files
        }
    
    def _execute_api_search(self, search_method: Callable, params: Dict) -> List[Dict]:
        """
        执行API搜索，带有重试机制
        
        Args:
            search_method: API搜索方法
            params: 搜索参数
            
        Returns:
            搜索结果列表
        """
        # 确定是否需要多页获取数据
        search_function_name = search_method.__name__
        
        # 对于单页请求，使用原来的方法
        if search_function_name == 'search_by_id':
            retries = 0
            while retries <= self.max_retries:
                try:
                    result = search_method(**params)
                    
                    # 检查result是否为字典且包含pois键
                    if isinstance(result, dict) and 'pois' in result:
                        return result['pois']
                    elif isinstance(result, list):
                        # 如果已经是列表，则直接返回
                        return result
                    else:
                        self.logger.error(f"API返回格式错误，未找到pois列表: {type(result)}")
                        if isinstance(result, dict):
                            self.logger.debug(f"API响应：{result.keys()}")
                        raise Exception("API返回格式错误，未找到pois列表")
                except Exception as e:
                    retries += 1
                    if retries > self.max_retries:
                        raise Exception(f"达到最大重试次数，搜索失败: {str(e)}")
                    
                    self.logger.warning(f"搜索失败，正在重试 ({retries}/{self.max_retries}): {str(e)}")
                    time.sleep(self.retry_delay)
        
        # 对于需要分页获取的搜索方法，使用get_poi_total_list
        else:
            # 确定搜索类型
            search_type_mapping = {
                'search_by_keywords': 'keywords',
                'search_around': 'around',
                'search_polygon': 'polygon'
            }
            
            search_type = search_type_mapping.get(search_function_name)
            if not search_type:
                raise ValueError(f"不支持的搜索方法: {search_function_name}")
            
            # 获取API实例
            api = search_method.__self__
            if not hasattr(api, 'get_poi_total_list'):
                self.logger.warning("API实例没有get_poi_total_list方法，将只获取第一页数据")
                # 回退到原始搜索方法
                return self._execute_single_search(search_method, params)
            
            # 使用get_poi_total_list获取所有页面数据
            retries = 0
            while retries <= self.max_retries:
                try:
                    self.logger.info(f"使用分页获取方式获取所有数据...")
                    all_pois = api.get_poi_total_list(search_type=search_type, **params)
                    return all_pois
                except Exception as e:
                    retries += 1
                    if retries > self.max_retries:
                        raise Exception(f"达到最大重试次数，搜索失败: {str(e)}")
                    
                    self.logger.warning(f"搜索失败，正在重试 ({retries}/{self.max_retries}): {str(e)}")
                    time.sleep(self.retry_delay)
        
        # 如果执行到这里，说明出现了意外情况
        raise Exception("搜索执行失败，未能获取数据")
        
    def _execute_single_search(self, search_method: Callable, params: Dict) -> List[Dict]:
        """
        执行单次API搜索，不使用分页获取所有数据
        
        Args:
            search_method: API搜索方法
            params: 搜索参数
            
        Returns:
            搜索结果列表
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                result = search_method(**params)
                
                # 检查result是否为字典且包含pois键
                if isinstance(result, dict) and 'pois' in result:
                    return result['pois']
                elif isinstance(result, list):
                    # 如果已经是列表，则直接返回
                    return result
                else:
                    self.logger.error(f"API返回格式错误，未找到pois列表: {type(result)}")
                    if isinstance(result, dict):
                        self.logger.debug(f"API响应：{result.keys()}")
                    raise Exception("API返回格式错误，未找到pois列表")
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    raise Exception(f"达到最大重试次数，搜索失败: {str(e)}")
                
                self.logger.warning(f"搜索失败，正在重试 ({retries}/{self.max_retries}): {str(e)}")
                time.sleep(self.retry_delay)


# 辅助函数，直接处理单个任务
def process_single_task(task: Dict, global_settings: Dict = None) -> Dict:
    """
    直接处理单个任务
    
    Args:
        task: 任务配置
        global_settings: 全局设置
        
    Returns:
        任务处理结果
    """
    # 创建一个临时任务组
    task_group = {
        'api': task.get('api', 'gaode2'),
        'search_method': task.get('search_method', 'keywords'),
        'tasks': [task]
    }
    
    # 处理任务组
    processor = TaskProcessor(global_settings)
    result = processor.process_task_group('temp_group', task_group)
    
    # 返回第一个任务的结果
    if result.get('task_results') and len(result['task_results']) > 0:
        return result['task_results'][0]
    else:
        return {'status': 'error', 'message': '任务处理失败'}


# 测试函数
def test_task_processor():
    """测试任务处理器"""
    # 这里只进行简单的结构测试，不实际调用API
    try:
        # 创建任务处理器
        processor = TaskProcessor({
            'log_level': 'info',
            'output_dir': 'data/test',
            'add_timestamp': True
        })
        
        # 检查任务处理方法注册是否正确
        for api_type, methods in processor.task_handlers.items():
            print(f"API类型 {api_type} 支持的搜索方法:")
            for method_name in methods.keys():
                print(f"  - {method_name}")
        
        print("\n任务处理器初始化成功！")
        print("要运行实际测试，请导入并使用这个模块的 process_task_group 方法。")
    except Exception as e:
        print(f"测试任务处理器时出错: {str(e)}")


if __name__ == "__main__":
    # 如果直接运行该模块，则执行测试
    test_task_processor() 