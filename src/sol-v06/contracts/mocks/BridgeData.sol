// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {Bridge} from "../bridge/Bridge.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";

contract BridgeData {
    Bridge public bridge;
    IBridge.RequestPacket public req;
    IBridge.ResponsePacket public res;

    constructor(Bridge _bridge) public {
        bridge = _bridge;
    }

    function relayAndSave(bytes calldata data) external {
        (
            IBridge.RequestPacket memory _req,
            IBridge.ResponsePacket memory _res
        ) = bridge.relayAndVerify(data);

        req = _req;
        res = _res;
    }

    function requestClientID() external view returns (string memory) {
        return req.clientID;
    }

    function oracleScriptID() external view returns (uint64) {
        return req.oracleScriptID;
    }

    function params() external view returns (bytes memory) {
        return req.params;
    }

    function askCount() external view returns (uint64) {
        return req.askCount;
    }

    function minCount() external view returns (uint64) {
        return req.minCount;
    }

    function responseClientID() external view returns (string memory) {
        return res.clientID;
    }

    function requestID() external view returns (uint64) {
        return res.requestID;
    }

    function ansCount() external view returns (uint64) {
        return res.ansCount;
    }

    function requestTime() external view returns (uint64) {
        return res.requestTime;
    }

    function resolveTime() external view returns (uint64) {
        return res.resolveTime;
    }

    function resolveStatus() external view returns (uint8) {
        return res.resolveStatus;
    }

    function result() external view returns (bytes memory) {
        return res.result;
    }
}
