import pytest
import brownie

REQUEST_PACKET = ["beeb", 1, "0x0000000342544300000000000003e8", 4, 4]
RESPONSE_PACKET = [
    "beeb",
    1,
    4,
    1591598291,
    1591598295,
    1,
    "0x0000000000948e69",
]
VERSION = "163"

INVALID_REQUEST_PACKET = ["wrong_id", 1, "0x0000000342544300000000000003e8", 4, 4]
INVALID_RESPONSE_PACKET = [
    "wrong_id",
    1,
    4,
    1591598291,
    1591598295,
    1,
    "0x0000000000948e69",
]

MERKLE_PATHS = [
    [
        True,  # isDataOnRight
        "2",  # subtreeHeight
        "3",  # subtreeSize
        "180",  # subtreeVersion
        "0x4D4479F8CF02CBA65F95231B06EEAA51E99F75A153C3ED28D9A86B565DE59306",  # siblingHash
    ],
    [
        True,  # isDataOnRight
        "3",  # subtreeHeight
        "5",  # subtreeSize
        "180",  # subtreeVersion
        "0x8861AD25F99A677D4934541A99928CDBE18BBF34EE39D754E93CCE090BE70502",  # siblingHash
    ],
    [
        True,  # isDataOnRight
        "4",  # subtreeHeight
        "9",  # subtreeSize
        "180",  # subtreeVersion
        "0x5D162C955AE030390CEA63CA7ED8BA72B7A49E0BC73DAEA23CF6B79E8899C49C",  # siblingHash
    ],
    [
        True,  # isDataOnRight
        "5",  # subtreeHeight
        "16",  # subtreeSize
        "180",  # subtreeVersion
        "0x08DD24B96C3C9413BA46A7149232C18AD66DB68AC04CF2A770B707B6D29FC8F7",  # siblingHash
    ],
    [
        True,  # isDataOnRight
        "6",  # subtreeHeight
        "24",  # subtreeSize
        "180",  # subtreeVersion
        "0x32D2E1CC89F3FBD139C35B5D5FE6430799AEEFD495C882C419A120B7257E3F5A",  # siblingHash
    ],
    [
        True,  # isDataOnRight
        "7",  # subtreeHeight
        "62",  # subtreeSize
        "181",  # subtreeVersion
        "0x691B2504CD253868BCCD43774C8B8DBFA1E2D0D41C07C23F2F1237FCF0D2F0D8",  # siblingHash
    ],
]

INCOMPLETE_MERKLE_PATHS = [
    [
        True,  # isDataOnRight
        "2",  # subtreeHeight
        "3",  # subtreeSize
        "180",  # subtreeVersion
        "0x4D4479F8CF02CBA65F95231B06EEAA51E99F75A153C3ED28D9A86B565DE59306",  # siblingHash
    ],
    [
        True,  # isDataOnRight
        "3",  # subtreeHeight
        "5",  # subtreeSize
        "180",  # subtreeVersion
        "0x8861AD25F99A677D4934541A99928CDBE18BBF34EE39D754E93CCE090BE70502",  # siblingHash
    ],
    [
        True,  # isDataOnRight
        "7",  # subtreeHeight
        "62",  # subtreeSize
        "181",  # subtreeVersion
        "0x691B2504CD253868BCCD43774C8B8DBFA1E2D0D41C07C23F2F1237FCF0D2F0D8",  # siblingHash
    ],
]


@pytest.fixture(scope="module")
def set_oracle_state(mockbridge):
    mockbridge.setOracleState(
        "182",  # _blockHeight
        "0xB59AD73DB9147F6AC7C88A64B1BAD51C90F8C48B4487ADA9276A323808E56E3E",  # _oracleIAVLStateHash)
    )
    return mockbridge


def test_bridge_verifyoracledata_success(set_oracle_state):
    (req, res) = set_oracle_state.verifyOracleData(
        "182",
        REQUEST_PACKET,  # _requestPacket
        RESPONSE_PACKET,  # _responsePacket
        VERSION,  # _version
        MERKLE_PATHS,
    )
    for i in range(len(REQUEST_PACKET)):
        assert req[i] == REQUEST_PACKET[i]
    for i in range(len(RESPONSE_PACKET)):
        assert res[i] == RESPONSE_PACKET[i]


def test_bridge_verifyoracledata_unrelayed_block(set_oracle_state):
    with brownie.reverts("NO_ORACLE_ROOT_STATE_DATA"):
        tx = set_oracle_state.verifyOracleData(
            "9999",  # _blockHeight
            REQUEST_PACKET,  # _requestPacket
            RESPONSE_PACKET,  # _responsePacket
            VERSION,  # _version
            MERKLE_PATHS,
        )
        assert tx.status == 0


def test_bridge_verifyoracledata_invalid_data(set_oracle_state):
    with brownie.reverts("INVALID_ORACLE_DATA_PROOF"):
        tx = set_oracle_state.verifyOracleData(
            "182",  # _blockHeight
            INVALID_REQUEST_PACKET,  # _requestPacket
            INVALID_RESPONSE_PACKET,  # _responsePacket
            "163",  # _version
            MERKLE_PATHS,
        )
        assert tx.status == 0


def test_bridge_verifyoracledata_invalid_merkle_proof_paths(set_oracle_state):
    with brownie.reverts("INVALID_ORACLE_DATA_PROOF"):
        tx = set_oracle_state.verifyOracleData(
            "182", REQUEST_PACKET, RESPONSE_PACKET, "163", INCOMPLETE_MERKLE_PATHS
        )
        assert tx.status == 0
