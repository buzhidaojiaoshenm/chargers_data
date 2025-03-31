import math
from typing import List, Tuple, Dict


def edge_length_to_radius(edge_length: float, num_sides: int) -> float:
    """
    根据多边形的边长计算其外接圆半径
    
    Args:
        edge_length: 多边形边长（米）
        num_sides: 多边形边数
        
    Returns:
        多边形的外接圆半径（米）
    """
    # 对于正多边形，边长与外接圆半径的关系为：edge_length = 2 * radius * sin(π/num_sides)
    # 求解出半径：radius = edge_length / (2 * sin(π/num_sides))
    return edge_length / (2 * math.sin(math.pi / num_sides))


def generate_polygon_grid(center_lng: float, center_lat: float, region_radius: float, 
                         edge_length: float, num_sides: int = 6) -> List[str]:
    """
    生成一个圆形区域内的多边形网格，并返回每个多边形的边界坐标点。
    
    Args:
        center_lng: 中心点经度
        center_lat: 中心点纬度
        region_radius: 整个区域的半径（米）
        edge_length: 每个多边形的边长（米）
        num_sides: 多边形边数（3=三角形，4=四边形，6=六边形等）
        
    Returns:
        多边形边界坐标点列表，每个边界格式为：'lng1,lat1|lng2,lat2|...|lngn,latn|lng1,lat1'
    """
    if num_sides < 3:
        raise ValueError("多边形边数不能小于3")
    
    # 根据边长计算多边形的外接圆半径
    polygon_radius = edge_length_to_radius(edge_length, num_sides)
    
    # 计算多边形顶点的角度
    polygon_angles = [i * (360 / num_sides) for i in range(num_sides)]
    
    # 计算经度和纬度的转换因子（将米转换为经纬度）
    # 纬度：1度约等于111.32公里
    lat_to_meters = 111320.0
    # 经度：1度在特定纬度下的距离
    lng_to_meters = 111320.0 * math.cos(math.radians(center_lat))
    
    # 计算网格布局参数
    # 对于不同形状的多边形，网格布局会有所不同
    if num_sides == 3:  # 三角形
        # 三角形排列呈蜂巢状，水平距离为边长，垂直为边长*sin(60°)
        grid_width = edge_length
        grid_height = edge_length * math.sin(math.radians(60))
        # 布局模式：交错排列
        is_staggered = True
        stagger_offset = edge_length / 2
    elif num_sides == 4:  # 四边形/正方形
        # 正方形网格，水平和垂直距离都是边长
        grid_width = edge_length
        grid_height = edge_length
        # 布局模式：网格排列
        is_staggered = False
        stagger_offset = 0
    else:  # 默认为六边形或其他多边形
        # 六边形排列中，相邻六边形中心点之间的水平距离为边长 * (1 + cos(60°))
        grid_width = edge_length * (1 + math.cos(math.radians(60)))
        # 竖直方向上，相邻中心点距离为边长 * sin(60°) * 2
        grid_height = edge_length * math.sin(math.radians(60)) * 2
        # 布局模式：交错排列（六边形蜂巢结构）
        is_staggered = True
        stagger_offset = grid_width / 2
    
    # 计算需要多少个多边形覆盖整个区域
    num_polygons_radius = math.ceil(region_radius / min(grid_width, grid_height)) + 1
    
    # 存储生成的多边形边界
    polygons = []
    
    # 生成网格中的每个多边形
    for row in range(-num_polygons_radius, num_polygons_radius + 1):
        for col in range(-num_polygons_radius, num_polygons_radius + 1):
            # 计算多边形中心点
            # 根据布局模式决定是否需要偏移
            offset = stagger_offset if (is_staggered and row % 2 != 0) else 0
            
            # 计算中心点坐标（米）
            x = col * grid_width + offset
            y = row * grid_height
            
            # 转换为经纬度坐标
            polygon_center_lng = center_lng + (x / lng_to_meters)
            polygon_center_lat = center_lat + (y / lat_to_meters)
            
            # 计算中心点到区域中心的距离
            distance = math.sqrt(x**2 + y**2)
            
            # 如果多边形中心在区域内，则生成该多边形
            if distance <= region_radius:
                # 计算多边形顶点
                vertices = []
                for angle in polygon_angles:
                    # 计算顶点相对于中心点的偏移（米）
                    vertex_x = polygon_radius * math.cos(math.radians(angle))
                    vertex_y = polygon_radius * math.sin(math.radians(angle))
                    
                    # 转换为经纬度坐标
                    vertex_lng = polygon_center_lng + (vertex_x / lng_to_meters)
                    vertex_lat = polygon_center_lat + (vertex_y / lat_to_meters)
                    
                    vertices.append(f"{vertex_lng},{vertex_lat}")
                
                # 添加第一个点作为最后一个点，确保闭合
                vertices.append(vertices[0])
                
                # 组合成多边形边界字符串
                polygon_boundary = "|".join(vertices)
                polygons.append(polygon_boundary)
    
    return polygons


# 保持原有的六边形网格生成函数，但实际调用新的通用函数
def generate_hexagon_grid(center_lng: float, center_lat: float, region_radius: float, 
                         hexagon_radius: float) -> List[str]:
    """
    生成一个圆形区域内的六边形网格，并返回每个六边形的边界坐标点。
    (此函数保留用于向后兼容，通过半径来指定六边形)
    
    Args:
        center_lng: 中心点经度
        center_lat: 中心点纬度
        region_radius: 整个区域的半径（米）
        hexagon_radius: 每个六边形的半径（米）
        
    Returns:
        六边形边界坐标点列表，每个边界格式为：'lng1,lat1|lng2,lat2|...|lng6,lat6|lng1,lat1'
    """
    # 六边形的边长是外接圆半径乘以2倍sin(30°)
    edge_length = 2 * hexagon_radius * math.sin(math.pi / 6)
    return generate_polygon_grid(center_lng, center_lat, region_radius, edge_length, num_sides=6)


def coords_to_polygon_param(coords: str) -> str:
    """
    确保多边形参数格式正确，首尾坐标点相同。
    
    Args:
        coords: 坐标点字符串，格式：'lng1,lat1|lng2,lat2|...|lngn,latn'
        
    Returns:
        确保首尾坐标点相同的多边形参数
    """
    points = coords.split('|')
    if points[0] != points[-1]:
        points.append(points[0])
        return '|'.join(points)
    return coords 