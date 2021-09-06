import pytest
from brownie import accounts, MockReceiver
import time

VALID_MULTI_PROOF = "000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000007E00000000000000000000000000000000000000000000000000000000000000780F083538B889DB1C042D7B2A483636B8747A4B9BB9453608EE16D02EC6A27F1C468E763BF8DC558BC1E2B32619F012123EAFD4083A12BF59AB4927C230475D5D84726B7F490EB59EB209CA3F11C30263E7F47A2913BF2A4B01FF1BD47BF0F427DB125AC2FE51484F660E16D288364D1B5EAD612111397F3124A596E3B00313C4CDC774CFA98070199004BE730C189D8F02004D18351545F439C58136B2996B083C9C8849ED125CC7681329C4D27B83B1FC8ACF7A865C9D1D1DF575CCA56F48DBE3F02642D9E70D5C1C493A4F732BFE9C9B95A4A42651703B816EDCFC8FADA5312000000000000000000000000000000000000000000000000000000000000C3500000000000000000000000000000000000000000000000000000000061263E0E000000000000000000000000000000000000000000000000000000001B037C0429E0CA2662475B6F62B86310FB49635F745E1157B7E247CAD1310DC34C5B5A0EA772AD11CB4A24B18B0A10FDF92D1B7BDDC632476732C7461B554F9593EB11759FB9C7533CAF1D218DA3AF6D277F6B101C42E3C3B75D784242DA663604DD53C29028C2AEF0CDD1F9746B1B2DEFFA898BFDE0B70CD58BAFB6211FABC8623F749400000000000000000000000000000000000000000000000000000000000001E00000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000001C0000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000004407FE6087623FD58F83E881DCF17E507B50FE7BE2A82D783C470BBDDF1FF30992004BB6BE1460632B1636664C4FCE1E2F5232CB09C37CF73508606025967FC3FAA000000000000000000000000000000000000000000000000000000000000001C00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E000000000000000000000000000000000000000000000000000000000000000106E08021150C300000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003F12240801122008337337E57539185C701E17DD6D4D40196CE5DC93C78D63F230F95A1400FF482A0C0890FC98890610A19BFE8901320962616E64636861696E00D29486D95B1644697DEA8C68383012C0E23CB1665A913E92A6E5A5B459A582F8755D5F030C0ACB291F0A9B83C2FE987BA8BAC50B823E750E6C06B343D0645CAE000000000000000000000000000000000000000000000000000000000000001C00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E000000000000000000000000000000000000000000000000000000000000000106E08021150C300000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003F12240801122008337337E57539185C701E17DD6D4D40196CE5DC93C78D63F230F95A1400FF482A0C0890FC98890610C1E8AE8A01320962616E64636861696E00F7ED403C3CCD072A0208D7C91672F82198CF70C5075A64CDE4BB12CCDEF2030B7115822A5CBF89C58D16D478898EEB43A6A22BC9DA3840947F2B3FFEC2D5350B000000000000000000000000000000000000000000000000000000000000001B00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E000000000000000000000000000000000000000000000000000000000000000106E08021150C300000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003F12240801122008337337E57539185C701E17DD6D4D40196CE5DC93C78D63F230F95A1400FF482A0C0890FC98890610A2F0C58301320962616E64636861696E00871C2C330046C9CFB995F7CBFD11842325D3BB7B74A698CEA6480DB626DA14D91E6BF8564B54DEB5D8AFFB81F1E653B71A9EC00449E6174C48969B3EF348F561000000000000000000000000000000000000000000000000000000000000001B00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E000000000000000000000000000000000000000000000000000000000000000106E08021150C300000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003F12240801122008337337E57539185C701E17DD6D4D40196CE5DC93C78D63F230F95A1400FF482A0C0890FC988906109A998D8201320962616E64636861696E0000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000062000000000000000000000000000000000000000000000000000000000000005C0000000000000000000000000000000000000000000000000000000000000C350000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000D900000000000000000000000000000000000000000000000000000000000002800000000000000000000000000000000000000000000000000000000000000160000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000001800000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000006124D493000000000000000000000000000000000000000000000000000000006124D497000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000001C000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000013000000010000000342544300000000000186A000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000C000000010000000124EC078C000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000009038EB739BB22F48B7F3053A90BA2BA4FE07FAB262CADF8664489565C50FF505B8BD00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000093D712C9E016BBC2A428B858A357B3BE2C6F0D0A719A1B0C9FDA955FE028F8475970000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000956A755BB0A913CF9311C9E75413BCA82BD6748E12E3D373A587FC06CA20D8FE7432000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000A00803BF06734CB8C9A28A0241A80F51CDE874902CA1CA84C48EEB5CEDC897B37104000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000021000000000000000000000000000000000000000000000000000000000000C34FFAAB0CC553A45E02D2223C6A29CF0BB1726B2A41E85780732F85B53BE7066F2000000000000000000000000000000000000000000000000000000000000005C0000000000000000000000000000000000000000000000000000000000000C35000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000008FCF00000000000000000000000000000000000000000000000000000000000002800000000000000000000000000000000000000000000000000000000000000160000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000001800000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000006125DF0E000000000000000000000000000000000000000000000000000000006125DF10000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000001C000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000013000000010000000342544300000000000186A000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000C000000010000000120F459390000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000093A1C8A00E3FAAD7C5167FE1F926D2DC2D60FD556D6BAA55D6EF4B3E5A6EAD028FA100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000093D7E811906FBEE0B3D365235071BD1B257B254DE6C433823CDA180A3F8AF7731C9A000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000956A755BB0A913CF9311C9E75413BCA82BD6748E12E3D373A587FC06CA20D8FE7432000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000A00803BF06734CB8C9A28A0241A80F51CDE874902CA1CA84C48EEB5CEDC897B37104000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000021000000000000000000000000000000000000000000000000000000000000C34FFAAB0CC553A45E02D2223C6A29CF0BB1726B2A41E85780732F85B53BE7066F20"


EXPECTED_MULTI_RELAY_RESULT = [
    [
        "", 
        1, 
        "0x000000010000000342544300000000000186a0", 
        1, 
        1, 
        1, 
        1, 
        1629803667, 
        1629803671, 
        1, 
        "0x000000010000000124ec078c"
    ],
    [
        "", 
        1, 
        "0x000000010000000342544300000000000186a0", 
        1, 
        1, 
        2, 
        1, 
        1629871886, 
        1629871888, 
        1, 
        "0x000000010000000120f45939"
    ],
]

# Deploy MockReceiver contract
@pytest.fixture(scope="module")
def mockreceiver(bridge):
    return accounts[0].deploy(MockReceiver, bridge)


def test_bridge_relayandmultiverify_success(bridge, mockreceiver):
    tx = mockreceiver.relayAndMultiSafe(VALID_MULTI_PROOF)
    assert tx.status == 1
    assert bridge.blockDetails(50000) == [
        "0xB125AC2FE51484F660E16D288364D1B5EAD612111397F3124A596E3B00313C4C",
        1629896206,
        453213188,
    ]
    for i in range(len(EXPECTED_MULTI_RELAY_RESULT)):
        res = mockreceiver.latestResults(i)
        assert [
            res["clientID"],
            res["oracleScriptID"],
            res["params"],
            res["askCount"],
            res["minCount"],
            res["requestID"],
            res["ansCount"],
            int(res["requestTime"]),
            int(res["resolveTime"]),
            res["resolveStatus"],
            res["result"],
        ] == EXPECTED_MULTI_RELAY_RESULT[i]
