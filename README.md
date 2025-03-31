# chargers_data

# POI数据搜索工具

这是一个用于搜索和收集POI数据的模块化工具，支持多种API和多种搜索方式。

## 功能特点

- **模块化设计**：易于扩展和维护
- **支持多种API**：可以轻松添加新的API支持
- **多种搜索方式**：支持关键字搜索、周边搜索、多边形区域搜索等
- **任务组管理**：在配置文件中定义多个任务组，每个任务组对应一种API和搜索方式
- **灵活的输出格式**：支持CSV和JSON格式输出
- **自动化日志**：详细记录各步骤执行情况
- **错误重试机制**：自动重试失败的API请求
- **数据去重**：在多边形网格搜索中自动去除重复POI
- **任务数量控制**：支持限制处理的任务数量，方便测试和调试
- **多边形网格搜索**：支持各种类型的多边形（三角形、四边形、六边形等）
- **边长控制**：支持指定多边形的边长而非半径
- **直接使用多边形坐标**：支持直接使用已格式化的多边形坐标，无需额外处理

## 项目结构

```
chargers_data/
├── config/
│   ├── search_config.json     # 搜索任务配置文件
│   └── gaode.token            # API密钥文件
├── src/
│   ├── gaode.py               # 高德地图API 1.0版本客户端
│   ├── gaode2.py              # 高德地图API 2.0版本客户端
│   ├── main.py                # 主程序入口
│   ├── examples/              # 示例脚本
│   │   ├── keywords_search.py     # 关键字搜索示例
│   │   ├── polygon_search.py      # 多边形搜索示例
│   │   └── task_processor_example.py  # 任务处理器示例
│   └── utils/                 # 工具模块
│       ├── api_factory.py         # API工厂模块
│       ├── config_parser.py       # 配置解析模块
│       ├── data_saver.py          # 数据保存模块
│       ├── logger.py              # 日志记录模块
│       ├── polygon_grid.py        # 多边形网格生成模块
│       └── task_processor.py      # 任务处理模块
├── data/                      # 数据输出目录
└── logs/                      # 日志输出目录
```

## 快速开始

### 使用Make命令（推荐）

项目提供了方便的Make命令来执行常见操作：

```bash
# 初始化项目（安装依赖）
make init

# 运行所有任务
make run

# 运行简化测试（只处理第一个任务）
make run-simple

# 运行特定任务组
make run ARGS="-g shanghai_keywords"

# 运行特定任务组的特定数量任务
make run ARGS="-g shanghai_keywords --task-count 3"

# 测试API连接
make test-api

# 清理数据和日志
make clean-data

# 完全清理项目
make clean-all
```

### 手动方式

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置API密钥

在`config`目录下创建`api.token`文件，内容为高德地图API密钥：

```
your_gaode_api_key_here
```

#### 创建默认配置文件

如果没有配置文件，可以通过以下命令创建默认配置：

```bash
python src/main.py --create-config
```

#### 运行主程序

```bash
# 运行所有任务组
python src/main.py

# 运行特定任务组
python src/main.py -g shanghai_keywords

# 只运行特定任务组的前N个任务
python src/main.py -g shanghai_keywords --task-count 3

# 使用自定义配置文件
python src/main.py -c my_config.json
```

## 命令行参数

程序支持以下命令行参数：

- `-c, --config`：指定配置文件路径（默认：config/search_config.json）
- `-g, --group`：指定要处理的任务组名称，不指定则处理所有任务组
- `-t, --task-count`：指定要处理的任务数量，不指定则处理所有任务
- `--create-config`：创建默认配置文件并退出

## 配置文件结构

配置文件采用JSON格式，包含两个主要部分：`task_groups`和`global_settings`。

### 任务组结构

```json
{
  "task_groups": {
    "group_name": {
      "api": "gaode2",
      "search_method": "keywords",
      "tasks": [
        {
          "name": "任务名称",
          "params": {
            "keywords": "搜索关键词",
            "types": "POI类型编码",
            "region": "区域代码",
            ...
          },
          "output": {
            "filename_prefix": "输出文件前缀",
            "formats": ["csv", "json"]
          }
        }
      ]
    }
  }
}
```

### 全局设置结构

```json
{
  "global_settings": {
    "output_dir": "data",
    "add_timestamp": true,
    "time_format": "%Y%m%d_%H%M",
    "max_retries": 3,
    "retry_delay": 1.0,
    "log_level": "info",
    "log_to_file": true,
    "log_dir": "logs"
  }
}
```

## 多边形搜索

### 自动生成多边形网格

支持根据指定的参数生成不同形状的多边形网格进行搜索：

```python
from src.utils.polygon_grid import generate_polygon_grid

# 生成六边形网格（使用边长指定）
polygons = generate_polygon_grid(
    center_lng=116.397428,  # 北京天安门
    center_lat=39.90923,
    region_radius=3000,     # 覆盖区域半径（米）
    edge_length=1000,       # 多边形边长（米）
    num_sides=6             # 六边形
)

# 其他支持的多边形类型
# num_sides=3  # 三角形
# num_sides=4  # 四边形
# num_sides=8  # 八边形
```

### 直接使用多边形坐标

