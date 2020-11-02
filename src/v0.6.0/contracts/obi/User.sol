// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {Obi} from "./Obi.sol";
import {ResultDecoder} from "./Result.sol";

contract ObiUser {
    using ResultDecoder for bytes;

    function decode(bytes memory data)
        public
        pure
        returns (ResultDecoder.Result memory)
    {
        return data.decodeResult();
    }
}
