# tests/test_calculator.py
import pytest
from modules.calculator import calculate_system

def test_calculate_slider_l():
    result = calculate_system({
        'system_type': 'Slider L',
        'width': 3000,
        'height': 2500,
        'panels': 3,
        'opening': 'влево',
        'left_edge': 'боковой профиль',
        'right_edge': 'боковой профиль'
    })

    assert 'system_info' in result
    assert 'profiles' in result
    assert 'hardware' in result
    assert result['system_info']['type'] == 'Slider L'
    assert len(result['profiles']) > 0

def test_calculate_unknown_system():
    with pytest.raises(ValueError):
        calculate_system({'system_type': 'Unknown'})
