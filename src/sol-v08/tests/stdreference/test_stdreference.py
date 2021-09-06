import pytest
import brownie
from brownie import accounts
import time

def test_challenge_invalid_relay_data(stdrefbasicv2, valid_proof):
    stdrefbasicv2.relay(["BTC"], [47287485000001], [1630474425], [1], {"from": accounts[0]})
    stdrefbasicv2.challenge("BTC", valid_proof, {"from": accounts[0]})
    
def test_challenge_invalid_relay_symbol(stdrefbasicv2, valid_proof):
    stdrefbasicv2.relay(["ETH"], [47287485000000], [1630474425], [1], {"from": accounts[0]})
    stdrefbasicv2.challenge("ETH", valid_proof, {"from": accounts[0]}) # ASYMBOL is not in requests

def test_challenge_invalid_oracle_id(stdrefbasicv2, valid_proof_of_other_oracle_id):
    stdrefbasicv2.relay(["ETH"], [3495491660000], [1630474532], [2], {"from": accounts[0]})
    stdrefbasicv2.challenge("ETH", valid_proof_of_other_oracle_id, {"from": accounts[0]})

def test_challenge_valid_relay_data(stdrefbasicv2, valid_proof):
    with brownie.reverts():
        stdrefbasicv2.relay(["BTC"], [47287485000000], [1630474425], [1], {"from": accounts[0]})
        stdrefbasicv2.challenge("BTC", valid_proof, {"from": accounts[0]})

def test_challenge_not_exists_symbol(stdrefbasicv2, valid_proof):
    with brownie.reverts("SYMBOL_IS_NOT_IN_PENDING_REFS"):
        stdrefbasicv2.relay(["BTC"], [47287485000000], [1630474425], [1], {"from": accounts[0]})
        stdrefbasicv2.challenge("ETH", valid_proof, {"from": accounts[0]})

def test_challenge_unmatched_id(stdrefbasicv2, valid_proof):
    with brownie.reverts("REQUEST_ID_IS_NOT_MATCHED"):
        stdrefbasicv2.relay(["BTC"], [47287485000000], [1630474425], [999999999999], {"from": accounts[0]})
        stdrefbasicv2.challenge("BTC", valid_proof, {"from": accounts[0]})

def test_challengebycount_invalid_relay_data(stdrefbasicv2, valid_requests_count_proof):
    stdrefbasicv2.relay(["BTC"], [47287485000000], [1630474425], [999999999999], {"from": accounts[0]})
    stdrefbasicv2.challengeByCount("BTC", valid_requests_count_proof, {"from": accounts[0]})

def test_challengebycount_valid_relay_data(stdrefbasicv2, valid_requests_count_proof):
    stdrefbasicv2.relay(["BTC"], [47287485000000], [1630474425], [1], {"from": accounts[0]})
    with brownie.reverts():
        stdrefbasicv2.challengeByCount("BTC", valid_requests_count_proof, {"from": accounts[0]})

def test_challengebycount_invalid_symbol(stdrefbasicv2, valid_requests_count_proof):
    stdrefbasicv2.relay(["BTC"], [47287485000000], [1630474425], [1], {"from": accounts[0]})
    with brownie.reverts("NO_SYMBOL_IN_PENDING_REFS"):
        stdrefbasicv2.challengeByCount("ETH", valid_requests_count_proof, {"from": accounts[0]})

@pytest.mark.parametrize("timeDiff", [-100, 0, 1, 4])
def test_relay_with_valid_resolvetime(stdrefbasicv2, timeDiff):
    resolve_time = int(time.time()) + timeDiff
    stdrefbasicv2.relay(["BTC"], [47287485000000], [resolve_time], [1], {"from": accounts[0]})
    assert stdrefbasicv2.pendingRefs("BTC") != (0, 0, 0, 0)

@pytest.mark.parametrize("timeDiff", [6, 10, 999999])
def test_relay_with_invalid_resolvetime(stdrefbasicv2, timeDiff):
    resolve_time = int(time.time()) + timeDiff
    stdrefbasicv2.relay(["BTC"], [47287485000000], [resolve_time], [1], {"from": accounts[0]})
    assert stdrefbasicv2.pendingRefs("BTC") == (0, 0, 0, 0)
