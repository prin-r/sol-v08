
// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {SafeMath} from "@openzeppelin/contracts/math/SafeMath.sol";
import {IAVLMerklePath} from "../bridge/library/IAVLMerklePath.sol";
import {Packets} from "../bridge/library/Packets.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";

/// @title BandChain MockBridge for VRF
/// @author Band Protocol Team
contract MockBridgeForVRF is IBridge {
    using IAVLMerklePath for IAVLMerklePath.Data;

    struct MockPacket {
        string clientID;
        uint64 oracleScriptID;
        bytes params;
        uint64 askCount;
        uint64 minCount;
        uint64 requestID;
        uint64 ansCount;
        uint64 requestTime;
        uint64 resolveTime;
        uint8 resolveStatus;
        bytes result;
    }

    /// Performs oracle state relay and oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and data verification.
    function relayAndVerify(bytes calldata data)
        external
        override
        returns (RequestPacket memory, ResponsePacket memory)
    {
        (bytes memory _relayData, bytes memory verifyData) = abi.decode(
            data,
            (bytes, bytes)
        );

        (
            uint256 _blockHeight,
            MockPacket memory mp,
            uint256 _version,
            IAVLMerklePath.Data[] memory _merklePaths
        ) = abi.decode(
                verifyData,
                (uint256, MockPacket, uint256, IAVLMerklePath.Data[])
            );

        RequestPacket memory req;
        ResponsePacket memory res;

        req.clientID = mp.clientID;
        req.oracleScriptID = mp.oracleScriptID;
        req.params = mp.params;
        req.askCount = mp.askCount;
        req.minCount = mp.minCount;

        res.clientID = mp.clientID;
        res.requestID = mp.requestID;
        res.ansCount = mp.ansCount;
        res.requestTime = mp.requestTime;
        res.resolveTime = mp.resolveTime;
        res.resolveStatus = mp.resolveStatus;
        res.result = mp.result;

        return (req, res);
    }

    /// Performs oracle state relay and many times of oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and an array of data verification.
    function relayAndMultiVerify(bytes calldata data)
        external
        override
        returns (RequestPacket[] memory, ResponsePacket[] memory)
    {
        revert("Unimplemented");
    }
}