可以直接指定多边形的经纬度坐标对，无需进行格式转换：

```json
{
  "tasks": [
    {
      "name": "自定义多边形搜索",
      "params": {
        "keywords": "充电站",
        "types": "011100|011101|011102|011103",
        "polygon": "116.460988,40.006919|116.48231,40.007381|116.47516,39.99713|116.460988,40.006919",
        "raw_polygon": true,  // 设置为true表示使用原始多边形坐标，无需额外格式转换
        "show_fields": "children,business,indoor,navi,photos"
      },
      "output": {
        "filename_prefix": "custom_polygon_search",
        "formats": ["csv", "json"]
      }
    }
  ]
}
```

如果不设置`raw_polygon`参数或设置为`false`，系统会自动检查并确保多边形坐标首尾相同（闭合）。

## 示例用法

### 关键字搜索示例

```python
from src.utils.api_factory import APIFactory
from src.utils.config_parser import load_api_key

# 加载API密钥和创建API实例
api_key = load_api_key('gaode')
api = APIFactory.get_api_instance('gaode2', api_key)

# 执行搜索
result = api.search_by_keywords(
    keywords="充电站",
    region="北京",
    city_limit=True,
    show_fields="children,business,indoor,navi,photos"
)
```

### 多边形网格搜索示例

```python
from src.utils.polygon_grid import generate_polygon_grid
from src.utils.data_saver import save_to_file
from src.utils.api_factory import APIFactory
from src.utils.config_parser import load_api_key

# 加载API密钥和创建API实例
api_key = load_api_key('gaode')
api = APIFactory.get_api_instance('gaode2', api_key)

# 生成多边形网格
polygons = generate_polygon_grid(
    center_lng=116.397428,  # 北京天安门
    center_lat=39.90923,
    region_radius=3000,     # 3公里
    edge_length=1000,       # 1公里边长
    num_sides=6             # 六边形
)

# 保存多边形边界用于可视化
save_to_file(polygons, "data/polygons.json", "json")

# 初始化结果集
all_pois = []
unique_poi_ids = set()

# 遍历搜索每个多边形
for i, polygon in enumerate(polygons):
    print(f"搜索多边形 {i+1}/{len(polygons)}")
    
    result = api.search_polygon(
        keywords="充电站",
        polygon=polygon,
        show_fields="children,business,indoor,navi,photos"
    )
    
    # 提取POI列表
    pois = result.get('pois', [])
    
    # 去重添加POI
    for poi in pois:
        poi_id = poi.get('id')
        if poi_id and poi_id not in unique_poi_ids:
            unique_poi_ids.add(poi_id)
            all_pois.append(poi)
    
    print(f"当前共找到 {len(all_pois)} 个唯一POI")

# 保存结果
save_to_file(all_pois, "data/all_pois.json", "json")
```

### 自定义多边形搜索示例

```python
from src.utils.api_factory import APIFactory
from src.utils.config_parser import load_api_key
from src.utils.data_saver import save_to_file

# 加载API密钥和创建API实例
api_key = load_api_key('gaode')
api = APIFactory.get_api_instance('gaode2', api_key)

# 定义自定义多边形（确保首尾坐标相同以闭合多边形）
custom_polygon = "116.460988,40.006919|116.48231,40.007381|116.47516,39.99713|116.460988,40.006919"

# 执行搜索
result = api.search_polygon(
    keywords="充电站",
    polygon=custom_polygon,
    show_fields="children,business,indoor,navi,photos"
)

# 提取POI列表
pois = result.get('pois', [])
print(f"找到 {len(pois)} 个POI")

# 保存结果
save_to_file(pois, "data/custom_polygon_pois.json", "json")
```

### 使用任务处理器

```python
from src.utils.task_processor import TaskProcessor

# 创建任务处理器
processor = TaskProcessor({
    "output_dir": "data/examples",
    "add_timestamp": True
})

# 处理任务组
result = processor.process_task_group("my_group", {
    "api": "gaode2",
    "search_method": "keywords",
    "tasks": [
        {
            "name": "搜索任务",
            "params": {...},
            "output": {...}
        }
    ]
})
```

## 最近更新

### 直接使用多边形坐标
添加了`raw_polygon`参数，支持直接使用已格式化的多边形坐标，无需额外的格式转换。

### 任务数量控制
添加了`--task-count`参数，支持限制处理的任务数量，方便测试和调试。

### 多边形类型支持
从原来只支持六边形网格扩展为支持多种类型的多边形（三角形、四边形、六边形、八边形等）。

### 使用边长而非半径
支持通过边长而非半径来定义多边形，使多边形设置更加直观。

### 错误处理优化
改进了API返回数据处理和错误处理机制，提高了程序的稳定性。

### 添加Make命令
添加了更多便捷的Make命令，简化了程序的使用。

## 自定义开发

### 添加新的API支持

1. 创建新的API客户端模块
2. 在`src/utils/api_factory.py`中注册新的API类型

```python
APIFactory.register_api('new_api', 'src.new_api_module', 'NewAPIClass')
```

### 添加新的搜索方法处理

在`src/utils/task_processor.py`中添加新的处理方法，并注册到`task_handlers`字典中。

## 许可证

MIT