// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {IAVLMerklePath} from "../bridge/library/IAVLMerklePath.sol";

contract MockIAVLMerklePath {
    function getParentHash(
        IAVLMerklePath.Data memory _self,
        bytes32 _dataSubtreeHash
    ) public pure returns (bytes32) {
        return IAVLMerklePath.getParentHash(_self, _dataSubtreeHash);
    }
}
