import pytest
from statistics import median
import time

@pytest.mark.benchmark
def test_median_performance(benchmark):

    benchmark(time.sleep, 5)


def test_num():
    assert 1 + 1 == 2