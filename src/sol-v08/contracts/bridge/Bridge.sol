// SPDX-License-Identifier: Apache-2.0

pragma solidity 0.8.4;
pragma abicoder v2;

import {ProtobufLib} from "./library/ProtobufLib.sol";
import {BlockHeaderMerkleParts} from "./library/BlockHeaderMerkleParts.sol";
import {MultiStore} from "./library/MultiStore.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IAVLMerklePath} from "./library/IAVLMerklePath.sol";
import {TMSignature} from "./library/TMSignature.sol";
import {Utils} from "./library/Utils.sol";
import {ResultCodec} from "./library/ResultCodec.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";

/// @title BandChain Bridge
/// @author Band Protocol Team
contract Bridge is IBridge, Ownable {
    using BlockHeaderMerkleParts for BlockHeaderMerkleParts.Data;
    using MultiStore for MultiStore.Data;
    using IAVLMerklePath for IAVLMerklePath.Data;
    using TMSignature for TMSignature.Data;

    struct ValidatorWithPower {
        address addr;
        uint256 power;
    }

    struct BlockDetail {
        bytes32 oracleState;
        uint64 timeSecond;
        uint32 timeNanoSecondFraction; // between 0 to 10^9
    }

    /// Mapping from block height to the struct that contains block time and hash of "oracle" iAVL Merkle tree.
    mapping(uint256 => BlockDetail) public blockDetails;
    /// Mapping from an address to its voting power.
    mapping(address => uint256) public validatorPowers;
    /// The total voting power of active validators currently on duty.
    uint256 public totalValidatorPower;

    /// Initializes an oracle bridge to BandChain.
    /// @param validators The initial set of BandChain active validators.
    constructor(ValidatorWithPower[] memory validators) {
        for (uint256 idx = 0; idx < validators.length; ++idx) {
            ValidatorWithPower memory validator = validators[idx];
            require(
                validatorPowers[validator.addr] == 0,
                "DUPLICATION_IN_INITIAL_VALIDATOR_SET"
            );
            validatorPowers[validator.addr] = validator.power;
            totalValidatorPower += validator.power;
        }
    }

    /// Update validator powers by owner.
    /// @param validators The changed set of BandChain validators.
    function updateValidatorPowers(ValidatorWithPower[] calldata validators)
        external
        onlyOwner
    {
        for (uint256 idx = 0; idx < validators.length; ++idx) {
            ValidatorWithPower memory validator = validators[idx];
            totalValidatorPower -= validatorPowers[validator.addr];
            validatorPowers[validator.addr] = validator.power;
            totalValidatorPower += validator.power;
        }
    }

    /// Relays a detail of Bandchain block to the bridge contract.
    /// @param multiStore Extra multi store to compute app hash. See MultiStore lib.
    /// @param merkleParts Extra merkle parts to compute block hash. See BlockHeaderMerkleParts lib.
    /// @param signatures The signatures signed on this block, sorted alphabetically by address.
    function relayBlock(
        MultiStore.Data calldata multiStore,
        BlockHeaderMerkleParts.Data calldata merkleParts,
        TMSignature.Data[] calldata signatures
    ) public {
        if (
            blockDetails[merkleParts.height].oracleState == multiStore.oracleIAVLStateHash &&
            blockDetails[merkleParts.height].timeSecond == merkleParts.timeSecond &&
            blockDetails[merkleParts.height].timeNanoSecondFraction == merkleParts.timeNanoSecondFraction
        ) return;

        // Computes Tendermint's block header hash at this given block.
        bytes32 blockHeader = merkleParts.getBlockHeader(multiStore.getAppHash());
        // Counts the total number of valid signatures signed by active validators.
        address lastSigner = address(0);
        uint256 sumVotingPower = 0;
        for (uint256 idx = 0; idx < signatures.length; ++idx) {
            address signer = signatures[idx].recoverSigner(blockHeader);
            require(signer > lastSigner, "INVALID_SIGNATURE_SIGNER_ORDER");
            sumVotingPower += validatorPowers[signer];
            lastSigner = signer;
        }
        // Verifies that sufficient validators signed the block and saves the oracle state.
        require(
            sumVotingPower * 3 > totalValidatorPower * 2,
            "INSUFFICIENT_VALIDATOR_SIGNATURES"
        );
        blockDetails[merkleParts.height] = BlockDetail({
            oracleState: multiStore.oracleIAVLStateHash,
            timeSecond: merkleParts.timeSecond,
            timeNanoSecondFraction: merkleParts.timeNanoSecondFraction
        });
    }

    /// Verifies that the given data is a valid data on BandChain as of the relayed block height.
    /// @param blockHeight The block height. Someone must already relay this block.
    /// @param result The result of this request.
    /// @param version Lastest block height that the data node was updated.
    /// @param merklePaths Merkle proof that shows how the data leave is part of the oracle iAVL.
    function verifyOracleData(
        uint256 blockHeight,
        Result calldata result,
        uint256 version,
        IAVLMerklePath.Data[] calldata merklePaths
    ) public view returns (Result memory) {
        bytes32 oracleStateRoot = blockDetails[blockHeight].oracleState;
        require(
            oracleStateRoot != bytes32(uint256(0)),
            "NO_ORACLE_ROOT_STATE_DATA"
        );
        // Computes the hash of leaf node for iAVL oracle tree.
        bytes32 dataHash = sha256(ResultCodec.encode(result));

        // Verify proof
        require(
            verifyProof(
                oracleStateRoot,
                version,
                abi.encodePacked(
                    uint8(255),
                    result.requestID
                ),
                dataHash,
                merklePaths
            ),
            "INVALID_ORACLE_DATA_PROOF"
        );

        return result;
    }

    /// Verifies that the given data is a valid data on BandChain as of the relayed block height.
    /// @param blockHeight The block height. Someone must already relay this block.
    /// @param count The requests count on the block.
    /// @param version Lastest block height that the data node was updated.
    /// @param merklePaths Merkle proof that shows how the data leave is part of the oracle iAVL.
    function verifyRequestsCount(
        uint256 blockHeight,
        uint256 count,
        uint256 version,
        IAVLMerklePath.Data[] memory merklePaths
    ) public view returns (uint64, uint64) {
        BlockDetail memory blockDetail = blockDetails[blockHeight];
        bytes32 oracleStateRoot = blockDetail.oracleState;
        require(
            oracleStateRoot != bytes32(uint256(0)),
            "NO_ORACLE_ROOT_STATE_DATA"
        );

        // Encode abd calculate hash of count
        bytes memory encodedCount = abi.encodePacked(
                ProtobufLib.encode_key(
                    1,
                    uint64(ProtobufLib.WireType.Varint)
                ),
                ProtobufLib.encode_uint64(uint64(count))
        );
        bytes32 dataHash = sha256(
            abi.encodePacked(
                Utils.encodeVarintUnsigned(encodedCount.length),
                encodedCount
            )
        );

        // Verify proof
        require(
            verifyProof(
                oracleStateRoot,
                version,
                hex"0052657175657374436f756e74",
                dataHash,
                merklePaths
            ),
            "INVALID_ORACLE_DATA_PROOF"
        );

        return (blockDetail.timeSecond, uint64(count));
    }

    /// Performs oracle state relay and oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and data verification.
    function relayAndVerify(bytes calldata data)
        external
        override
        returns (Result memory)
    {
        (bytes memory relayData, bytes memory verifyData) = abi.decode(
            data, 
            (bytes, bytes)
        );
        (bool relayOk, ) = address(this).call(
            abi.encodePacked(this.relayBlock.selector, relayData)
        );
        require(relayOk, "RELAY_BLOCK_FAILED");
        (bool verifyOk, bytes memory verifyResult) = address(this).staticcall(
            abi.encodePacked(this.verifyOracleData.selector, verifyData)
        );
        require(verifyOk, "VERIFY_ORACLE_DATA_FAILED");
        return abi.decode(verifyResult, (Result));
    }

    /// Performs oracle state relay and many times of oracle data verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data for oracle state relay and an array of data verification.
    function relayAndMultiVerify(bytes calldata data)
        external
        override
        returns (Result[] memory)
    {
        (bytes memory relayData, bytes[] memory manyVerifyData) = abi.decode(
            data, 
            (bytes, bytes[])
        );
        (bool relayOk, ) = address(this).call(
            abi.encodePacked(this.relayBlock.selector, relayData)
        );
        require(relayOk, "RELAY_BLOCK_FAILED");

        Result[] memory results = new Result[](manyVerifyData.length);
        for (uint256 i = 0; i < manyVerifyData.length; i++) {
            (bool verifyOk, bytes memory verifyResult) =
                address(this).staticcall(
                    abi.encodePacked(
                        this.verifyOracleData.selector,
                        manyVerifyData[i]
                    )
                );
            require(verifyOk, "VERIFY_ORACLE_DATA_FAILED");
            results[i] = abi.decode(verifyResult, (Result));
        }

        return results;
    }

    /// Performs oracle state relay and requests count verification in one go. The caller submits
    /// the encoded proof and receives back the decoded data, ready to be validated and used.
    /// @param data The encoded data
    function relayAndVerifyCount(bytes calldata data)
        external
        override
        returns (uint64, uint64) 
    {
        (bytes memory relayData, bytes memory verifyData) = abi.decode(
            data,
            (bytes, bytes)
        );
        (bool relayOk, ) = address(this).call(
            abi.encodePacked(this.relayBlock.selector, relayData)
        );
        require(relayOk, "RELAY_BLOCK_FAILED");

        (bool verifyOk, bytes memory verifyResult) = address(this).staticcall(
            abi.encodePacked(this.verifyRequestsCount.selector, verifyData)
        );
        require(verifyOk, "VERIFY_REQUESTS_COUNT_FAILED");

        return abi.decode(verifyResult, (uint64, uint64));
    }
    
    /// Verifies validity of the given data in the Oracle store. This function is used for both
    /// querying an oracle request and request count.
    /// @param rootHash The expected rootHash of the oracle store.
    /// @param version Lastest block height that the data node was updated.
    /// @param key The encoded key of an oracle request or request count. 
    /// @param dataHash Hashed data corresponding to the provided key.
    /// @param merklePaths Merkle proof that shows how the data leave is part of the oracle iAVL.
    function verifyProof(
        bytes32 rootHash,
        uint256 version,
        bytes memory key,
        bytes32 dataHash,
        IAVLMerklePath.Data[] memory merklePaths
    ) internal pure returns (bool) {
        bytes memory encodedVersion = Utils.encodeVarintSigned(version);

        bytes32 currentMerkleHash = sha256(
            abi.encodePacked(
                uint8(0), // Height of tree (only leaf node) is 0 (signed-varint encode)
                uint8(2), // Size of subtree is 1 (signed-varint encode)
                encodedVersion,
                uint8(key.length), // Size of data key
                key,
                uint8(32), // Size of data hash
                dataHash
            )
        );

        // Goes step-by-step computing hash of parent nodes until reaching root node.
        for (uint256 idx = 0; idx < merklePaths.length; ++idx) {
            currentMerkleHash = merklePaths[idx].getParentHash(
                currentMerkleHash
            );
        }

        // Verifies that the computed Merkle root matches what currently exists.
        return currentMerkleHash == rootHash;
    }
}
