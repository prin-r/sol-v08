// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {Bridge} from "../bridge/Bridge.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";

/// @dev Mock OracleBridge that allows setting oracle iAVL state at a given height directly.
contract MockBridge is Bridge {
    constructor(ValidatorWithPower[] memory _validators)
        public
        Bridge(_validators)
    {}

    function setOracleState(uint256 _blockHeight, bytes32 _oracleIAVLStateHash)
        public
    {
        blockDetails[_blockHeight].oracleState = _oracleIAVLStateHash;
    }
}

contract MockReceiver {
    Bridge.RequestPacket public latestReq;
    Bridge.ResponsePacket public latestRes;
    Bridge.RequestPacket[] public latestRequests;
    Bridge.ResponsePacket[] public latestResponses;
    IBridge public bridge;

    constructor(IBridge _bridge) public {
        bridge = _bridge;
    }

    function relayAndSafe(bytes calldata _data) external {
        (latestReq, latestRes) = bridge.relayAndVerify(_data);
    }

    function relayAndMultiSafe(bytes calldata _data) external {
        (
            Bridge.RequestPacket[] memory requests,
            Bridge.ResponsePacket[] memory responses
        ) = bridge.relayAndMultiVerify(_data);
        delete latestRequests;
        delete latestResponses;
        for (uint256 i = 0; i < requests.length; i++) {
            latestRequests.push(requests[i]);
            latestResponses.push(responses[i]);
        }
    }
}
