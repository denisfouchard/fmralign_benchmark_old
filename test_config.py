import sys  # noqa: F401

import pytest  # noqa: F401


def check_test_solver_install(solver_class):
    """Hook called in `test_solver_install`.

    If one solver needs to be skip/xfailed on some
    particular architecture, call pytest.xfail when
    detecting the situation.
    """
    fmralign_solvers = [
        "fastsrm",
        "identity",
        "ot",
        "procrustes",
        "ridge",
        "hyperalignment",
    ]

    if solver_class.name.lower() in fmralign_solvers:
        pytest.skip("fmralign solvers need to be installed from source")

    if solver_class.name.lower() == "fugw":
        pytest.skip("Latest version of fugw is not available on PyPI")
