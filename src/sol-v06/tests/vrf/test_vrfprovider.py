import pytest
import brownie
from brownie import accounts, MockBridgeForVRF

INPUT_SEED_TIME_1 = [("mumu1", 12345678)]
INPUT_SEED_TIME_2 = [("mumu2", 87654321)]

# (os_id,min_count,ask_count)
PROVIDER_SETTING = [(38, 2, 3), (999, 1, 4)]

BOUNTY = 999
EXPECTED_RESULT_1 = "0xab28fb90b6c2826017165c85ad7f6eb982b72173e6fbb1913c0a3b1b5d54cc3d"
EXPECTED_RESULT_2 = "0xdb2807c8220687a9aadeb480042121a981d1cdff29170642e91d979a834b51c5"


@pytest.mark.parametrize("", [()])
def test_basic_parameters(vrf_provider):
    oracle_script_id = vrf_provider.oracleScriptID()
    min_count = vrf_provider.minCount()
    ask_count = vrf_provider.askCount()

    assert oracle_script_id == PROVIDER_SETTING[0][0]
    assert min_count == PROVIDER_SETTING[0][1]
    assert ask_count == PROVIDER_SETTING[0][2]


@pytest.mark.parametrize("_oracleScriptID", [PROVIDER_SETTING[1][0]])
def test_set_oracle_script_id(vrf_provider, _oracleScriptID):
    oracle_script_id = vrf_provider.oracleScriptID()
    assert oracle_script_id == PROVIDER_SETTING[0][0]

    vrf_provider.setOracleScriptID(_oracleScriptID, {"from": accounts[0]})
    oracle_script_id = vrf_provider.oracleScriptID()
    assert oracle_script_id == PROVIDER_SETTING[1][0]


@pytest.mark.parametrize("_oracleScriptID", [PROVIDER_SETTING[1][0]])
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


@pytest.mark.parametrize("_minCount", [PROVIDER_SETTING[1][1]])
def test_set_min_count(vrf_provider, _minCount):
    min_count = vrf_provider.minCount()
    assert min_count == PROVIDER_SETTING[0][1]

    vrf_provider.setMinCount(_minCount, {"from": accounts[0]})
    min_count = vrf_provider.minCount()
    assert min_count == PROVIDER_SETTING[1][1]


@pytest.mark.parametrize("_minCount", [PROVIDER_SETTING[0][1]])
def test_set_min_count_not_owner(vrf_provider, _minCount):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider.setMinCount(_minCount, {"from": accounts[1]})


@pytest.mark.parametrize("_askCount", [PROVIDER_SETTING[1][2]])
def test_set_ask_count(vrf_provider, _askCount):
    ask_count = vrf_provider.askCount()
    assert ask_count == PROVIDER_SETTING[0][2]

    vrf_provider.setAskCount(_askCount, {"from": accounts[0]})
    ask_count = vrf_provider.askCount()
    assert ask_count == PROVIDER_SETTING[1][2]


@pytest.mark.parametrize("_askCount", [PROVIDER_SETTING[1][2]])
def test_set_ask_count_not_owner(vrf_provider, _askCount):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider.setAskCount(_askCount, {"from": accounts[1]})


@pytest.mark.parametrize("seed,time", INPUT_SEED_TIME_1)
def test_request_random_data_1(vrf_provider, seed, time):
    key = vrf_provider.getKey(accounts[1].address, seed, time)
    assert key == "0x164189923c76e11989a7f855b390667c1b889018c59d2f15d7a6f2d65a7515dd"

    task = vrf_provider.tasks(key)
    assert task == (
        "0x" + ("0" * 40),
        0,
        False,
        "0x00",
    )

    vrf_provider.requestRandomData(seed, time, {"from": accounts[1], "value": BOUNTY})
    task = vrf_provider.tasks(key)
    assert task == (
        accounts[1].address,
        BOUNTY,
        False,
        "0x00",
    )


