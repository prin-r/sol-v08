import pytest
import brownie
from brownie import accounts, MockBridgeForVRF

OS_ID = 38
MIN_COUNT = 2
ASK_COUNT = 3

INPUT_SEED_TIME = [("mumu1", 12345678)]
INPUT_NEW_OS_ID = [(999)]
INPUT_NEW_MIN_COUNT = [(2)]
INPUT_NEW_ASK_COUNT = [(3)]


@pytest.mark.parametrize("", [()])
def test_basic_parameters(vrf_provider):
    oracle_script_id = vrf_provider.oracleScriptID()
    min_count = vrf_provider.minCount()
    ask_count = vrf_provider.askCount()

    assert oracle_script_id == OS_ID
    assert min_count == MIN_COUNT
    assert ask_count == ASK_COUNT


@pytest.mark.parametrize("_oracleScriptID", INPUT_NEW_OS_ID)
def test_set_oracle_script_id(vrf_provider, _oracleScriptID):
    oracle_script_id = vrf_provider.oracleScriptID()
    assert oracle_script_id == OS_ID

    vrf_provider.setOracleScriptID(_oracleScriptID, {"from": accounts[0]})
    oracle_script_id = vrf_provider.oracleScriptID()
    assert oracle_script_id == INPUT_NEW_OS_ID[0]


@pytest.mark.parametrize("_oracleScriptID", INPUT_NEW_OS_ID)
def test_set_oracle_script_id_not_owner(vrf_provider, _oracleScriptID):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider.setOracleScriptID(_oracleScriptID, {"from": accounts[1]})


@pytest.mark.parametrize("", [()])
def test_set_bridge(vrf_provider, mock_bridge_for_vrf):
    bridge = vrf_provider.bridge()
    assert bridge == mock_bridge_for_vrf.address

    new_bridge = accounts[0].deploy(MockBridgeForVRF)
    vrf_provider.setBridge(new_bridge.address, {"from": accounts[0]})
    bridge = vrf_provider.bridge()
    assert bridge == new_bridge.address


@pytest.mark.parametrize("", [()])
def test_set_bridge_script_id_not_owner(vrf_provider, mock_bridge_for_vrf):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider.setBridge(mock_bridge_for_vrf, {"from": accounts[1]})


@pytest.mark.parametrize("_minCount", INPUT_NEW_MIN_COUNT)
def test_set_min_count(vrf_provider, _minCount):
    min_count = vrf_provider.minCount()
    assert min_count == MIN_COUNT

    vrf_provider.setMinCount(_minCount, {"from": accounts[0]})
    min_count = vrf_provider.minCount()
    assert min_count == INPUT_NEW_MIN_COUNT[0]


@pytest.mark.parametrize("_minCount", INPUT_NEW_MIN_COUNT)
def test_set_min_count_not_owner(vrf_provider, _minCount):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider.setMinCount(_minCount, {"from": accounts[1]})


@pytest.mark.parametrize("_askCount", INPUT_NEW_ASK_COUNT)
def test_set_ask_count(vrf_provider, _askCount):
    ask_count = vrf_provider.askCount()
    assert ask_count == ASK_COUNT

    vrf_provider.setAskCount(_askCount, {"from": accounts[0]})
    ask_count = vrf_provider.askCount()
    assert ask_count == INPUT_NEW_ASK_COUNT[0]


@pytest.mark.parametrize("_askCount", INPUT_NEW_MIN_COUNT)
def test_set_ask_count_not_owner(vrf_provider, _askCount):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider.setAskCount(_askCount, {"from": accounts[1]})


@pytest.mark.parametrize("seed,time", INPUT_SEED_TIME)
def test_request_random_data(vrf_provider, seed, time):
    key = vrf_provider.getKey(accounts[1].address, seed, time)
    assert key == "0x164189923c76e11989a7f855b390667c1b889018c59d2f15d7a6f2d65a7515dd"

    task = vrf_provider.tasks(key)
    assert task == (
        "0x0000000000000000000000000000000000000000",
        0,
        False,
        "0x00",
    )

    vrf_provider.requestRandomData(seed, time, {"from": accounts[1], "value": 1})
    task = vrf_provider.tasks(key)
    assert task == (
        accounts[1].address,
        1,
        False,
        "0x00",
    )


@pytest.mark.parametrize("seed,time", INPUT_SEED_TIME)
def test_request_random_data_fail_already_exist(vrf_provider, seed, time):
    # fail, task already exist
    with brownie.reverts("Task already existed"):
        vrf_provider.requestRandomData(seed, time, {"from": accounts[1], "value": 1})
