// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;

/// @title IVRFProvider interface
/// @notice Interface for the BandVRF provider
interface IVRFProvider {
    /// @dev The function for consumers who want random data.
    /// Consumers can simply make requests to get random data back later.
    /// @param seed Any string that used to initialize the randomizer.
    /// @param time Timestamp where the random data was created.
    function requestRandomData(string calldata seed, uint64 time)
        external
        payable;
}
