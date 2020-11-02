// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {Obi} from "../../obi/Obi.sol";

/// @title ParamsDecoder library
/// @notice Library for decoding the OBI-encoded input parameters of a VRF data request
library VRFResultDecoder {
    using Obi for Obi.Data;

    struct Result {
        bytes hash;
    }

    /// @notice Decodes the encoded data request response result
    /// @param encodedResult Encoded result data
    function decodeResult(bytes memory encodedResult)
        internal
        pure
        returns (Result memory result)
    {
        Obi.Data memory obiData = Obi.from(encodedResult);
        result.hash = obiData.decodeBytes();
    }
}