def test_relay_proof_success(vrf_provider, testnet_vrf_proof):
    oracle_script_id = vrf_provider.oracleScriptID()
    min_count = vrf_provider.minCount()
    ask_count = vrf_provider.askCount()
    assert (oracle_script_id, min_count, ask_count) == PROVIDER_SETTING[1]

    # set back the parameters
    vrf_provider.setOracleScriptID(PROVIDER_SETTING[0][0], {"from": accounts[0]})
    vrf_provider.setMinCount(PROVIDER_SETTING[0][1], {"from": accounts[0]})
    vrf_provider.setAskCount(PROVIDER_SETTING[0][2], {"from": accounts[0]})
    oracle_script_id = vrf_provider.oracleScriptID()
    min_count = vrf_provider.minCount()
    ask_count = vrf_provider.askCount()
    assert (oracle_script_id, min_count, ask_count) == PROVIDER_SETTING[0]

    # before relay balance
    account2_prev_balance = accounts[2].balance()

    tx = vrf_provider.relayProof(accounts[1].address, testnet_vrf_proof, {"from": accounts[2]})
    assert tx.status == 1

    key = vrf_provider.getKey(accounts[1].address, *INPUT_SEED_TIME_1[0])
    task = vrf_provider.tasks(key)
    assert task == (
        accounts[1].address,
        BOUNTY,
        True,
        EXPECTED_RESULT_1,
    )

    # after relay balance
    # relayer must receive bounty
    assert accounts[2].balance() == account2_prev_balance + BOUNTY


@pytest.mark.parametrize("seed,time", INPUT_SEED_TIME_2)
def test_request_random_data_2(vrf_provider, seed, time):
    key = vrf_provider.getKey(accounts[1].address, seed, time)
    assert key == "0x184ad0e46849626210e7623814c6d6ea78a15382cfe6c11734ff0b963b9d83bc"

    task = vrf_provider.tasks(key)
    assert task == (
        "0x" + ("0" * 40),
        0,
        False,
        "0x00",
    )

    vrf_provider.requestRandomData(seed, time, {"from": accounts[1], "value": BOUNTY})
    task = vrf_provider.tasks(key)
    assert task == (
        accounts[1].address,
        BOUNTY,
        False,
        "0x00",
    )


def test_relay_proof_success_2(vrf_provider, testnet_vrf_proof_1_4):
    min_count = vrf_provider.minCount()
    ask_count = vrf_provider.askCount()
    assert (min_count, ask_count) == PROVIDER_SETTING[0][1:]

    # set back the parameters
    vrf_provider.setMinCount(PROVIDER_SETTING[1][1], {"from": accounts[0]})
    vrf_provider.setAskCount(PROVIDER_SETTING[1][2], {"from": accounts[0]})
    min_count = vrf_provider.minCount()
    ask_count = vrf_provider.askCount()
    assert (min_count, ask_count) == PROVIDER_SETTING[1][1:]

    # before relay balance
    account2_prev_balance = accounts[2].balance()

    tx = vrf_provider.relayProof(accounts[1].address, testnet_vrf_proof_1_4, {"from": accounts[2]})
    assert tx.status == 1

    key = vrf_provider.getKey(accounts[1].address, *INPUT_SEED_TIME_2[0])
    task = vrf_provider.tasks(key)
    assert task == (accounts[1].address, BOUNTY, True, EXPECTED_RESULT_2)

    # after relay balance
    # relayer must receive bounty
    assert accounts[2].balance() == account2_prev_balance + BOUNTY


@pytest.mark.parametrize("seed,time", INPUT_SEED_TIME_1)
def test_request_random_data_fail_already_exist(vrf_provider, seed, time):
    # fail, task already exist
    with brownie.reverts("Task already existed"):
        vrf_provider.requestRandomData(seed, time, {"from": accounts[1], "value": 1})
