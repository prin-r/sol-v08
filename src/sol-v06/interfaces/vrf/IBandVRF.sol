// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

/// @title IBandVRF interface
/// @notice Interface for the BandVRF provider
interface IBandVRF {
    /// @notice Validate the input proof and returns the corresponding seed, timestamp, and random hash
    /// @dev The function expects a proof byte corresponding to a VRF data request on BandChain.
    /// It then uses Band's bridge contract to verify the correctness of the proof and decodes
    /// the corresponding request and response packets
    /// Finally, the function decodes the packets and returns the seed phrase, timestamp,
    /// and result random hash
    /// @param proof The proof bytes returned as a result of a data request on BandChain
    function getRandomHash(bytes calldata proof)
        external
        returns (
            string memory seed,
            uint64 time,
            bytes memory hash
        );
}
