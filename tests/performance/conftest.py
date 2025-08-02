"""Configuration for performance tests."""
import pytest
import time
from typing import Callable, Any


def pytest_configure(config):
    """Register performance marker."""
    config.addinivalue_line(
        "markers",
        "performance: mark test as a performance test (deselect with '-m "not performance"')",
    )


@pytest.fixture(scope="function")
def benchmark():
    ""
    Simple benchmark fixture for performance testing.
    
    Example:
        def test_something(benchmark):
            result = benchmark(lambda: some_function(arg1, arg2))
            assert result == expected_value
    """
    class Benchmark:
        def __call__(self, func: Callable[..., Any], *args, **kwargs) -> Any:
            """Run the function and return its result along with timing information."""
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            # Store timing information
            self.duration = end_time - start_time
            self.start_time = start_time
            self.end_time = end_time
            
            return result
    
    return Benchmark()


@pytest.fixture(scope="session", autouse=True)
def skip_slow_tests(request):
    """Skip performance tests unless explicitly requested with --runslow."""
    if "performance" in request.keywords and not request.config.getoption("--runslow"):
        pytest.skip("performance tests are skipped by default (use --runslow to run them)")
