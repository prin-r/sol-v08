import pytest
import brownie
from brownie import accounts, Bridge

INPUT_SEED_1 = [("mumu1")]
INPUT_SEED_2 = [("mumu2")]

# (os_id,min_count,ask_count)
PROVIDER_SETTING = [(57, 2, 3), (999, 1, 4)]

MOCK_TIMESTAMP = 1631010808
MOCK_BLOCK_HASH = "0x61045f446e2ee45c19788fafb789e9fef9994c8897a4fde62759c1f648f1c1a3"
BOUNTY = 999
EXPECTED_RESULT_1 = "0x857732ef13b3e9119553e0d3a55224784f96399609a71661e47627ed5d8ccff1"
EXPECTED_RESULT_2 = "0x6af5e21fa185bf0bbbb540b2d4ea3be4cc90e261a8f5916f158bdcfaed5219cb"


@pytest.mark.parametrize("", [()])
def test_basic_parameters(vrf_provider):
    oracle_script_id = vrf_provider.oracleScriptID()
    min_count = vrf_provider.minCount()
    ask_count = vrf_provider.askCount()
    task_nonce = vrf_provider.taskNonce()

    assert oracle_script_id == PROVIDER_SETTING[0][0]
    assert min_count == PROVIDER_SETTING[0][1]
    assert ask_count == PROVIDER_SETTING[0][2]
    assert task_nonce == 0


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
def test_set_bridge(vrf_provider, bridge):
    assert vrf_provider.bridge() == bridge.address

    new_bridge = accounts[0].deploy(Bridge, [])
    vrf_provider.setBridge(new_bridge.address, {"from": accounts[0]})
    bridge = vrf_provider.bridge()
    assert bridge == new_bridge.address


@pytest.mark.parametrize("", [()])
def test_set_bridge_script_id_not_owner(vrf_provider, bridge):
    with brownie.reverts("Ownable: caller is not the owner"):
        vrf_provider.setBridge(bridge, {"from": accounts[1]})


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


@pytest.mark.parametrize("", [()])
def test_hex_to_string(vrf_provider):
    s = vrf_provider.b32ToHexString(
        "0x164189923c76e11989a7f855b390667c1b889018c59d2f15d7a6f2d65a7515dd"
    )
    assert s == "164189923c76e11989a7f855b390667c1b889018c59d2f15d7a6f2d65a7515dd"


@pytest.mark.parametrize("", [()])
def test_getting_random_task(vrf_provider):
    some_random_seed = "164189923c76e11989a7f855b390667c1b889018c59d2f15d7a6f2d65a7515dd"
    task = vrf_provider.tasks(some_random_seed)
    assert task == (
        "0x" + ("00" * 20),
        "",
        0,
        0,
        False,
        "0x00",
    )


@pytest.mark.parametrize("client_seed", INPUT_SEED_1)
def test_request_random_data_1(vrf_provider, client_seed):
    nonce = 0
    caller = accounts[1]

    seed = vrf_provider.getSeed(client_seed, MOCK_TIMESTAMP, MOCK_BLOCK_HASH, nonce, caller)
    task = vrf_provider.tasks(seed)
    assert task == (
        "0x" + ("00" * 20),
        "",
        0,
        0,
        False,
        "0x00",
    )

    tx = vrf_provider.requestRandomData(client_seed, {"from": accounts[1], "value": BOUNTY})
    assert tx.status == 1

    events = dict(tx.events["RandomDataRequested"][0])
    assert events["nonce"] == nonce
    assert events["caller"] == caller
    assert events["clientSeed"] == client_seed
    assert events["time"] == MOCK_TIMESTAMP
    assert events["blockHash"] == MOCK_BLOCK_HASH
    assert events["bounty"] == BOUNTY
    assert events["seed"] == seed

    task = vrf_provider.tasks(seed)
    assert task == (
        caller,
        client_seed,
        MOCK_TIMESTAMP,
        BOUNTY,
        False,
        "0x00",
    )


@pytest.mark.parametrize("client_seed", INPUT_SEED_1)
def test_request_random_data_fail_seed_already_exist_for_sender(vrf_provider, client_seed):
    # fail, task already exist
    with brownie.reverts("Seed already existed for this sender"):
        vrf_provider.requestRandomData(client_seed, {"from": accounts[1], "value": 1})


