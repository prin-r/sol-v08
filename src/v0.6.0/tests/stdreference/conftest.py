import pytest
from brownie import accounts, StdReferenceBasic


@pytest.fixture(scope="module")
def stdrefbasic():
    return accounts[0].deploy(StdReferenceBasic)
