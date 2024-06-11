import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--generate", action="store_true",
        help="generate expected JSON outputs for GCN Notices"
    )


@pytest.fixture
def generate(request):
    return request.config.getoption("--generate")
