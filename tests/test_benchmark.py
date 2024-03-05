import pytest
from statistics import median
import time
from src.main import first_func
@pytest.mark.benchmark( min_rounds=10,)
def test_median_performance(benchmark):

    benchmark(first_func)


def test_num():
    assert 1 + 1 == 2