// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {SafeMath} from "@openzeppelin/contracts/math/SafeMath.sol";
import {IAVLMerklePath} from "../bridge/library/IAVLMerklePath.sol";
import {Packets} from "../bridge/library/Packets.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";

/// @title BandChain MockBridge for VRF
/// @author Band Protocol Team
contract MockBridgeForVRF {
    using IAVLMerklePath for IAVLMerklePath.Data;

    /// Performs oracle state relay and oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and data verification.
    function relayAndVerify(bytes calldata data)
        external
        returns (IBridge.RequestPacket memory, IBridge.ResponsePacket memory)
    {
        (bytes memory _relayData, bytes memory verifyData) =
            abi.decode(data, (bytes, bytes));

        (
            uint256 _blockHeight,
            IBridge.RequestPacket memory requestPacket,
            IBridge.ResponsePacket memory responsePacket,
            uint256 _version,
            IAVLMerklePath.Data[] memory _merklePaths
        ) =
            abi.decode(
                verifyData,
                (
                    uint256,
                    IBridge.RequestPacket,
                    IBridge.ResponsePacket,
                    uint256,
                    IAVLMerklePath.Data[]
                )
            );

        return (requestPacket, responsePacket);
    }
}
