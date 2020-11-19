// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {Obi} from "../../obi/Obi.sol";

/// @title ParamsDecoder library
/// @notice Library for decoding the OBI-encoded input parameters of a VRF data request
library VRFDecoder {
    using Obi for Obi.Data;

    struct Params {
        string seed;
        uint64 time;
    }

    struct Result {
        bytes hash;
    }

    /// @notice Decodes the encoded request input parameters
    /// @param encodedParams Encoded paramter data
    function decodeParams(bytes memory encodedParams)
        internal
        pure
        returns (Params memory params)
    {
        Obi.Data memory decoder = Obi.from(encodedParams);
        params.seed = decoder.decodeString();
        params.time = decoder.decodeU64();
        require(decoder.finished(), "DATA_DECODE_NOT_FINISHED");
    }

    /// @notice Decodes the encoded data request response result
    /// @param encodedResult Encoded result data
    function decodeResult(bytes memory encodedResult)
        internal
        pure
        returns (Result memory result)
    {
        Obi.Data memory decoder = Obi.from(encodedResult);
        result.hash = decoder.decodeBytes();
        require(decoder.finished(), "DATA_DECODE_NOT_FINISHED");
    }
}
