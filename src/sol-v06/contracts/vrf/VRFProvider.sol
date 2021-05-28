// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Address} from "@openzeppelin/contracts/utils/Address.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";
import {IVRFProvider} from "../../interfaces/vrf/IVRFProvider.sol";
import {IVRFConsumer} from "../../interfaces/vrf/IVRFConsumer.sol";
import {VRFDecoder} from "./library/VRFDecoder.sol";

/// @title VRFProvider contract
/// @notice Contract for working with BandChain's verifiable random function feature
contract VRFProvider is IVRFProvider, Ownable {
    using VRFDecoder for bytes;
    using Address for address;

    IBridge public bridge;
    uint256 public oracleScriptID;
    uint256 public minCount;
    uint256 public askCount;

    mapping(bytes32 => Task) public tasks;

    event RandomDataRequested(
        address caller,
        string seed,
        uint64 time,
        bytes32 taskKey,
        uint256 bounty
    );
    event RandomDataRelayed(
        address to,
        string seed,
        uint64 time,
        bytes32 taskKey,
        bytes32 result
    );

    struct Task {
        address caller;
        uint256 bounty;
        bool isResolved;
        bytes32 result;
    }

    constructor(
        IBridge _bridge,
        uint256 _oracleScriptID,
        uint256 _minCount,
        uint256 _askCount
    ) public {
        bridge = _bridge;
        oracleScriptID = _oracleScriptID;
        minCount = _minCount;
        askCount = _askCount;
    }

    function setBridge(IBridge _bridge) external onlyOwner {
        bridge = _bridge;
    }

    function setOracleScriptID(uint256 _oracleScriptID) external onlyOwner {
        oracleScriptID = _oracleScriptID;
    }

    function setMinCount(uint256 _minCount) external onlyOwner {
        minCount = _minCount;
    }

    function setAskCount(uint256 _askCount) external onlyOwner {
        askCount = _askCount;
    }

    // Return hash to generate a unique key for this combination
    function getKey(
        address caller,
        string memory seed,
        uint64 time
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(caller, seed, time));
    }

    function requestRandomData(string calldata seed, uint64 time)
        external
        payable
        override
    {
        bytes32 taskKey = getKey(msg.sender, seed, time);
        Task storage task = tasks[taskKey];
        require(task.caller == address(0), "Task already existed");
        task.caller = msg.sender;
        task.bounty = msg.value;
        emit RandomDataRequested(msg.sender, seed, time, taskKey, msg.value);
    }

    function relayProof(address to, bytes calldata proof) external {
        (IBridge.RequestPacket memory req, IBridge.ResponsePacket memory res) =
            bridge.relayAndVerify(proof);

        // check oracle script id, min count, ask count
        require(
            req.oracleScriptID == oracleScriptID,
            "Oracle Script ID not match"
        );
        require(req.minCount == minCount, "Min Count not match");
        require(req.askCount == askCount, "Ask Count not match");

        VRFDecoder.Params memory params = req.params.decodeParams();

        bytes32 taskKey = getKey(to, params.seed, params.time);
        Task storage task = tasks[taskKey];
        require(address(task.caller) != address(0), "Task not found");
        require(!task.isResolved, "Task already resolved");

        VRFDecoder.Result memory result = res.result.decodeResult();
        bytes32 resultHash = keccak256(result.hash);

        // End function by call consume function on VRF consumer with data from BandChain
        if (to.isContract()) {
            IVRFConsumer(task.caller).consume(
                params.seed,
                params.time,
                resultHash
            );
        }

        // Save result and mark resolve to this task
        task.result = resultHash;
        task.isResolved = true;
        msg.sender.transfer(task.bounty);
        emit RandomDataRelayed(
            to,
            params.seed,
            params.time,
            taskKey,
            resultHash
        );
    }
}
