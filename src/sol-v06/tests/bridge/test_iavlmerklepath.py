import pytest
from brownie import accounts, MockIAVLMerklePath


@pytest.fixture(scope="module")
def mockiavlmerklepath():
    return accounts[0].deploy(MockIAVLMerklePath)


def test_iavlmerklepath_getparenthash_success(mockiavlmerklepath):
    parent_hash = mockiavlmerklepath.getParentHash(
        [
            True,
            1,
            2,
            599,
            "0x1459BBC7DB7FFCCE3DECEEA3DF062968F4E3D2B206B93D59FA936E334B9EC434",
        ],
        "0x5c67c4993b78e7900b56f86dfe426e30dbf597e152918e8ebd029103fae32905",
    )
    assert (
        parent_hash
        == "0x3f590cfc6a2568ef992f39ace15ca3256b6ee7bc06b81b847455d4190d67d775"
    )
    parent_hash = mockiavlmerklepath.getParentHash(
        [
            True,
            2,
            4,
            599,
            "0x5B70BFADD16EC95409072FB3686BF2BFEC48113F96CACA88397883110C672F13",
        ],
        "0x3f590cfc6a2568ef992f39ace15ca3256b6ee7bc06b81b847455d4190d67d775",
    )
    assert (
        parent_hash
        == "0x56e60e1bf390a5045077f34cb6f96b91f3f3d79965b23e4d649d62b3f58dfb0a"
    )
    parent_hash = mockiavlmerklepath.getParentHash(
        [
            True,
            3,
            8,
            599,
            "0x709E1C73511B24EFDD9B8D3CD717A5210BA20E2411A8529E8B642C54FB002DC4",
        ],
        "0x56e60e1bf390a5045077f34cb6f96b91f3f3d79965b23e4d649d62b3f58dfb0a",
    )
    assert (
        parent_hash
        == "0x320fec0587c84c21c33d8c2361c06e0e51354f5b9d353c3f3dc3a123e97cbded"
    )
    parent_hash = mockiavlmerklepath.getParentHash(
        [
            True,
            4,
            13,
            663,
            "0xD546BD0A2922A50FD184831DACA108E742A14C3D339C92A7467D31BCD7B0DAD2",
        ],
        "0x320fec0587c84c21c33d8c2361c06e0e51354f5b9d353c3f3dc3a123e97cbded",
    )
    assert (
        parent_hash
        == "0xd0ee29edb1a80f80b6dc2c058b07e85846e2a1d4ec49fce1dd0cf1b946ccf456"
    )
