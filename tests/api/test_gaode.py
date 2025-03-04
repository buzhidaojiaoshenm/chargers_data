import json
import pytest
from unittest.mock import patch
from src.api.gaode import GaodeAPI
import requests


@pytest.fixture
def api():
    return GaodeAPI(key="test_key")


def test_gaode_api_init(api):
    assert api.key == "test_key"
    assert api.offset == 20


@patch('requests.get')
def test_search_by_keywords(mock_get, api):
    # 模拟API响应
    mock_response = {
        'status': '1',
        'count': '100',
        'infocode': '10000',
        'pois': [{'id': '1', 'name': 'test_poi'}]
    }
    mock_get.return_value.json.return_value = mock_response
    
    result = api.search_by_keywords(keywords="餐厅", city="北京")
    assert result == mock_response
    
    # 验证请求参数
    args, kwargs = mock_get.call_args
    params = kwargs['params']
    assert params['keywords'] == '餐厅'
    assert params['city'] == '北京'


@patch('requests.get')
def test_search_around(mock_get, api):
    mock_response = {
        'status': '1',
        'count': '50',
        'infocode': '10000',
        'pois': [{'id': '2', 'name': 'nearby_poi'}]
    }
    mock_get.return_value.json.return_value = mock_response
    
    result = api.search_around(
        location="116.397428,39.909187",
        radius=1000,
        keywords="咖啡",
        extensions='all'
    )
    assert result == mock_response
    
    # 验证请求参数
    args, kwargs = mock_get.call_args
    params = kwargs['params']
    assert params['location'] == '116.397428,39.909187'
    assert params['radius'] == 1000
    assert params['keywords'] == '咖啡'
    assert params['extensions'] == 'all'


@patch('requests.get')
def test_search_polygon(mock_get, api):
    mock_response = {
        'status': '1',
        'count': '30',
        'infocode': '10000',
        'pois': [{'id': '3', 'name': 'area_poi'}]
    }
    mock_get.return_value.json.return_value = mock_response
    
    polygon = "116.460988,40.006919|116.48231,40.007381|116.47516,39.99713"
    result = api.search_polygon(
        polygon=polygon,
        types="050000",
        extensions='all'
    )
    assert result == mock_response
    
    # 验证请求参数
    args, kwargs = mock_get.call_args
    params = kwargs['params']
    assert params['polygon'] == polygon
    assert params['types'] == '050000'
    assert params['extensions'] == 'all'


@patch('requests.get')
def test_search_by_id(mock_get, api):
    mock_response = {
        'status': '1',
        'infocode': '10000',
        'pois': [{'id': '4', 'name': 'specific_poi'}]
    }
    mock_get.return_value.json.return_value = mock_response
    
    # 测试单个ID
    result = api.search_by_id("B000A7BM4H")
    assert result == mock_response
    
    # 测试多个ID
    result = api.search_by_id(["B000A7BM4H", "B0FFKEPXS2"])
    assert result == mock_response
    
    # 验证请求参数
    args, kwargs = mock_get.call_args
    params = kwargs['params']
    assert params['id'] == "B000A7BM4H|B0FFKEPXS2"
    
    # 测试ID数量超限
    with pytest.raises(ValueError):
        api.search_by_id(["id"] * 11)


@patch('requests.get')
def test_api_error_handling(mock_get, api):
    # 测试API错误响应
    mock_get.return_value.json.return_value = {
        'status': '0',
        'info': 'INVALID_USER_KEY',
        'infocode': '10001'
    }
    
    with pytest.raises(Exception) as exc_info:
        api.search_by_keywords(keywords="test")
    assert "API调用失败" in str(exc_info.value)
    
    # 测试请求异常
    mock_get.side_effect = requests.RequestException("Connection error")
    with pytest.raises(Exception) as exc_info:
        api.search_by_keywords(keywords="test")
    assert "请求失败" in str(exc_info.value)


@patch('src.api.gaode.GaodeAPI.search_by_keywords')
def test_get_poi_total_list(mock_search, api):
    # 模拟分页数据
    mock_search.side_effect = [
        {
            'status': '1',
            'count': '45',
            'infocode': '10000',
            'pois': [{'id': str(i)} for i in range(20)]
        },
        {
            'status': '1',
            'infocode': '10000',
            'pois': [{'id': str(i)} for i in range(20, 40)]
        },
        {
            'status': '1',
            'infocode': '10000',
            'pois': [{'id': str(i)} for i in range(40, 45)]
        }
    ]
    
    result = api.get_poi_total_list(
        search_type='keywords',
        keywords="餐厅",
        city="北京"
    )
    
    assert len(result) == 45
    assert all(isinstance(poi, dict) for poi in result) 