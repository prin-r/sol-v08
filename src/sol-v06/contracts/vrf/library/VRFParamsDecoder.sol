// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {Obi} from "../../obi/Obi.sol";

/// @title ParamsDecoder library
/// @notice Library for decoding the OBI-encoded input parameters of a VRF data request
library VRFParamsDecoder {
    using Obi for Obi.Data;

    struct Params {
        string seed;
        uint64 time;
    }

    /// @notice Decodes the encoded request input parameters
    /// @param encodedParams Encoded paramter data
    function decodeParams(bytes memory encodedParams)
        internal
        pure
        returns (Params memory params)
    {
        Obi.Data memory obiData = Obi.from(encodedParams);
        params.seed = obiData.decodeString();
        params.time = obiData.decodeU64();
    }
}
