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
    assert bridgeinfo_relayed.requestClientID() == "bandchain.js"


def test_bridge_relayandverify_request_oraclescriptid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.oracleScriptID() == 10


def test_bridge_relayandverify_request_params(bridgeinfo_relayed):
    assert (
        bridgeinfo_relayed.params()
        == "0x00000042307866383334636661653566363431303062656337343739393930336563623963353139333635643533386431373862303763333562616663633539663766343331000000005f824b00"
    )


def test_bridge_relayandverify_askcount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.askCount() == 4


def test_bridge_relayandverify_mincount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.minCount() == 4


def test_bridge_relayandverify_response_clientid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.responseClientID() == "bandchain.js"


def test_bridge_relayandverify_requestid(bridgeinfo_relayed):
    assert bridgeinfo_relayed.requestID() == 916026


def test_bridge_relayandverify_anscount(bridgeinfo_relayed):
    assert bridgeinfo_relayed.ansCount() == 4


def test_bridge_relayandverify_request_time(bridgeinfo_relayed):
    ts = time.time()
    assert bridgeinfo_relayed.requestTime() < ts
    assert bridgeinfo_relayed.requestTime() == 1604188873


def test_bridge_relayandverify_resolve_time(bridgeinfo_relayed):
    ts = time.time()
    assert bridgeinfo_relayed.resolveTime() < ts
    assert bridgeinfo_relayed.resolveTime() > bridgeinfo_relayed.requestTime()
    assert bridgeinfo_relayed.resolveTime() == 1604188883


def test_bridge_relayandverify_resolve_status(bridgeinfo_relayed):
    ts = time.time()
    assert bridgeinfo_relayed.resolveStatus() == 1


def test_bridge_relayandverify_resolve_status(bridgeinfo_relayed):
    ts = time.time()
    assert (
        bridgeinfo_relayed.result()
        == "0x00000040ccab8c0bc2337a2afdcd487747bfea7bd12b88dfe0f92ed0894621d7dcc1fb861b894f18b2fd39f2e6c6e3b01eb2ec2a7ad5aaa199d9d7f7dd9c0eb56dba8bf3"
    )
