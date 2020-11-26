import pytest
import brownie
from brownie import accounts, Bridge, MockReceiver
import time

VALID_MULTI_PROOF = "000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000009C00000000000000000000000000000000000000000000000000000000000000960B468711C1FD8587C8A1DDEBF207E5CF0FC8EB59960906887BF591D26A6B45E9F712D0B5A4A2C0A79795714A85F70AE6BD1C959FB0AC5F74BD399157DE67528FDC73EDF96586F886FE4069996FB450378A10C788B838C1C5C5B5639301AC0461A2B6A7E0F44ED9C179A47A40F93D5824189A5426D6C3F77692DE28E50E20A33DD488EF2C49D3266D49742792F0D125C64ECD091826294DABD3CD3AB10C0ECF0AD3561783E9C3BDF932A16580FC0C9CEFFEC4C509073FFF65A42871BFAB64408AE00000000000000000000000000000000000000000000000000000000002E6ACB000000000000000000000000000000000000000000000000000000005FB65098000000000000000000000000000000000000000000000000000000001375A792065DE0F2AD50CB669BF82EBC611ED84FCC30FF3E095BA8F9C3ED72B4298C6660EA01CD62E714B603323A21A4A7382F8AB04788C867A0C99ADE687D00E7D5FE622D8CF49EFBEA83CED748FD95E46F5739B2E8397FDA1F7D5C9D723FDDB1CF399AF53C1AE75171513D4278346694D6EBB7F466DE29F84FC4E01E5A00BF6479244200000000000000000000000000000000000000000000000000000000000001C0000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000A00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000036000000000000000000000000000000000000000000000000000000000000004C00000000000000000000000000000000000000000000000000000000000000620FD3DEB742FE8549592B80C86896A0CEFD90F891B633C9AD0345BDF412EA89A325751172ADE4F94B11ACE538F037034ABE2CBAFD6984EB48B7B1CDAB0EC346D9B000000000000000000000000000000000000000000000000000000000000001C00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E0000000000000000000000000000000000000000000000000000000000000001074080211CB6A2E000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004512240A20E5D712A51D58F709F311C6328DEEA5110AEB1D191E13748CB7AF202919D768D910012A0C089BA1D9FD0510CFDBF18D01320F62616E642D6775616E79752D706F610000000000000000000000000000000000000000000000000000005532480EC18BC8525F958AD134E6CF8A46A46C13747C05AA5A00FE8E9F669F9E2DD57E25E3E3B2A7EA37E9801BA8F01324976AB9FE5BD722F673FE49BB48A9FD000000000000000000000000000000000000000000000000000000000000001B00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E0000000000000000000000000000000000000000000000000000000000000001073080211CB6A2E000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004412240A20E5D712A51D58F709F311C6328DEEA5110AEB1D191E13748CB7AF202919D768D910012A0B089BA1D9FD0510E7E8996F320F62616E642D6775616E79752D706F6100000000000000000000000000000000000000000000000000000000539D0B158F2E3030B2CCA7EDBBB11987817BB7DF5137C432969D648E4F9ED41E01E000527E4CD9CDCDB0FF2C8BDD7ECF0963687FC4CD0095B5EBC653FF5B226B000000000000000000000000000000000000000000000000000000000000001B00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E0000000000000000000000000000000000000000000000000000000000000001073080211CB6A2E000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004412240A20E5D712A51D58F709F311C6328DEEA5110AEB1D191E13748CB7AF202919D768D910012A0B089BA1D9FD0510BACCD66C320F62616E642D6775616E79752D706F610000000000000000000000000000000000000000000000000000000003953902A654BF3CC97AA24C76E35723CCE4F41047B16E2A87A920459F7A87EF6879AC9F06FD1CAB5E9F2E73333EA8E4280C8279A9D94E42E21309ED47DEAAA4000000000000000000000000000000000000000000000000000000000000001B00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E0000000000000000000000000000000000000000000000000000000000000001073080211CB6A2E000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004412240A20E5D712A51D58F709F311C6328DEEA5110AEB1D191E13748CB7AF202919D768D910012A0B089BA1D9FD0510FDC3C26C320F62616E642D6775616E79752D706F6100000000000000000000000000000000000000000000000000000000477823664D94FDCFC0407867CD2BA0DC68503E18A5F12C2FF98F6D3C49D4184B6F3423BDC94A5EDD92F93A2E670D7AC07472EF63D10FEFA16824FFF497F79DAE000000000000000000000000000000000000000000000000000000000000001B00000000000000000000000000000000000000000000000000000000000000A000000000000000000000000000000000000000000000000000000000000000E0000000000000000000000000000000000000000000000000000000000000001074080211CB6A2E000000000022480A2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004512240A20E5D712A51D58F709F311C6328DEEA5110AEB1D191E13748CB7AF202919D768D910012A0C089BA1D9FD051083F7C68D01320F62616E642D6775616E79752D706F61000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000001280000000000000000000000000000000000000000000000000000000000000122000000000000000000000000000000000000000000000000000000000002E6ACB00000000000000000000000000000000000000000000000000000000000000A00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000013272000000000000000000000000000000000000000000000000000000000000003A000000000000000000000000000000000000000000000000000000000000000A0000000000000000000000000000000000000000000000000000000000000000A00000000000000000000000000000000000000000000000000000000000000E000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000C62616E64636861696E2E6A730000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004E00000042307861303233633930636262643537333837653233613361643736336264396263343839326566343136373661626564306330363531323937356537323864346231000000005F62ADCC00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000E00000000000000000000000000000000000000000000000000000000000030D400000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000005F635E63000000000000000000000000000000000000000000000000000000005F635E6900000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000120000000000000000000000000000000000000000000000000000000000000000C62616E64636861696E2E6A730000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004400000040F29530BEAB543E12C53E6E1A52B82F00C8971EC2516F05D140F83D16125B41900958D87FF44AA743BEA410E94FF42B89735F44B50C01642372FE5F5074E80F34000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000017000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000013274C46EBC499DA23DB3A9B78B84234C489BBD180D1445EA9E4398E1A6B0821E0CD50000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000013275675B7A69A8D93E17EA62B22F60A9DC2A36D87546E41FA45D38A14A5F23BD01318000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000013275FCF94DC15900DEA7EB8CC2ABCB35FDE5DEB8774612A26C07584D8F146E7E810FB00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000001327635CD17A6E8731924673141F69ECA63E51DF52A984664D5C7004656A80C54F98F800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000001327BFA6B554F1AB667FCB0CC48FD442400814D2A1737C8756C47CA987F3C4846F68BF00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000001327DFA8108FA4A93B9D26F6A6B79935DA3B55CF1AC40BD8F4A2981E3A172ADDDCA86C00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000007000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000001328468DC6D268F36F153950855D762AFE859035C4F44403D9970CBE8AB9AE9F3AC7C100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000001329411DE3DFE263EE9FBA59BB1D8D5A0BE5CFE7FF92B624995690CDBC6253E59106AE0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000900000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000132ADD3FF84ABBD9F66F73AF96485624C1944E13EF3E02D52FE627F838E990C1FFBFED0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000A00000000000000000000000000000000000000000000000000000000000003FF00000000000000000000000000000000000000000000000000000000001334D926C61F8C0DA16600F803CA4149466FEBE850803493FC6B201A887AAECEE7DE900000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000B00000000000000000000000000000000000000000000000000000000000007FE0000000000000000000000000000000000000000000000000000000000133B7A29A3912215FB42008F483858D50E1D10EB9AF699103B69171B2DDF6EF5FF03E20000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000C0000000000000000000000000000000000000000000000000000000000000FFA00000000000000000000000000000000000000000000000000000000001348EBC368F85E523AB1469101312197E130F1899195AE66021B6DAC2613F40AE3D0E20000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000D0000000000000000000000000000000000000000000000000000000000001FF60000000000000000000000000000000000000000000000000000000000136391A3775FB6B8179F8C0E2221F78B2B61D0073462F26CF9FFC95384D69EB574109E0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000E0000000000000000000000000000000000000000000000000000000000003FF0000000000000000000000000000000000000000000000000000000000013E9BF2CF9A7D0095B43CCAB8A004643936D4D46B5C58DD003C5251E7755430565C71D0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000F0000000000000000000000000000000000000000000000000000000000007FE5000000000000000000000000000000000000000000000000000000000014EE8BB5CE915B57F32A9622B381F3122B4779791B7C6445550A49A0E5314B1A336CF800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000FFD0000000000000000000000000000000000000000000000000000000000016DB7F09B5558485E7391AAFA9D45A6351D1154D77B94998B146ACB7EA694E72FA1D3500000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000011000000000000000000000000000000000000000000000000000000000001FFC00000000000000000000000000000000000000000000000000000000000180863AD241E834A5CD8E4264264FF20A334CBED822B1596A85E19450D986E3996FE4900000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000003EF900000000000000000000000000000000000000000000000000000000000285D6BFA9E317EA658A47E319DFDA65DD2B74861142720C52EB883FAAAD23956773FBB00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000013000000000000000000000000000000000000000000000000000000000007EDF10000000000000000000000000000000000000000000000000000000000285D6B9D165B7984CBE6EFEB7DA6A68C0C7067E43FD851DBE4D6C7EBB4A2ACB35400E700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000015000000000000000000000000000000000000000000000000000000000012EEBA00000000000000000000000000000000000000000000000000000000002E6ACA82D3483C022207D086A9CF388E91B78082A4DCBCECDCE78924F14068BFC70983000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000160000000000000000000000000000000000000000000000000000000000316EDF00000000000000000000000000000000000000000000000000000000002E6ACAFE60A428C0C4541B2C0853F939107DA648B970245E8796D5B1D388216C537B9C0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000001700000000000000000000000000000000000000000000000000000000005EE4A200000000000000000000000000000000000000000000000000000000002E6ACA57B362B4E1DB7F5AAED43A34138B021D44A6AE5B2B4A3B6E0439C8B1931D630E00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000072667700000000000000000000000000000000000000000000000000000000002E6ACAF2674916787DC0567367951D0C161DB375C74BA54CAC4C5AC7421AA551C1939E000000000000000000000000000000000000000000000000000000000000130000000000000000000000000000000000000000000000000000000000002E6ACB00000000000000000000000000000000000000000000000000000000000000A0000000000000000000000000000000000000000000000000000000000000026000000000000000000000000000000000000000000000000000000000001A34EA000000000000000000000000000000000000000000000000000000000000048000000000000000000000000000000000000000000000000000000000000000A0000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000E000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000862616E647465616D00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000BE000000190000000342544300000003455448000000045553445400000003585250000000044C494E4B00000003444F5400000003424348000000034C544300000003414441000000034253560000000343524F00000003424E4200000003454F530000000358545A0000000354525800000003584C4D0000000441544F4D00000003584D52000000034F4B420000000455534443000000034E454F0000000358454D000000034C454F00000002485400000003564554000000003B9ACA00000000000000000000000000000000000000000000000000000000000000000000E000000000000000000000000000000000000000000000000000000000000609510000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000005F78CE03000000000000000000000000000000000000000000000000000000005F78CE0900000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000120000000000000000000000000000000000000000000000000000000000000000862616E647465616D00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000CC00000019000009A00E94090000000051ACB69D80000000003BB19DC0000000000DFA2FA00000000235E2F18000000000F503482800000033513A30200000000AB276C0C000000000059FD30F000000256A9464E00000000008C55109000000068C2F169F00000000951177F0000000007F8DCF000000000001B069440000000004443960000000012FE52E2000000018129575C0000000016D2AD578000000003B9C50A00000000436D815000000000006D4B407000000004B1A13000000000116716EE00000000000B909B00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001700000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000001A34ED0C6F3BBC51835AB55E6FFA856BF8F753A823FD34E09B09CD7E4D54696D7F435500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000001A34F2E03B8FE47F0453B91F9D1A636D712E35FBD5B92012AD9E5F789F4D710C73986200000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000001A34F47B5616F4B511CCFBEF76035A17E73F8176863E69015FAD78B687F9B8E270AFBF00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000F00000000000000000000000000000000000000000000000000000000001A34FBE4839BC7955C6549CF5A9E48C3CB9F1BD399ADB7810C194D3AB3212A466C00EA00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000005000000000000000000000000000000000000000000000000000000000000001F00000000000000000000000000000000000000000000000000000000001A350D8884ED98A581525E3DD5F12A38584E9DEAD1AEF8BA7B12C8A42DB22774B070C700000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000003F00000000000000000000000000000000000000000000000000000000001A35365C782ACDF2C08582E91726E7072FB2D0ABBCA91B8467D1D45E2B7CBE9E11083500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007000000000000000000000000000000000000000000000000000000000000007F00000000000000000000000000000000000000000000000000000000001A35CDA49AAA0FACE4D3E0DFBCF1563D30FB23424772A5D178B496C7A487F6F72040340000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000FF00000000000000000000000000000000000000000000000000000000001A363EE2BD80AE08C98DA07E070A69E96A19FEB8F85DF0AD6B946BF3148B045D0EB5E10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000900000000000000000000000000000000000000000000000000000000000001FF00000000000000000000000000000000000000000000000000000000001A38C31DFD7E0354016B65578F7D11BD4BFB5103BF7E055960B3DFFB2C82083AC22F390000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000A00000000000000000000000000000000000000000000000000000000000003FD00000000000000000000000000000000000000000000000000000000001A3A8864D5E2384E8E68FEF3D4B5EFE89B2B4D2D0D609DD6E88647C565BED6648D78570000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000B00000000000000000000000000000000000000000000000000000000000007FA00000000000000000000000000000000000000000000000000000000001A44C1C29B4F7C9434EF88B652DF63B26A8CDE5A0C3FBB862CD507B6A7851EF39625610000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000C0000000000000000000000000000000000000000000000000000000000000FF800000000000000000000000000000000000000000000000000000000001A4B97675BDB848D1CE87F32AFBE51B5394AE00C1B5CD4E31D0B650F7EC53B2EA5750C0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000D0000000000000000000000000000000000000000000000000000000000001FEF00000000000000000000000000000000000000000000000000000000001A59359C21C26A193CCF9D7B47492BD6BA2206A18707336BA5F7538C106C2D1A9830090000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000E0000000000000000000000000000000000000000000000000000000000003FE200000000000000000000000000000000000000000000000000000000001AAB266238695673CEEC466513A9AE3FC61E6ED32DE97FD53F5904250C9C2C72FD738C0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000F0000000000000000000000000000000000000000000000000000000000007FB700000000000000000000000000000000000000000000000000000000001B4F235F99AACF6C295732B27588CAFB23B74BEE5A7AB07A5FDAC0E7C8FE6E4FB710B600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000FF8100000000000000000000000000000000000000000000000000000000001C97151AA861CA223714A8F839D1E59A713C322FB27DEADFD5AF0A99186AD1EABE73B400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000011000000000000000000000000000000000000000000000000000000000001FEF000000000000000000000000000000000000000000000000000000000001F25E6BD14BD9B424F52B903BC53DDED57D6F7DAEFB0ACF17CFB1539A67974FC012B1700000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000003FE6100000000000000000000000000000000000000000000000000000000002092EC175C1E15C21F92C2D34E689EA9331995C7E68590C3E1A64392459146F03AC71200000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000013000000000000000000000000000000000000000000000000000000000007EDF10000000000000000000000000000000000000000000000000000000000285D6B0B17953B934F1708AEE2CC8D54A0C74EBE3D1367B59805CDF2AE7ED6B07576CE00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000015000000000000000000000000000000000000000000000000000000000012EEBA00000000000000000000000000000000000000000000000000000000002E6ACA82D3483C022207D086A9CF388E91B78082A4DCBCECDCE78924F14068BFC70983000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000160000000000000000000000000000000000000000000000000000000000316EDF00000000000000000000000000000000000000000000000000000000002E6ACAFE60A428C0C4541B2C0853F939107DA648B970245E8796D5B1D388216C537B9C0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000001700000000000000000000000000000000000000000000000000000000005EE4A200000000000000000000000000000000000000000000000000000000002E6ACA57B362B4E1DB7F5AAED43A34138B021D44A6AE5B2B4A3B6E0439C8B1931D630E00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000018000000000000000000000000000000000000000000000000000000000072667700000000000000000000000000000000000000000000000000000000002E6ACAF2674916787DC0567367951D0C161DB375C74BA54CAC4C5AC7421AA551C1939E"


