import pytest
import brownie
from brownie import accounts, chain, StdReferenceBasic, StdReferenceProxy
import time

INPUTS_VALID = [
    (["ABC"], [123], [234], [345]),
    (
        ["BCD", "CDE"],
        [123789, 987654321],
        [987654321, 1234567890],
        [123789098765432, 98765432123456789],
    ),
]


@pytest.fixture(scope="module", autouse=False)
def stdrefproxy(stdrefbasic):
    return accounts[0].deploy(StdReferenceProxy, stdrefbasic.address)


@pytest.mark.parametrize("symbols,rates,resolveTimes,requestIDs", INPUTS_VALID)
def test_relay_success(
    stdrefbasic, stdrefproxy, symbols, rates, resolveTimes, requestIDs
):
    stdrefbasic.relay(symbols, rates, resolveTimes, requestIDs, {"from": accounts[0]})
    chain.sleep(20)
    ts = chain.time()
    for i in range(len(symbols)):
        stdRates = stdrefproxy.getReferenceData(symbols[i], "USD")
        assert stdRates[0] == rates[i] * 1e9
        assert stdRates[1] == resolveTimes[i]
        assert ts - stdRates[2] > 0


def test_setref_success(stdrefproxy):
    newRef = accounts[0].deploy(StdReferenceBasic)
    stdrefproxy.setRef(newRef.address, {"from": accounts[0]})


def test_setref_success_not_owner(stdrefproxy):
    newRef = accounts[0].deploy(StdReferenceBasic)
    with brownie.reverts():
        stdrefproxy.setRef(newRef.address, {"from": accounts[1]})
