// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {
    IStdReference,
    StdReferenceBase
} from "../../interfaces/stdreference/IStdReference.sol";

contract StdReferenceProxy is Ownable, StdReferenceBase {
    IStdReference public ref;

    constructor(IStdReference _ref) public {
        ref = _ref;
    }

    /// Updates standard reference implementation. Only callable by the owner.
    function setRef(IStdReference _ref) public onlyOwner {
        ref = _ref;
    }

    /// Returns the price data for the given base/quote pair. Revert if not available.
    function getReferenceData(string memory base, string memory quote)
        public
        override
        view
        returns (ReferenceData memory)
    {
        return ref.getReferenceData(base, quote);
    }
}
