import scrivid

import importlib.metadata

import pytest


def convert_package_version_to_tuple(package_version):
    return tuple(int(element) for element in package_version.split("."))


@pytest.fixture
def package_version():
    yield importlib.metadata.version("scrivid")


def test_package_version(package_version):
    assert scrivid.__version__ == package_version


def test_package_version_tuple(package_version):
    package_version = convert_package_version_to_tuple(package_version)
    assert scrivid.__version_tuple__ == package_version
