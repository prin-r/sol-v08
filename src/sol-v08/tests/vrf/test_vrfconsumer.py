from brownie.network import account
import brownie
from brownie import accounts, MockVRFConsumer

INPUT_SEED_TIME = [("mumu1")]
BOUNTY = 999
MOCK_TIMESTAMP = 1631010808
MOCK_BLOCK_HASH = "0x61045f446e2ee45c19788fafb789e9fef9994c8897a4fde62759c1f648f1c1a3"
EXPECTED_RESULT = "0x81053ec6ce07eab1fe83d0c408a72c7fe05b3d1bde271db386e8c7e7eb31a8fe"


def test_vrf_request_by_consumer(vrf_provider, mock_vrf_consumer):
    nonce = 0
    caller = mock_vrf_consumer.address
    client_seed = INPUT_SEED_TIME[0]

    seed = vrf_provider.getSeed(client_seed, MOCK_TIMESTAMP, MOCK_BLOCK_HASH, nonce, caller)
    # before request
    task = vrf_provider.tasks(seed)
    assert task == (
        "0x" + ("00" * 20),
        "",
        0,
        0,
        False,
        "0x00",
    )

    tx = mock_vrf_consumer.requestRandomDataFromProvider(
        client_seed, {"from": accounts[1], "value": BOUNTY}
    )
    assert tx.status == 1

    # after request
    task = vrf_provider.tasks(seed)
    assert task == (
        caller,
        client_seed,
        MOCK_TIMESTAMP,
        BOUNTY,
        False,
        "0x00",
    )


def test_consume_fail_not_the_provider(mock_vrf_consumer):
    fake_result = "a" * 64
    with brownie.reverts("Caller is not the provider"):
        mock_vrf_consumer.consume(
            INPUT_SEED_TIME[0], MOCK_TIMESTAMP, fake_result, {"from": accounts[1]}
        )


def test_vrf_request_relay_consume_fail_task_not_found(vrf_provider, testnet_vrf_proof):
    with brownie.reverts("Task not found"):
        vrf_provider.relayProof(testnet_vrf_proof, {"from": accounts[1]})


def test_vrf_request_relay_consume_fail_os_id_not_match(vrf_provider, testnet_vrf_proof_wrong_os):
    with brownie.reverts("Oracle Script ID not match"):
        vrf_provider.relayProof(testnet_vrf_proof_wrong_os, {"from": accounts[1]})


def test_vrf_request_relay_consume_fail_min_count_not_match(
    vrf_provider, testnet_vrf_proof_wrong_min_count
):
    with brownie.reverts("Min Count not match"):
        vrf_provider.relayProof(testnet_vrf_proof_wrong_min_count, {"from": accounts[1]})


def test_vrf_request_relay_consume_fail_ask_count_not_match(
    vrf_provider, testnet_vrf_proof_wrong_ask_count
):
    with brownie.reverts("Ask Count not match"):
        vrf_provider.relayProof(testnet_vrf_proof_wrong_ask_count, {"from": accounts[1]})


def test_vrf_request_relay_task_not_found(vrf_provider, testnet_vrf_proof):
    with brownie.reverts("Task not found"):
        vrf_provider.relayProof(testnet_vrf_proof, {"from": accounts[2]})


def test_vrf_request_relay_consume_success(
    vrf_provider, mock_vrf_consumer, testnet_vrf_proof_for_consumer
):
    assert mock_vrf_consumer.latestSeed() == ""
    assert mock_vrf_consumer.latestTime() == 0
    assert mock_vrf_consumer.latestResult() == "0x00"

    account2_prev_balance = accounts[2].balance()
    tx = vrf_provider.relayProof(testnet_vrf_proof_for_consumer, {"from": accounts[2]})
    assert tx.status == 1

    # relayer must receive the bounty
    assert accounts[2].balance() == account2_prev_balance + BOUNTY

    assert mock_vrf_consumer.latestSeed() == INPUT_SEED_TIME[0]
    assert mock_vrf_consumer.latestTime() == MOCK_TIMESTAMP
    assert mock_vrf_consumer.latestResult() == EXPECTED_RESULT


def test_vrf_request_relay_consume_fail_task_already_resolved(
    vrf_provider, testnet_vrf_proof_for_consumer
):
    with brownie.reverts("Task already resolved"):
        vrf_provider.relayProof(testnet_vrf_proof_for_consumer, {"from": accounts[2]})
