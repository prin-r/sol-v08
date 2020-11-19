// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;
import {Obi} from "../../obi/Obi.sol";

library StdReferenceDecoder {
    using Obi for Obi.Data;
    struct Params {
        string[] symbols;
        uint64 multiplier;
    }

    struct Result {
        uint64[] rates;
    }

    function decodeParams(bytes memory _data)
        internal
        pure
        returns (Params memory result)
    {
        Obi.Data memory decoder = Obi.from(_data);
        uint32 length = decoder.decodeU32();
        string[] memory symbols = new string[](length);
        for (uint256 i = 0; i < length; i++) {
            symbols[i] = string(decoder.decodeBytes());
        }
        result.symbols = symbols;
        result.multiplier = decoder.decodeU64();
        require(decoder.finished(), "DATA_DECODE_NOT_FINISHED");
    }

    function decodeResult(bytes memory _data)
        internal
        pure
        returns (Result memory result)
    {
        Obi.Data memory decoder = Obi.from(_data);
        uint32 length = decoder.decodeU32();
        uint64[] memory rates = new uint64[](length);
        for (uint256 i = 0; i < length; i++) {
            rates[i] = decoder.decodeU64();
        }
        result.rates = rates;
        require(decoder.finished(), "DATA_DECODE_NOT_FINISHED");
    }
}
