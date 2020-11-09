import pytest
from brownie import accounts, StdReferenceBasic

# Deploy StdReferenceBasic contract
@pytest.fixture(scope="module")
def stdrefbasic():
    return accounts[0].deploy(StdReferenceBasic)
