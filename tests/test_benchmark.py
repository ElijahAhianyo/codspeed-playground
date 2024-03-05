# import pytest
# from statistics import median
# import time
#
# @pytest.mark.benchmark
# def test_median_performance(benchmark):
#
#     benchmark(time.sleep, 5)
#
#
# def test_num():
#     assert 1 + 1 == 2

import pytest
import numba
from pathlib import Path
from typing import Any, Callable, cast
import ast

from egglog.exp.array_api import *
from egglog.exp.array_api_numba import array_api_numba_module
from egglog.exp.array_api_program_gen import *
from sklearn import config_context, datasets
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


def test_simplify_any_unique():
    X = NDArray.var("X")
    res = (
        any(
            (astype(unique_counts(X)[Int(1)], DType.float64) / NDArray.scalar(Value.float(Float(150.0))))
            < NDArray.scalar(Value.int(Int(0)))
        )
        .to_value()
        .to_bool
    )

    egraph = EGraph([array_api_module])
    egraph.register(res)
    egraph.run((run() * 20).saturate())
    egraph.check(eq(res).to(FALSE))


def test_tuple_value_includes():
    x = TupleValue(Value.bool(FALSE))
    should_be_true = x.includes(Value.bool(FALSE))
    should_be_false = x.includes(Value.bool(TRUE))
    egraph = EGraph([array_api_module])
    egraph.register(should_be_true)
    egraph.register(should_be_false)
    egraph.run((run() * 10).saturate())
    egraph.check(eq(should_be_true).to(TRUE))
    egraph.check(eq(should_be_false).to(FALSE))


def test_reshape_index():
    # Verify that it doesn't expand forever
    x = NDArray.var("x")
    new_shape = TupleInt(Int(-1))
    res = reshape(x, new_shape).index(TupleInt(Int(1)) + TupleInt(Int(2)))
    egraph = EGraph([array_api_module])
    egraph.register(res)
    egraph.run(run() * 10)
    equiv_expr = egraph.extract_multiple(res, 10)
    assert len(equiv_expr) < 10


def test_reshape_vec_noop():
    x = NDArray.var("x")
    assume_shape(x, TupleInt(Int(5)))
    res = reshape(x, TupleInt(Int(-1)))
    egraph = EGraph([array_api_module])
    egraph.register(res)
    egraph.run(run() * 10)
    equiv_expr = egraph.extract_multiple(res, 10)

    assert len(equiv_expr) == 2
    egraph.check(eq(res).to(x))


# This test happens in different steps. Each will be benchmarked and saved as a snapshot.
# The next step will load the old snapshot and run their test on it.


def run_lda(x, y):
    with config_context(array_api_dispatch=True):
        lda = LinearDiscriminantAnalysis(n_components=2)
        return lda.fit(x, y).transform(x)


iris = datasets.load_iris()
X_np, y_np = (iris.data, iris.target)
res = run_lda(X_np, y_np)


def _load_py_snapshot(fn: Callable, var: str | None = None) -> Any:
    """
    Load a python snapshot, evaling the code, and returning the `var` defined in it.

    If no var is provided, then return the last expression.
    """
    path = Path(__file__).parent / "__snapshots__" / "test_array_api" / f"TestLDA.{fn.__name__}.py"
    contents = path.read_text()

    contents = "import numpy as np\nfrom egglog.exp.array_api import *\n" + contents
    globals: dict[str, Any] = {}
    if var is None:
        # exec once as a full statement
        exec(contents, globals)
        # Eval the last statement
        last_expr = ast.unparse(ast.parse(contents).body[-1])
        return eval(last_expr, globals)
    else:
        exec(contents, globals)
        return globals[var]
