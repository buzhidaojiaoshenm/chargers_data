import json
import time
from typing import List, Dict, Union, Optional
import requests

from src.utils.logger import Logger

# 创建API专用日志记录器
logger = Logger(log_dir="logs/api")


class GaodeAPI2:
    """高德地图 POI 搜索 API 2.0版本封装"""
    
    BASE_URL = "https://restapi.amap.com/v5/place"
    MAX_PAGE_SIZE = 25  # 每页记录数上限
    MAX_PAGES = 100    # 最大页数限制

    def __init__(self, key: str):
        """
        初始化高德API客户端
        
        Args:
            key: API密钥
        """
        self.key = key
        self.page_size = 25  # 每页记录数，取值范围：1-25
        self.qps_delay = 0.5  # 每次请求之间的延时（秒）
        self.logger = Logger()

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        发送API请求
        
        Args:
            endpoint: API端点
            params: 请求参数
            
        Returns:
            API响应结果
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        params['key'] = self.key
        url = f"{self.BASE_URL}/{endpoint}"
        
        self.logger.info("\n=== API请求信息 ===")
        self.logger.info(f"URL: {url}")
        self.logger.info("参数:")
        for key, value in params.items():
            if key != 'key':  # 不打印 API key
                self.logger.info(f"  {key}: {value}")
        
        try:
            # 添加请求延时
            time.sleep(self.qps_delay)
            
            response = requests.get(url, params=params)
            result = response.json()
            
            self.logger.info("\n=== API响应信息 ===")
            self.logger.info(f"状态码: {result.get('status')}")
            self.logger.info(f"信息: {result.get('info')}")
            self.logger.info(f"总数: {result.get('count', '0')}")
            if result.get('pois'):
                self.logger.info(f"本次返回: {len(result['pois'])} 条数据")
            
            if result['status'] != '1':
                if result.get('infocode') == '10009':  # QPS超限
                    self.logger.warning("QPS超限，等待后重试...")
                    time.sleep(1)
                    return self._make_request(endpoint, params)
                raise Exception(f"API调用失败: {result.get('info', '未知错误')}")
                
            if result['infocode'] == '10044':
                raise Exception('当日查询已限额，请明天再试')
                
            return result
        except requests.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")

    def search_by_keywords(self, 
                         keywords: Optional[str] = None,
                         types: Optional[str] = None,
                         region: Optional[str] = None,
                         city_limit: bool = False,
                         show_fields: Optional[str] = None,
                         children: int = 0,
                         page_num: int = 1,
                         page_size: Optional[int] = None) -> Dict:
        """
        关键字搜索POI
        
        Args:
            keywords: 关键字
            types: POI类型代码
            region: 搜索区域（行政区划代码）
            city_limit: 是否限制城市内搜索
            show_fields: 返回字段控制
            children: 是否返回子POI，1：返回，0：不返回
            page_num: 页码，取值范围：1-100
            page_size: 每页记录数，取值范围：1-25
        """
        if not keywords and not types:
            raise ValueError("keywords和types至少需要提供一个")
            
        params = {
            'page_num': str(page_num),
            'page_size': str(page_size or self.page_size)
        }
        
        if keywords:
            params['keywords'] = keywords
        if types:
            params['types'] = types
        if region:
            params['region'] = region
        if city_limit:
            params['city_limit'] = 'true'
        if show_fields:
            params['show_fields'] = show_fields
        if children:
            params['children'] = str(children)
            
        return self._make_request('text', params)

    def search_around(self,
                     location: str,
                     keywords: Optional[str] = None,
                     types: Optional[str] = None,
                     radius: int = 5000,
                     sort_rule: str = 'distance',
                     show_fields: Optional[str] = None,
                     children: int = 0,
                     page_num: int = 1,
                     page_size: Optional[int] = None) -> Dict:
        """
        周边搜索POI
        
        Args:
            location: 中心点坐标，格式：'longitude,latitude'
            keywords: 关键字
            types: POI类型代码
            radius: 搜索半径，单位：米，取值范围：0-50000
            sort_rule: 排序规则，'distance'按距离排序
            show_fields: 返回字段控制
            children: 是否返回子POI
            page_num: 页码
            page_size: 每页记录数
        """
        params = {
            'location': location,
            'radius': str(min(radius, 50000)),
            'sort_rule': sort_rule,
            'page_num': str(page_num),
            'page_size': str(page_size or self.page_size)
        }
        
        if keywords:
            params['keywords'] = keywords
        if types:
            params['types'] = types
        if show_fields:
            params['show_fields'] = show_fields
        if children:
            params['children'] = str(children)
            
        return self._make_request('around', params)

    def search_polygon(self,
                      polygon: str,
                      keywords: Optional[str] = None,
                      types: Optional[str] = None,
                      show_fields: Optional[str] = None,
                      children: int = 0,
                      page_num: int = 1,
                      page_size: Optional[int] = None) -> Dict:
        """
        多边形区域搜索POI
        
        Args:
            polygon: 多边形边界坐标点，格式：'lng1,lat1|lng2,lat2|...|lngn,latn'
            keywords: 关键字
            types: POI类型代码
            show_fields: 返回字段控制
            children: 是否返回子POI
            page_num: 页码
            page_size: 每页记录数
        """
        params = {
            'polygon': polygon,
            'page_num': str(page_num),
            'page_size': str(page_size or self.page_size)
        }
        
        if keywords:
            params['keywords'] = keywords
        if types:
            params['types'] = types
        if show_fields:
            params['show_fields'] = show_fields
        if children:
            params['children'] = str(children)
            
        return self._make_request('polygon', params)

    def search_by_id(self,
                    id: Union[str, List[str]],
                    show_fields: Optional[str] = None) -> Dict:
        """
        根据ID搜索POI
        
        Args:
            id: POI ID或ID列表（最多10个）
            show_fields: 返回字段控制
            
        Returns:
            搜索结果
        """
        if isinstance(id, list):
            if len(id) > 10:
                raise ValueError("ID数量不能超过10个")
            id = '|'.join(id)
            
        params = {'id': id}
        if show_fields:
            params['show_fields'] = show_fields
            
        return self._make_request('detail', params)

    def get_poi_total_list(self, search_type: str, **params) -> List[Dict]:
        """
        获取所有页面的POI数据
        
        Args:
            search_type: 搜索类型，可选值：'keywords'（关键字搜索）, 'around'（周边搜索）, 'polygon'（多边形搜索）
            **params: 搜索参数
            
        Returns:
            所有页面的POI数据列表
        """
        all_pois = []
        page_num = 1
        has_more_data = True
        
        # 设置每页大小为最大值
        params['page_size'] = str(self.MAX_PAGE_SIZE)
        
        self.logger.info("\n开始获取数据...")
        self.logger.info(f"搜索类型: {search_type}")
        self.logger.info("搜索参数:")
        for key, value in params.items():
            if key != 'key':  # 不打印 API key
                self.logger.info(f"  {key}: {value}")
        
        while page_num <= self.MAX_PAGES and has_more_data:  # 最多获取100页且有数据时继续
            self.logger.info(f"\n正在获取第 {page_num} 页...")
            
            # 设置当前页码
            params['page_num'] = str(page_num)
            
            # 根据搜索类型调用相应的方法
            if search_type == 'keywords':
                result = self.search_by_keywords(**params)
            elif search_type == 'around':
                result = self.search_around(**params)
            elif search_type == 'polygon':
                result = self.search_polygon(**params)
            else:
                raise ValueError(f"不支持的搜索类型: {search_type}")
            
            # 获取当前页的POI列表
            pois = result.get('pois', [])
            
            # 如果没有数据了，退出循环
            if not pois:
                self.logger.info("没有更多数据了")
                has_more_data = False
                break
            
            # 添加本页数据
            all_pois.extend(pois)
            
            # 获取总数（第一页时）- 仅用于显示，不用于判断结束条件
            if page_num == 1:
                total_count = int(result.get('count', '0'))
                self.logger.info(f"\n服务器返回总数: {total_count} 条数据")
                self.logger.info("注意：实际数据量可能超过这个数值")
                if total_count == 0:
                    has_more_data = False
                    break
            
            self.logger.info(f"第 {page_num} 页获取到 {len(pois)} 条数据")
            self.logger.info(f"当前共获取 {len(all_pois)} 条数据")
            
            # 如果这一页获取的数据量小于页大小，说明没有更多数据了
            if len(pois) < int(params['page_size']):
                self.logger.info("当前页数据不足一页，应该没有更多数据了")
                has_more_data = False
                break
                
            # 继续获取下一页
            page_num += 1
            
        self.logger.info(f"\n获取完成，共获取 {len(all_pois)} 条数据")
        return all_pois 