EXPECTED_MULTI_RELAY_RESULT = [
    [
        [
            "bandchain.js",
            10,
            "0x00000042307861303233633930636262643537333837653233613361643736336264396263343839326566343136373661626564306330363531323937356537323864346231000000005f62adcc",
            4,
            4,
        ],
        [
            "bandchain.js",
            200000,
            4,
            1600347747,
            1600347753,
            1,
            "0x00000040f29530beab543e12c53e6e1a52b82f00c8971ec2516f05d140f83d16125b41900958d87ff44aa743bea410e94ff42b89735f44b50c01642372fe5f5074e80f34",
        ],
    ],
    [
        [
            "bandteam",
            8,
            "0x000000190000000342544300000003455448000000045553445400000003585250000000044c494e4b00000003444f5400000003424348000000034c544300000003414441000000034253560000000343524f00000003424e4200000003454f530000000358545a0000000354525800000003584c4d0000000441544f4d00000003584d52000000034f4b420000000455534443000000034e454f0000000358454d000000034c454f00000002485400000003564554000000003b9aca00",
            4,
            3,
        ],
        [
            "bandteam",
            395601,
            4,
            1601752579,
            1601752585,
            1,
            "0x00000019000009a00e94090000000051acb69d80000000003bb19dc0000000000dfa2fa00000000235e2f18000000000f503482800000033513a30200000000ab276c0c000000000059fd30f000000256a9464e00000000008c55109000000068c2f169f00000000951177f0000000007f8dcf000000000001b069440000000004443960000000012fe52e2000000018129575c0000000016d2ad578000000003b9c50a00000000436d815000000000006d4b407000000004b1a13000000000116716ee00000000000b909b0",
        ],
    ],
]

# Deploy MockReceiver contract
@pytest.fixture(scope="module")
def mockreceiver(bridge):
    return accounts[0].deploy(MockReceiver, bridge)


def test_bridge_relayandmultiverify_success(bridge, mockreceiver):
    tx = mockreceiver.relayAndMultiSafe(VALID_MULTI_PROOF)
    assert tx.status == 1
    assert bridge.blockDetails(3041995) == [
        "0xC73EDF96586F886FE4069996FB450378A10C788B838C1C5C5B5639301AC0461A",
        1605783704,
        326477714,
    ]
    for i in range(len(EXPECTED_MULTI_RELAY_RESULT)):
        req = mockreceiver.latestRequests(i)
        res = mockreceiver.latestResponses(i)
        assert [
            req["clientID"],
            req["oracleScriptID"],
            req["params"],
            req["askCount"],
            req["minCount"],
        ] == EXPECTED_MULTI_RELAY_RESULT[i][0]
        assert [
            res["clientID"],
            res["requestID"],
            res["ansCount"],
            int(res["requestTime"]),
            int(res["resolveTime"]),
            res["resolveStatus"],
            res["result"],
        ] == EXPECTED_MULTI_RELAY_RESULT[i][1]
