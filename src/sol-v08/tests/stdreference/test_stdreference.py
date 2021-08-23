import pytest
import brownie
from brownie import accounts
import time

def test_challenge_invalid_relay_data(stdrefbasicv2, valid_proof):
    stdrefbasicv2.relay(["AAPL"], [126740000001], [1623244117], [3], {"from": accounts[0]})
    stdrefbasicv2.challenge("AAPL", valid_proof, {"from": accounts[0]})
    

def test_challenge_invalid_relay_symbol(stdrefbasicv2, valid_proof):
    stdrefbasicv2.relay(["ASYMBOL"], [126740000000], [1623244117], [3], {"from": accounts[0]})
    stdrefbasicv2.challenge("ASYMBOL", valid_proof, {"from": accounts[0]}) # ASYMBOL is not in requests

def test_challenge_invalid_oracle_id(stdrefbasicv2, valid_proof_of_other_oracle_id):
    stdrefbasicv2.relay(["AAPL"], [126740000000], [1623244977], [4], {"from": accounts[0]})
    stdrefbasicv2.challenge("AAPL", valid_proof_of_other_oracle_id, {"from": accounts[0]})

def test_challenge_valid_relay_data(stdrefbasicv2, valid_proof):
    with brownie.reverts():
        stdrefbasicv2.relay(["AAPL"], [126740000000], [1623244117], [3], {"from": accounts[0]})
        stdrefbasicv2.challenge("AAPL", valid_proof, {"from": accounts[0]})

def test_challenge_not_exists_symbol(stdrefbasicv2, valid_proof):
    with brownie.reverts("SYMBOL_IS_NOT_IN_PENDING_REFS"):
        stdrefbasicv2.relay(["AAPL"], [126740000000], [1623244117], [3], {"from": accounts[0]})
        stdrefbasicv2.challenge("ASYMBOL", valid_proof, {"from": accounts[0]})

def test_challenge_unmatched_id(stdrefbasicv2, valid_proof):
    with brownie.reverts("REQUEST_ID_IS_NOT_MATCHED"):
        stdrefbasicv2.relay(["AAPL"], [126740000000], [1623244117], [999999999999], {"from": accounts[0]})
        stdrefbasicv2.challenge("AAPL", valid_proof, {"from": accounts[0]})

def test_challengebycount_invalid_relay_data(stdrefbasicv2, valid_requests_count_proof):
    stdrefbasicv2.relay(["AAPL"], [126740000000], [1623244117], [999999999999], {"from": accounts[0]})
    stdrefbasicv2.challengeByCount("AAPL", valid_requests_count_proof, {"from": accounts[0]})

def test_challengebycount_valid_relay_data(stdrefbasicv2, valid_requests_count_proof):
    stdrefbasicv2.relay(["AAPL"], [126740000000], [1623244117], [3], {"from": accounts[0]})
    with brownie.reverts():
        stdrefbasicv2.challengeByCount("AAPL", valid_requests_count_proof, {"from": accounts[0]})

def test_challengebycount_invalid_symbol(stdrefbasicv2, valid_requests_count_proof):
    stdrefbasicv2.relay(["AAPL"], [126740000000], [1623244117], [3], {"from": accounts[0]})
    with brownie.reverts("NO_SYMBOL_IN_PENDING_REFS"):
        stdrefbasicv2.challengeByCount("ASYMBOL", valid_requests_count_proof, {"from": accounts[0]})

@pytest.mark.parametrize("timeDiff", [-100, 0, 1, 4])
def test_relay_with_valid_resolvetime(stdrefbasicv2, timeDiff):
    resolve_time = int(time.time()) + timeDiff
    stdrefbasicv2.relay(["AAPL"], [126740000000], [resolve_time], [3], {"from": accounts[0]})
    assert stdrefbasicv2.pendingRefs("AAPL") != (0, 0, 0, 0)

@pytest.mark.parametrize("timeDiff", [6, 10, 999999])
def test_relay_with_invalid_resolvetime(stdrefbasicv2, timeDiff):
    resolve_time = int(time.time()) + timeDiff
    stdrefbasicv2.relay(["AAPL"], [126740000000], [resolve_time], [3], {"from": accounts[0]})
    assert stdrefbasicv2.pendingRefs("AAPL") == (0, 0, 0, 0)
