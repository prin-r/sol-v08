import brownie
from brownie import accounts
import time


def test_bridge_relayandverify_bridge_success(bridge, valid_proof):
    tx = bridge.relayAndVerify(valid_proof, {"from": accounts[0]})
    assert tx.status == 1


def test_bridge_relayandverify_bridge_fail(bridge):
    with brownie.reverts():
        tx = bridge.relayAndVerify("0x00", {"from": accounts[0]})
        tx.status == 0


def test_bridge_relayandverify_bridgeinfo_success(bridgeinfo, valid_proof):
    tx = bridgeinfo.relayAndSave(valid_proof, {"from": accounts[0]})
    assert tx.status == 1


def test_bridge_relayandverify_bridgeinfo_success(bridgeinfo):
    with brownie.reverts():
        tx = bridgeinfo.relayAndSave("0x00", {"from": accounts[0]})
        tx.status == 0


def test_bridge_relay_request_clientid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.ClientID() == "from_scan"


def test_bridge_relayandverify_request_oraclescriptid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.oracleScriptID() == 1


def test_bridge_relayandverify_request_params(bridgeinfo_relayed):
    assert (
        bridgeinfo_relayed.params()
        == "0x0000000342544300000000000f4240"
    )


def test_bridge_relayandverify_askcount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.askCount() == 1


def test_bridge_relayandverify_mincount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.minCount() == 1


def test_bridge_relayandverify_requestid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.requestID() == 1


def test_bridge_relayandverify_anscount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.ansCount() == 1


def test_bridge_relayandverify_request_time(bridgeinfo_relayed):
    ts = time.time()
    assert bridgeinfo_relayed.requestTime() < ts
    assert bridgeinfo_relayed.requestTime() == 1622111198


def test_bridge_relayandverify_resolve_time(bridgeinfo_relayed):
    ts = time.time()
    assert bridgeinfo_relayed.resolveTime() < ts
    assert bridgeinfo_relayed.resolveTime() > bridgeinfo_relayed.requestTime()
    assert bridgeinfo_relayed.resolveTime() == 1622111200


def test_bridge_relayandverify_resolve_status(bridgeinfo_relayed):
    ts = time.time()
    assert bridgeinfo_relayed.resolveStatus() == 1


def test_bridge_relayandverify_resolve_status(bridgeinfo_relayed):
    ts = time.time()
    assert (
        bridgeinfo_relayed.result()
        == "0x000000092b6826f2"
    )
