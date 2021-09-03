// SPDX-License-Identifier: Apache-2.0

pragma solidity 0.8.4;
pragma abicoder v2;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import {IAVLMerklePath} from "../bridge/library/IAVLMerklePath.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";

/// @title BandChain MockBridge for VRF
/// @author Band Protocol Team
contract MockBridgeForVRF is IBridge {
    using IAVLMerklePath for IAVLMerklePath.Data;

    /// Performs oracle state relay and oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and data verification.
    function relayAndVerify(bytes calldata data)
        external
        override
        returns (IBridge.Result memory)
    {
        (bytes memory _relayData, bytes memory verifyData) = abi.decode(
            data,
            (bytes, bytes)
        );

        (
            uint256 _blockHeight,
            IBridge.Result memory result,
            uint256 _version,
            IAVLMerklePath.Data[] memory _merklePaths
        ) = abi.decode(
                verifyData,
                (uint256, IBridge.Result, uint256, IAVLMerklePath.Data[])
            );

        return result;
    }

    function relayAndVerifyCount(bytes calldata data)
        external
        override
        returns (uint64, uint64)
    {
        revert("Unimplemented");
    }

    function relayAndMultiVerify(bytes calldata data)
        external
        override
        returns (IBridge.Result[] memory)
    {
        revert("Unimplemented");
    }
}
