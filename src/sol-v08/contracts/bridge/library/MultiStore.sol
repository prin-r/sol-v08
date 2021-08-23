// SPDX-License-Identifier: Apache-2.0

pragma solidity 0.8.4;
import {Utils} from "./Utils.sol";


// Computes Tendermint's application state hash at this given block. AppHash is actually a
// Merkle hash on muliple stores.
//                         ________________[AppHash]_______________
//                        /                                        \
//             _______[I10]______                          _______[I11]________
//            /                  \                        /                    \
//       __[I6]__             __[I7]__                __[I8]__              __[I9]__
//      /         \          /         \            /          \           /         \
//    [I0]       [I1]     [I2]        [I3]        [I4]        [I5]       [C]         [D]
//   /   \      /   \    /    \      /    \      /    \      /    \
// [0]   [1]  [2]   [3] [4]   [5]  [6]    [7]  [8]    [9]  [A]    [B]
// [0] - auth   [1] - bank     [2] - capability  [3] - dist    [4] - evidence
// [5] - gov    [6] - ibchost  [7] - ibctransfer [8] - mint    [9] - oracle
// [A] - params [B] - slashing [C] - staking     [D] - upgrade
// Notice that NOT all leaves of the Merkle tree are needed in order to compute the Merkle
// root hash, since we only want to validate the correctness of [9] In fact, only
// [8], [I5], [I9], and [I10] are needed in order to compute [AppHash].

library MultiStore {
    struct Data {
        bytes32 authToIbcTransferStoresMerkleHash; // [I10]
        bytes32 mintStoreMerkleHash; // [8]
        bytes32 oracleIAVLStateHash; // [9]
        bytes32 paramsToSlashStoresMerkleHash; // [I5]
        bytes32 stakingToUpgradeStoresMerkleHash; // [I9]
    }

    function getAppHash(Data memory self) internal pure returns (bytes32) {
        return
            Utils.merkleInnerHash( // [AppHash]
                self.authToIbcTransferStoresMerkleHash, // [I10]
                Utils.merkleInnerHash( // [I11]
                    Utils.merkleInnerHash( // [I8]
                        Utils.merkleInnerHash( // [I4]
                            self.mintStoreMerkleHash, // [8]
                            Utils.merkleLeafHash( // [9]
                                abi.encodePacked(
                                    hex"066f7261636c6520", // oracle prefix (uint8(6) + "oracle" + uint8(32))
                                    sha256(
                                        abi.encodePacked(
                                            self.oracleIAVLStateHash
                                        )
                                    )
                                )
                            )
                        ),
                        self.paramsToSlashStoresMerkleHash // [I5],
                    ),
                    self.stakingToUpgradeStoresMerkleHash // [I9]
                )
            );
    }
}
