import pytest


def _evaluate_keyword(keyword, skip_categories):
    if keyword in skip_categories:
        return True
    else:
        return False


def pytest_addoption(parser):
    parser.addoption("--skip", action="store", default=[], nargs="+", help="Skips the specified categories.")


def pytest_collection_modifyitems(config, items):
    skip_categories = config.getoption("--skip")
    if not skip_categories:
        return

    for item in items:
        keywords = item.keywords

        for keyword in keywords:
            if not _evaluate_keyword(keyword, skip_categories):
                continue

            item.add_marker(pytest.mark.skip())
            break
