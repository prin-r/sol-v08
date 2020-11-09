import pytest
from brownie import accounts, MockPackets


@pytest.fixture(scope="module")
def mockpackets():
    return accounts[0].deploy(MockPackets)


def test_packets_encoderequestpacket_success(mockpackets):
    encoded = mockpackets.encodeRequestPacket(
        [
            "beeb",
            1,
            "0x030000004254436400000000000000",
            1,
            1,
        ]
    )
    assert (
        encoded
        == "0x000000046265656200000000000000010000000f03000000425443640000000000000000000000000000010000000000000001"
    )


def test_packets_encoderesponsepacket_success(mockpackets):
    encoded = mockpackets.encodeResponsePacket(
        [
            "beeb",
            1,
            1,
            1589535020,
            1589535022,
            1,
            "0x4bb10e0000000000",
        ]
    )
    assert (
        encoded
        == "0x000000046265656200000000000000010000000000000001000000005ebe612c000000005ebe612e00000001000000084bb10e0000000000"
    )


def test_packets_getencodedresult_success(mockpackets):
    encoded_result = mockpackets.getEncodedResult(
        ["beeb", 1, "0x030000004254436400000000000000", 1, 1],
        ["beeb", 1, 1, 1589535020, 1589535022, 1, "0x4bb10e0000000000"],
    )
    assert (
        encoded_result
        == "0x000000046265656200000000000000010000000f03000000425443640000000000000000000000000000010000000000000001000000046265656200000000000000010000000000000001000000005ebe612c000000005ebe612e00000001000000084bb10e0000000000"
    )
    encoded_result = mockpackets.getEncodedResult(
        ["", 1, "0x030000004254436400000000000000", 1, 1],
        ["", 1, 1, 1590490752, 1590490756, 1, "0x568c0d0000000000"],
    )
    assert (
        encoded_result
        == "0x0000000000000000000000010000000f030000004254436400000000000000000000000000000100000000000000010000000000000000000000010000000000000001000000005eccf680000000005eccf6840000000100000008568c0d0000000000"
    )
