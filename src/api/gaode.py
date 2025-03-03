import json
import requests


class GaodeAPI:
    """高德API接口封装"""

    def __init__(self, key, city='北京', keyword=None):
        """
        初始化高德API客户端
        
        Args:
            key (str): API密钥
            city (str, optional): 城市名称. 默认为'北京'
            keyword (str, optional): 搜索关键词. 默认为None
        """
        self.key = key
        self.keyword = keyword
        self.city = city
        self.offset = 20

    def get_poi_total_list(self):
        """
        获取所有POI列表
        
        Returns:
            list: POI信息列表
            
        Raises:
            Exception: 当日查询限额用完时抛出异常
        """
        first_page = self.get_poi_page(pagenum=1)
        if first_page['infocode'] == '10044':
            raise Exception('当日查询已限额，请明天再试.')
        
        page_count = int(first_page['count'])
        iterate_num = round(page_count / self.offset) + 1
        final_result = first_page.get('pois', [])  # 包含第一页结果
        
        for i in range(2, iterate_num + 1):  # 从第2页开始
            temp_result = self.get_poi_page(i)
            if temp_result.get('pois'):
                final_result.extend(temp_result['pois'])

        return final_result

    def get_poi_page(self, pagenum):
        """
        获取指定页码的POI详情
        
        Args:
            pagenum (int): 页码
            
        Returns:
            dict: API响应结果
        """
        url = (f'https://restapi.amap.com/v3/place/text'
               f'?city={self.city}'
               f'&offset={self.offset}'
               f'&page={pagenum}'
               f'&key={self.key}'
               f'&types=011100|011102|011103|073000|073001|073002'
               f'&extensions=all')

        response = requests.get(url)
        return json.loads(response.text) 