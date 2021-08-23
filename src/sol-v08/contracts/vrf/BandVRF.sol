// // SPDX-License-Identifier: Apache-2.0

// pragma solidity ^0.6.0;
// pragma experimental ABIEncoderV2;

// import {IBridge} from "../../interfaces/bridge/IBridge.sol";
// import {Obi} from "../obi/Obi.sol";
// import {VRFDecoder} from "./library/VRFDecoder.sol";

// /// @title BandVRF contract
// /// @notice Contract for working with BandChain's verifiable random function feature
// contract BandVRF {
//     using Obi for Obi.Data;
//     IBridge private _bridge;

//     /// @notice BandVRF constructor
//     /// @param bridge The address of Band's Bridge contract
//     constructor(IBridge bridge) public {
//         _bridge = bridge;
//     }

//     /// @notice Validate the input proof and returns the corresponding seed, timestamp, and random hash
//     /// @dev The function expects a proof byte corresponding to a VRF data request on BandChain.
//     /// It then uses Band's bridge contract to verify the correctness of the proof and decodes
//     /// the corresponding request and response packets
//     /// Finally, the function decodes the packets and returns the seed phrase, timestamp,
//     /// and result random hash
//     /// @param proof The proof bytes returned as a result of a data request on BandChain
//     function getRandomHash(bytes calldata proof)
//         external
//         returns (
//             string memory seed,
//             uint64 time,
//             bytes memory hash
//         )
//     {
//         // Verify input proof using the bridge contract's relayAndVerify method
//         (
//             IBridge.RequestPacket memory req,
//             IBridge.ResponsePacket memory res
//         ) = _bridge.relayAndVerify(proof);

//         // Decode the returned request's input parameters and response parameters
//         VRFDecoder.Params memory params = VRFDecoder.decodeParams(req.params);
//         VRFDecoder.Result memory result = VRFDecoder.decodeResult(res.result);

//         return (params.seed, params.time, result.hash);
//     }
// }
