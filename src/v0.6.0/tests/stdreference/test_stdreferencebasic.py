import pytest
import brownie
from brownie import accounts, StdReferenceBasic
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

INPUTS_INVALID_RATES_LENGTH = [
    (["ABC"], [123, 234], [345], [456]),
    (["BCD", "CDE"], [123], [234, 345], [456, 567]),
]

INPUTS_INVALID_RESOLVETIMES_LENGTH = [
    (["ABC"], [123], [234, 345], [456]),
    (["BCD", "CDE"], [123, 234], [345], [456, 567]),
]

INPUTS_INVALID_REQUESTIDS_LENGTH = [
    (["ABC"], [123], [234], [345, 456]),
    (["BCD", "CDE"], [123, 234], [345, 456], [567]),
]


@pytest.mark.parametrize("symbols,rates,resolveTimes,requestIds", INPUTS_VALID)
def test_relay_success(stdrefbasic, symbols, rates, resolveTimes, requestIds):
    stdrefbasic.relay(symbols, rates, resolveTimes, requestIds, {"from": accounts[0]})


@pytest.mark.parametrize("symbols,rates,resolveTimes,requestIds", INPUTS_VALID)
def test_relay_not_relayer(stdrefbasic, symbols, rates, resolveTimes, requestIds):
    with brownie.reverts("NOTARELAYER"):
        stdrefbasic.relay(
            symbols, rates, resolveTimes, requestIds, {"from": accounts[1]}
        )


@pytest.mark.parametrize(
    "symbols,rates,resolveTimes,requestIds", INPUTS_INVALID_RATES_LENGTH
)
def test_relay_invalid_rates_length(
    stdrefbasic, symbols, rates, resolveTimes, requestIds
):
    with brownie.reverts("BADRATESLENGTH"):
        stdrefbasic.relay(
            symbols, rates, resolveTimes, requestIds, {"from": accounts[0]}
        )


@pytest.mark.parametrize(
    "symbols,rates,resolveTimes,requestIds", INPUTS_INVALID_RESOLVETIMES_LENGTH
)
def test_relay_invalid_resolvetimes_length(
    stdrefbasic, symbols, rates, resolveTimes, requestIds
):
    with brownie.reverts("BADRESOLVETIMESLENGTH"):
        stdrefbasic.relay(
            symbols, rates, resolveTimes, requestIds, {"from": accounts[0]}
        )


@pytest.mark.parametrize(
    "symbols,rates,resolveTimes,requestIds", INPUTS_INVALID_REQUESTIDS_LENGTH
)
def test_relay_invalid_requestids_length(
    stdrefbasic, symbols, rates, resolveTimes, requestIds
):
    with brownie.reverts("BADREQUESTIDSLENGTH"):
        stdrefbasic.relay(
            symbols, rates, resolveTimes, requestIds, {"from": accounts[0]}
        )


@pytest.mark.parametrize("symbols,rates,resolveTimes,requestIds", INPUTS_VALID)
def test_getreferencedata(stdrefbasic, symbols, rates, resolveTimes, requestIds):
    stdrefbasic.relay(symbols, rates, resolveTimes, requestIds, {"from": accounts[0]})
    ts = time.time()
    for i in range(len(symbols)):
        stdRates = stdrefbasic.getReferenceData(symbols[i], "USD")
        assert stdRates[0] == rates[i] * 1e9
        assert stdRates[1] == resolveTimes[i]
        assert ts - stdRates[2] > 0
