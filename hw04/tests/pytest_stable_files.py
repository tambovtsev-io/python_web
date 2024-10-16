import pytest
from pathlib import Path

def pytest_addoption(parser):
    parser.addini('stable_files', 'list of stable test files', type='linelist')

def pytest_collection_modifyitems(config, items):
    main_patterns = config.getini('stable_files')

    for item in items:
        fspath = Path(item.fspath)
        if any(fspath.match(pattern) for pattern in main_patterns):
            item.add_marker(pytest.mark.stable)
