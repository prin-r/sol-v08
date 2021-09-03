// SPDX-License-Identifier: Apache-2.0

pragma solidity 0.8.4;
pragma abicoder v2;

import {IBridge} from "../../interfaces/bridge/IBridge.sol";
import {VRFProviderBase} from "./VRFProviderBase.sol";

contract VRFProvider is VRFProviderBase {
    constructor(
        IBridge _bridge,
        uint256 _oracleScriptID,
        uint256 _minCount,
        uint256 _askCount
    ) public VRFProviderBase(_bridge, _oracleScriptID, _minCount, _askCount) {}
}
