from brownie.network import account
import brownie
from brownie import accounts, MockVRFConsumer

INPUT_SEED_TIME = [("mumu1", 12345678)]
BOUNTY = 999


def test_vrf_request_by_consumer(vrf_provider, mock_vrf_consumer):
    key = vrf_provider.getKey(mock_vrf_consumer.address, *INPUT_SEED_TIME[0])
    # before request
    task = vrf_provider.tasks(key)
    assert task == (
        "0x0000000000000000000000000000000000000000",
        0,
        False,
        "0x00",
    )

    mock_vrf_consumer.requestRandomDataFromProvider(
        *INPUT_SEED_TIME[0], {"from": accounts[1], "value": BOUNTY}
    )

    # after request
    task = vrf_provider.tasks(key)
    assert task == (
        mock_vrf_consumer.address,
        BOUNTY,
        False,
        "0x00",
    )


def test_vrf_request_relay_consume_fail_task_not_found(vrf_provider, testnet_vrf_proof):
    new_consumer = accounts[0].deploy(MockVRFConsumer, vrf_provider.address)
    with brownie.reverts("Task not found"):
        vrf_provider.relayProof(new_consumer.address, testnet_vrf_proof, {"from": accounts[1]})


def test_vrf_request_relay_consume_fail_os_id_not_match(
    mock_vrf_consumer, vrf_provider, testnet_vrf_proof_wrong_os
):
    with brownie.reverts("Oracle Script ID not match"):
        vrf_provider.relayProof(
            mock_vrf_consumer.address, testnet_vrf_proof_wrong_os, {"from": accounts[1]}
        )


def test_vrf_request_relay_consume_fail_min_count_not_match(
    mock_vrf_consumer, vrf_provider, testnet_vrf_proof_wrong_min_count
):
    with brownie.reverts("Min Count not match"):
        vrf_provider.relayProof(
            mock_vrf_consumer.address, testnet_vrf_proof_wrong_min_count, {"from": accounts[1]}
        )


def test_vrf_request_relay_consume_fail_ask_count_not_match(
    mock_vrf_consumer, vrf_provider, testnet_vrf_proof_wrong_ask_count
):
    with brownie.reverts("Ask Count not match"):
        vrf_provider.relayProof(
            mock_vrf_consumer.address, testnet_vrf_proof_wrong_ask_count, {"from": accounts[1]}
        )


def test_vrf_request_relay_consume_success(vrf_provider, mock_vrf_consumer, testnet_vrf_proof):
    assert mock_vrf_consumer.latestSeed() == ""
    assert mock_vrf_consumer.latestTime() == 0
    assert mock_vrf_consumer.latestResult() == "0x00"

    account2_prev_balance = accounts[2].balance()
    tx = vrf_provider.relayProof(
        mock_vrf_consumer.address, testnet_vrf_proof, {"from": accounts[2]}
    )
    assert tx.status == 1

    # check relayer balance
    assert accounts[2].balance() == account2_prev_balance + BOUNTY

    key = vrf_provider.getKey(mock_vrf_consumer.address, *INPUT_SEED_TIME[0])
    task = vrf_provider.tasks(key)
    assert task == (
        mock_vrf_consumer.address,
        BOUNTY,
        True,
        "0xab28fb90b6c2826017165c85ad7f6eb982b72173e6fbb1913c0a3b1b5d54cc3d",
    )

    assert mock_vrf_consumer.latestSeed() == INPUT_SEED_TIME[0][0]
    assert mock_vrf_consumer.latestTime() == INPUT_SEED_TIME[0][1]
    assert (
        mock_vrf_consumer.latestResult()
        == "0xab28fb90b6c2826017165c85ad7f6eb982b72173e6fbb1913c0a3b1b5d54cc3d"
    )


def test_vrf_request_relay_consume_fail_task_already_resolved(
    vrf_provider, mock_vrf_consumer, testnet_vrf_proof
):
    with brownie.reverts("Task already resolved"):
        vrf_provider.relayProof(mock_vrf_consumer.address, testnet_vrf_proof, {"from": accounts[2]})