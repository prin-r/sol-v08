// SPDX-License-Identifier: Apache-2.0

pragma solidity 0.8.4;
pragma abicoder v2;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Address} from "@openzeppelin/contracts/utils/Address.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";
import {IVRFProvider} from "../../interfaces/vrf/IVRFProvider.sol";
import {IVRFConsumer} from "../../interfaces/vrf/IVRFConsumer.sol";
import {VRFDecoder} from "./library/VRFDecoder.sol";

/// @title VRFProvider contract
/// @notice Contract for working with BandChain's verifiable random function feature
abstract contract VRFProviderBase is IVRFProvider, Ownable {
    using SafeMath for uint256;
    using VRFDecoder for bytes;
    using Address for address;

    IBridge public bridge;
    uint256 public oracleScriptID;
    uint256 public minCount;
    uint256 public askCount;

    uint256 public taskNonce;

    mapping(address => mapping(string => bool)) public hasClientSeed;
    mapping(string => Task) public tasks;

    event RandomDataRequested(
        uint256 nonce,
        address caller,
        string clientSeed,
        string seed,
        uint64 time,
        bytes32 blockHash,
        uint256 bounty
    );
    event RandomDataRelayed(
        address to,
        string clientSeed,
        string seed,
        uint64 time,
        uint64 bandRequestID,
        bytes32 result
    );

    struct Task {
        address caller;
        string clientSeed;
        uint64 time;
        uint256 bounty;
        bool isResolved;
        bytes32 result;
    }

    constructor(
        IBridge _bridge,
        uint256 _oracleScriptID,
        uint256 _minCount,
        uint256 _askCount
    ) {
        bridge = _bridge;
        oracleScriptID = _oracleScriptID;
        minCount = _minCount;
        askCount = _askCount;
    }

    function b32ToHexString(bytes32 x) public pure returns (string memory) {
        bytes memory s = new bytes(64);
        for (uint256 i = 0; i < 32; i++) {
            uint8 j = ((uint8(x[i]) & 240) >> 4) + 48;
            uint8 k = (uint8(x[i]) & 15) + 48;
            if (j > 57) {
                j += 39;
            }
            if (k > 57) {
                k += 39;
            }
            s[(i << 1)] = bytes1(j);
            s[(i << 1) + 1] = bytes1(k);
        }
        return string(s);
    }

    function getBlockTime() public view virtual returns (uint64) {
        return uint64(block.timestamp);
    }

    function getBlockLatestHash() public view virtual returns (bytes32) {
        return blockhash(block.number - 1);
    }

    function getSeed(
        string memory clientSeed,
        uint64 time,
        bytes32 blockHash,
        uint256 nonce,
        address caller
    ) public pure returns (string memory) {
        return
            b32ToHexString(
                keccak256(
                    abi.encode(clientSeed, time, blockHash, nonce, caller)
                )
            );
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

    function requestRandomData(string calldata clientSeed)
        external
        payable
        override
    {
        require(
            !hasClientSeed[msg.sender][clientSeed],
            "Seed already existed for this sender"
        );

        uint64 time = getBlockTime();
        bytes32 blockHash = getBlockLatestHash();
        string memory seed = getSeed(
            clientSeed,
            time,
            blockHash,
            taskNonce,
            msg.sender
        );

        Task storage task = tasks[seed];
        task.caller = msg.sender;
        task.bounty = msg.value;
        task.time = time;
        task.clientSeed = clientSeed;

        emit RandomDataRequested(
            taskNonce,
            msg.sender,
            clientSeed,
            seed,
            time,
            blockHash,
            msg.value
        );

        hasClientSeed[msg.sender][clientSeed] = true;
        taskNonce = taskNonce.add(1);
    }

    function relayProof(bytes calldata proof) external {
        IBridge.Result memory res = bridge.relayAndVerify(proof);

        // check oracle script id, min count, ask count
        require(
            res.oracleScriptID == oracleScriptID,
            "Oracle Script ID not match"
        );
        require(res.minCount == minCount, "Min Count not match");
        require(res.askCount == askCount, "Ask Count not match");
        require(
            res.resolveStatus == IBridge.ResolveStatus.RESOLVE_STATUS_SUCCESS,
            "Request not successfully resolved"
        );

        VRFDecoder.Params memory params = res.params.decodeParams();

        Task storage task = tasks[params.seed];
        require(task.caller != address(0), "Task not found");
        require(!task.isResolved, "Task already resolved");

        VRFDecoder.Result memory result = res.result.decodeResult();
        bytes32 resultHash = keccak256(result.hash);

        // End function by call consume function on VRF consumer with data from BandChain
        if (task.caller.isContract()) {
            IVRFConsumer(task.caller).consume(
                task.clientSeed,
                task.time,
                resultHash
            );
        }

        // Save result and mark resolve to this task
        task.result = resultHash;
        task.isResolved = true;
        payable(msg.sender).transfer(task.bounty);
        emit RandomDataRelayed(
            task.caller,
            task.clientSeed,
            params.seed,
            task.time,
            res.requestID,
            resultHash
        );
    }
}
