import pandas as pd
from typing import List, Dict

class CodeReader:
    """读取和查询城市代码与POI类型代码"""
    
    # 直辖市列表
    MUNICIPALITIES = ['北京市', '上海市', '天津市', '重庆市']
    
    def __init__(self):
        # 读取Excel文件
        self.city_df = pd.read_excel('config/AMap_adcode_citycode.xlsx')
        self.poi_df = pd.read_excel('config/AMap_poicode.xlsx')
        
        # 打印列名用于调试
        # print("城市数据列名:", self.city_df.columns.tolist())
        # print("POI数据列名:", self.poi_df.columns.tolist())
        
    def get_district_codes(self, city_name: str) -> List[str]:
        """
        获取指定城市的所有区县代码
        
        Args:
            city_name: 城市名称，如"北京市"
            
        Returns:
            区县代码列表
        """
        # 先找到城市本身
        city_mask = self.city_df['中文名'].str.contains(f"^{city_name}$", na=False)
        city_data = self.city_df[city_mask]
        
        if city_data.empty:
            raise ValueError(f"未找到城市: {city_name}")
            
        city_adcode = str(city_data.iloc[0]['adcode'])
        
        # 对直辖市特殊处理
        if city_name in self.MUNICIPALITIES:
            # 直辖市使用前两位+01作为前缀，如北京为1101
            prefix = city_adcode[:2] + '01'
        else:
            # 普通城市使用前4位
            prefix = city_adcode[:4]
            
        print(f"使用前缀 {prefix} 查找 {city_name} 的区县")
        
        # 查找所有以该前缀开头的区县
        district_mask = (
            (self.city_df['adcode'].astype(str).str.startswith(prefix)) &
            (self.city_df['中文名'].str.contains('区|县|市$', na=False))
        )
        
        districts = self.city_df[district_mask]
        
        if districts.empty:
            print(f"警告：未找到{city_name}的下属区县")
            return []
            
        # 打印找到的区县信息
        print(f"找到的区县：{', '.join(districts['中文名'].tolist())}")
        return districts['adcode'].astype(str).tolist()
    
    def get_poi_types(self, big_category: str, mid_category: str = None) -> List[str]:
        """
        根据大类和中类获取POI类型代码
        
        Args:
            big_category: 大类名称，如"汽车服务"
            mid_category: 中类名称（可选），如"充电站"
            
        Returns:
            类型代码列表，保持完整格式（包括前导零）
        """
        print("\n=== POI类型匹配过程 ===")
        print(f"大类: {big_category}")
        if mid_category:
            print(f"中类: {mid_category}")
        
        # 首先匹配大类
        matched_df = self.poi_df[self.poi_df['大类'] == big_category]
        
        if matched_df.empty:
            print(f"\n未找到大类 '{big_category}'")
            print("可用的大类:")
            print(', '.join(self.poi_df['大类'].unique()))
            raise ValueError(f"未找到匹配的大类: {big_category}")
        
        # 如果指定了中类，继续筛选
        if mid_category:
            mid_matched_df = matched_df[matched_df['中类'] == mid_category]
            if mid_matched_df.empty:
                print(f"\n在大类 '{big_category}' 下未找到中类 '{mid_category}'")
                print("该大类下可用的中类:")
                print(', '.join(matched_df['中类'].unique()))
                raise ValueError(f"未找到匹配的中类: {mid_category}")
            matched_df = mid_matched_df
        
        # 打印匹配结果
        print(f"\n找到 {len(matched_df)} 个匹配的POI类型:")
        for _, row in matched_df.iterrows():
            print(f"\n类型ID: {row['NEW_TYPE']}")
            print(f"大类: {row['大类']}")
            print(f"中类: {row['中类']}")
            print(f"小类: {row['小类']}")
        
        # 确保返回的POI代码保持原始格式（包括前导零）
        return [f"{int(code):06d}" for code in matched_df['NEW_TYPE'].tolist()]

    def get_district_info(self, adcode: str) -> Dict:
        """
        获取区县的详细信息
        
        Args:
            adcode: 区县代码
            
        Returns:
            区县信息字典
        """
        district = self.city_df[self.city_df['adcode'].astype(str) == str(adcode)].iloc[0]
        return {
            'name': district['中文名'],
            'adcode': str(district['adcode']),
            'citycode': str(district['citycode'])
        }