import json
import pytest
from unittest.mock import patch
from src.api.gaode import GaodeAPI


@pytest.fixture
def api():
    return GaodeAPI(key="test_key")


def test_gaode_api_init(api):
    assert api.key == "test_key"
    assert api.city == "北京"
    assert api.offset == 20


@patch('requests.get')
def test_get_poi_page(mock_get, api):
    # 模拟API响应
    mock_response = {
        'status': '1',
        'count': '100',
        'infocode': '10000',
        'pois': [{'id': '1', 'name': 'test_poi'}]
    }
    
    # 使用 json.dumps 将字典转换为 JSON 字符串
    mock_get.return_value.text = json.dumps(mock_response)
    
    result = api.get_poi_page(1)
    assert isinstance(result, dict)
    assert 'status' in result
    assert result['status'] == '1'


@patch('src.api.gaode.GaodeAPI.get_poi_page')
def test_get_poi_total_list(mock_get_poi_page, api):
    # 模拟第一页响应
    mock_get_poi_page.return_value = {
        'status': '1',
        'count': '2',
        'infocode': '10000',
        'pois': [{'id': '1', 'name': 'poi1'}]
    }
    
    result = api.get_poi_total_list()
    assert isinstance(result, list)
    assert len(result) > 0


def test_api_limit_exception(api):
    with patch('src.api.gaode.GaodeAPI.get_poi_page') as mock_get:
        mock_get.return_value = {'infocode': '10044'}
        
        with pytest.raises(Exception) as exc_info:
            api.get_poi_total_list()
        
        assert '当日查询已限额' in str(exc_info.value) 