def test_relay_proof_success(vrf_provider, testnet_vrf_proof):
    # oracle_script_id = vrf_provider.oracleScriptID()
    # min_count = vrf_provider.minCount()
    # ask_count = vrf_provider.askCount()
    # assert (oracle_script_id, min_count, ask_count) == PROVIDER_SETTING[1]

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

    seed = vrf_provider.getSeed(INPUT_SEED_1[0], MOCK_TIMESTAMP, MOCK_BLOCK_HASH, 0, accounts[1])
    task = vrf_provider.tasks(seed)

    print(seed)
    print(task)
    print((oracle_script_id, min_count, ask_count))

    assert 0 == 1

    tx = vrf_provider.relayProof(testnet_vrf_proof, {"from": accounts[2]})
    assert tx.status == 1

    seed = vrf_provider.getSeed(INPUT_SEED_1[0], MOCK_TIMESTAMP, MOCK_BLOCK_HASH, 0, accounts[1])
    task = vrf_provider.tasks(seed)
    assert task == (
        accounts[1],
        INPUT_SEED_1[0],
        MOCK_TIMESTAMP,
        BOUNTY,
        True,
        EXPECTED_RESULT_1,
    )

    # after relay balance
    # relayer must receive bounty
    assert accounts[2].balance() == account2_prev_balance + BOUNTY


@pytest.mark.parametrize("client_seed", INPUT_SEED_2)
def test_request_random_data_2(vrf_provider, client_seed):
    pass
    # nonce = 0
    # caller = accounts[1]

    # seed = vrf_provider.getSeed(client_seed, MOCK_TIMESTAMP, MOCK_BLOCK_HASH, nonce, caller)

    # task = vrf_provider.tasks(seed)
    # assert task == (
    #     "0x" + ("00" * 20),
    #     "",
    #     0,
    #     0,
    #     False,
    #     "0x00",
    # )

    # tx = vrf_provider.requestRandomData(client_seed, {"from": accounts[1], "value": BOUNTY})
    # assert tx.status == 1

    # events = dict(tx.events["RandomDataRequested"][0])
    # assert events["nonce"] == nonce
    # assert events["caller"] == caller
    # assert events["clientSeed"] == client_seed
    # assert events["time"] == MOCK_TIMESTAMP
    # assert events["blockHash"] == MOCK_BLOCK_HASH
    # assert events["bounty"] == BOUNTY
    # assert events["seed"] == seed


def test_relay_proof_success_2(vrf_provider, testnet_vrf_proof_1_4):
    pass
    # nonce = 0
    # caller = accounts[2]
    # client_seed = INPUT_SEED_2[0]
    # seed = vrf_provider.getSeed(client_seed, MOCK_TIMESTAMP, MOCK_BLOCK_HASH, nonce, caller)

    # tx = vrf_provider.requestRandomData(client_seed, {"from": accounts[2], "value": BOUNTY})
    # assert tx.status == 1

    # print(seed)

    # assert 0 == 1

    # # set back the parameters
    # vrf_provider.setMinCount(PROVIDER_SETTING[1][1], {"from": accounts[0]})
    # vrf_provider.setAskCount(PROVIDER_SETTING[1][2], {"from": accounts[0]})
    # min_count = vrf_provider.minCount()
    # ask_count = vrf_provider.askCount()
    # assert (min_count, ask_count) == PROVIDER_SETTING[1][1:]

    # # before relay balance
    # account2_prev_balance = accounts[2].balance()

    # tx = vrf_provider.relayProof(testnet_vrf_proof_1_4, {"from": accounts[2]})
    # assert tx.status == 1

    # task = vrf_provider.tasks(seed)
    # assert task == (
    #     accounts[2],
    #     INPUT_SEED_2[0],
    #     MOCK_TIMESTAMP,
    #     BOUNTY,
    #     True,
    #     EXPECTED_RESULT_2,
    # )

    # # after relay balance
    # # relayer must receive bounty
    # assert accounts[2].balance() == account2_prev_balance + BOUNTY
