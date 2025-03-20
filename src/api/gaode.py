import json
import time
from typing import List, Dict, Union, Optional
import requests


class GaodeAPI:
    """高德地图 POI 搜索 API 封装"""
    
    BASE_URL = "https://restapi.amap.com/v3/place"

    def __init__(self, key: str):
        """
        初始化高德API客户端
        
        Args:
            key: API密钥
        """
        self.key = key
        self.offset = 20  # 每页记录数，取值范围：1-25
        self.qps_delay = 0.5  # 每次请求之间的延时（秒）

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
        
        # 打印请求信息
        print("\n=== API请求信息 ===")
        print(f"URL: {url}")
        print("参数:")
        for key, value in params.items():
            if key != 'key':  # 不打印 API key
                print(f"  {key}: {value}")
        
        try:
            # 添加请求延时
            time.sleep(self.qps_delay)
            
            response = requests.get(url, params=params)
            result = response.json()
            
            # 打印响应信息
            print("\n=== API响应信息 ===")
            print(f"状态码: {result.get('status')}")
            print(f"信息: {result.get('info')}")
            print(f"总数: {result.get('count', '0')}")
            if result.get('pois'):
                print(f"本次返回: {len(result['pois'])} 条数据")
            
            if result['status'] != '1':
                if result.get('infocode') == '10009':  # QPS超限
                    print("QPS超限，等待后重试...")
                    # 如果是QPS超限，等待更长时间后重试
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
                         city: Optional[str] = None,
                         city_limit: bool = False,
                         extensions: str = 'base',
                         page: int = 1,
                         offset: Optional[int] = None) -> Dict:
        """
        关键字搜索POI
        
        Args:
            keywords: 关键字
            types: POI类型代码，可使用'|'组合多个类型
            city: 搜索城市（城市名、adcode等）
            city_limit: 是否限制在city指定的城市内
            extensions: 返回信息详略，'base'返回基本信息，'all'返回详细信息
            page: 页码，取值范围：1-100
            offset: 每页记录数，取值范围：1-25
        """
        if not keywords and not types:
            raise ValueError("keywords和types至少需要提供一个")
            
        params = {
            'page': page,
            'offset': offset or self.offset,
            'extensions': extensions
        }
        
        if keywords:
            params['keywords'] = keywords
        if types:
            params['types'] = types
        if city:
            params['city'] = city
        if city_limit:
            params['citylimit'] = 'true'
            
        return self._make_request('text', params)

    def search_around(self,
                     location: str,
                     keywords: Optional[str] = None,
                     types: Optional[str] = None,
                     radius: int = 5000,
                     sort_rule: str = 'distance',
                     extensions: str = 'base',
                     page: int = 1,
                     offset: Optional[int] = None) -> Dict:
        """
        周边搜索POI
        
        Args:
            location: 中心点坐标，格式：'longitude,latitude'
            keywords: 关键字
            types: POI类型代码
            radius: 搜索半径，单位：米，取值范围：0-50000
            sort_rule: 排序规则，'distance'按距离排序，'weight'按综合排序
            extensions: 返回信息详略，'base'返回基本信息，'all'返回详细信息
            page: 页码
            offset: 每页记录数
        """
        params = {
            'location': location,
            'radius': min(radius, 50000),
            'sortrule': sort_rule,
            'page': page,
            'offset': offset or self.offset,
            'extensions': extensions
        }
        
        if keywords:
            params['keywords'] = keywords
        if types:
            params['types'] = types
            
        return self._make_request('around', params)

    def search_polygon(self,
                      polygon: str,
                      keywords: Optional[str] = None,
                      types: Optional[str] = None,
                      extensions: str = 'base',
                      page: int = 1,
                      offset: Optional[int] = None) -> Dict:
        """
        多边形区域搜索POI
        
        Args:
            polygon: 多边形边界坐标点，格式：'lng1,lat1|lng2,lat2|...|lngn,latn'
            keywords: 关键字
            types: POI类型代码
            extensions: 返回信息详略，'base'返回基本信息，'all'返回详细信息
            page: 页码
            offset: 每页记录数
        """
        params = {
            'polygon': polygon,
            'page': page,
            'offset': offset or self.offset,
            'extensions': extensions
        }
        
        if keywords:
            params['keywords'] = keywords
        if types:
            params['types'] = types
            
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

    def get_poi_total_list(self,
                          search_type: str = 'keywords',
                          **search_params) -> List[Dict]:
        """获取所有分页的POI数据"""
        search_methods = {
            'keywords': self.search_by_keywords,
            'around': self.search_around,
            'polygon': self.search_polygon
        }
        
        if search_type not in search_methods:
            raise ValueError(f"不支持的搜索类型: {search_type}")
            
        search_method = search_methods[search_type]
        
        try:
            # 获取第一页
            print("\n开始获取数据...")
            first_page = search_method(page=1, **search_params)
            total_count = int(first_page['count'])
            result = first_page.get('pois', [])
            
            print(f"\n总计找到 {total_count} 条数据")
            if total_count == 0:
                return []
                
            # 获取剩余页面
            total_pages = (total_count + self.offset - 1) // self.offset
            if total_pages > 1:
                print(f"需要获取 {total_pages} 页数据")
                
            for page in range(2, total_pages + 1):
                print(f"\n正在获取第 {page}/{total_pages} 页...")
                page_result = search_method(page=page, **search_params)
                if page_result.get('pois'):
                    result.extend(page_result['pois'])
                    print(f"已获取 {len(result)}/{total_count} 条数据")
                
            return result
            
        except Exception as e:
            print(f"获取数据时出错: {str(e)}")
            return result  # 返回已获取的数据 