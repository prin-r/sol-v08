import pytest
from brownie import accounts, MockBlockHeaderMerkleParts


@pytest.fixture(scope="module")
def mockblockheadermerkleparts():
    return accounts[0].deploy(MockBlockHeaderMerkleParts)


def test_blockheadermerkleparts_getblockheader_success(mockblockheadermerkleparts):
    block_header = mockblockheadermerkleparts.getBlockHeader(
        [
            "0x3561783E9C3BDF932A16580FC0C9CEFFEC4C509073FFF65A42871BFAB64408AE",
            3021518,
            1605721438,
            605059026,
            "0x21114E3076A55C6853B4730FB8678B5BF2314C1DF6DCE169ACEE9AECE893C60F",
            "0xEA01CD62E714B603323A21A4A7382F8AB04788C867A0C99ADE687D00E7D5FE62",
            "0xAA3C7CBEFF135291E6415ECA2528FC98D263B120C67BCECD8D8CCD3253EFECC1",
            "0x68D9EF5EB2AFAF2E36940299C8CDA2F43ACB015FC2D6CAFD2C577CA48F1B2C26",
        ],
        "0x91C6C90AD6765C3080CEF2AEB25B1DBDD8ABE6EB409F400C3D6F8DC2767980F6",
    )
    assert block_header == "0x707C8E52320D12F0A27A0C35B9DB5649428FC535C4C42A73EFD9BDEB3F8A72D5"
