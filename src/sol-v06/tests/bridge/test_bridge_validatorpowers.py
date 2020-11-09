import brownie
from brownie import accounts, Bridge


def test_bridge_validatorpowers_total_validator_power(simple_validator_set):
    totalPower = sum([l[1] for l in simple_validator_set])
    bridge = accounts[0].deploy(Bridge, simple_validator_set)
    assert totalPower == bridge.totalValidatorPower()


def test_bridge_validatorpowers_validator_power(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set)
    for [address, power] in simple_validator_set:
        assert bridge.validatorPowers(address) == power


def test_bridge_update_validator_powers_success(simple_validator_set):
    new_validator_power = ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150]
    bridge = accounts[0].deploy(Bridge, simple_validator_set)
    assert bridge.totalValidatorPower() == 400
    tx = bridge.updateValidatorPowers([new_validator_power])
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 450
    for [address, power] in simple_validator_set:
        if address == new_validator_power[0]:
            assert bridge.validatorPowers(address) == new_validator_power[1]
        else:
            assert bridge.validatorPowers(address) == power


def test_bridge_update_validator_powers_multi_success(simple_validator_set):
    new_validator_powers = [
        ["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150],
        ["0x88e1cd00710495EEB93D4f522d16bC8B87Cb00FE", 0],
        ["0x85109F11A7E1385ee826FbF5dA97bB97dba0D76f", 200],
    ]
    bridge = accounts[0].deploy(Bridge, simple_validator_set)
    assert bridge.totalValidatorPower() == 400
    tx = bridge.updateValidatorPowers(new_validator_powers)
    assert tx.status == 1
    assert bridge.totalValidatorPower() == 550
    for [address, power] in simple_validator_set:
        for [addr2, new_power] in new_validator_powers:
            if addr2 == address:
                assert bridge.validatorPowers(address) == new_power
                break
        else:
            assert bridge.validatorPowers(address) == power


def test_bridge_update_validator_powers_not_owner(simple_validator_set):
    bridge = accounts[0].deploy(Bridge, simple_validator_set)
    start_total_validator_power = 400
    with brownie.reverts("Ownable: caller is not the owner"):
        tx = bridge.updateValidatorPowers(
            [["0x652D89a66Eb4eA55366c45b1f9ACfc8e2179E1c5", 150]], {"from": accounts[1]}
        )
        assert tx.status == 0
    assert bridge.totalValidatorPower() == start_total_validator_power
    for [address, power] in simple_validator_set:
        assert bridge.validatorPowers(address) == power
