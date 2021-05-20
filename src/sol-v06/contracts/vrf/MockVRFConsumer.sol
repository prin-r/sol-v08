// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;

import {IVRFProvider} from "../../interfaces/vrf/IVRFProvider.sol";
import {VRFConsumerBase} from "./VRFConsumerBase.sol";

contract MockVRFConsumer is VRFConsumerBase {
    string public latestSeed;
    uint64 public latestTime;
    bytes32 public latestResult;

    constructor(IVRFProvider _provider) public {
        provider = _provider;
    }

    function requestRandomDataFromProvider(string calldata seed, uint64 time)
        public
    {
        provider.requestRandomData(seed, time);
    }

    function _consume(
        string calldata seed,
        uint64 time,
        bytes32 result
    ) internal override {
        // revert("Unimplemented");
    }
}
