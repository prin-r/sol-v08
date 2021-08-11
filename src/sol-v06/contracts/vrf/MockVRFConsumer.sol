// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;

import {IVRFProvider} from "../../interfaces/vrf/IVRFProvider.sol";
import {VRFConsumerBase} from "./VRFConsumerBase.sol";

contract MockVRFConsumer is VRFConsumerBase {
    string public latestSeed;
    uint64 public latestTime;
    bytes32 public latestResult;

    event RandomDataRequested(address provider, string seed, uint256 bounty);
    event Consume(string seed, uint64 time, bytes32 result);

    constructor(IVRFProvider _provider) public {
        provider = _provider;
    }

    function requestRandomDataFromProvider(string calldata seed)
        external
        payable
    {
        provider.requestRandomData{value: msg.value}(seed);

        emit RandomDataRequested(address(provider), seed, msg.value);
    }

    function _consume(
        string calldata seed,
        uint64 time,
        bytes32 result
    ) internal override {
        latestSeed = seed;
        latestTime = time;
        latestResult = result;

        emit Consume(seed, time, result);
    }
}
