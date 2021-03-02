// SPDX-License-Identifier: Apache-2.0

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {SafeMath} from "@openzeppelin/contracts/math/SafeMath.sol";
import {IBridge} from "../../interfaces/bridge/IBridge.sol";
import {Obi} from "../obi/Obi.sol";
import {StdReferenceDecoder} from "./library/StdReferenceDecoder.sol";
import "../../interfaces/stdreference/IStdReference.sol";

/// @title BandChain StdReferenceBasic
/// @author Band Protocol Team
contract StdReference is AccessControl, StdReferenceBase {
    using Obi for Obi.Data;
    using SafeMath for uint256;

    IBridge public bridge;

    /// List of valid oracle script IDs
    uint64[] public oracleScriptIDs;

    /// Mininum number of BandChain validator reports to allow
    uint64 public ansCount;

    /// Mininum number of BandChain validator reports asked to allow
    uint64 public askCount;

    /// Duration to wait for challenge before data will be
    /// available for each symbol
    uint256 public pendingDuration;

    /// Whether to trust the relayer
    /// Initially true but will be false if disproved by user.
    bool public trustRelayer = true;

    // Update event emitted when ref is updated
    event RefDataUpdate(
        string symbol,
        uint64 rate,
        uint64 resolveTime,
        uint64 requestID
    );

    // Update event emitted when pendingRef is updated
    event PendingRefDataUpdate(
        string symbol,
        uint64 rate,
        uint64 resolveTime,
        uint64 requestID
    );

    // Update event emitted from a successful relayWithProof call
    event VerifiedRefDataUpdate(
        string symbol,
        uint64 rate,
        uint64 resolveTime,
        uint64 requestID
    );

    struct RefData {
        uint64 rate; // USD-rate, multiplied by 1e9.
        uint64 resolveTime; // UNIX epoch when this data has been resolved.
        uint64 relayTime; // UNIX epoch when this data has been resolved.
        uint64 requestID; // BandChain request identifier for this data.
    }

    /// Mapping from token symbol to ref data
    /// Updated by relay() after past pendingDuration
    mapping(string => RefData) public refs;

    /// Mapping from token symbol to pending ref data
    /// updated by relay()
    mapping(string => RefData) public pendingRefs;

    /// Mapping from token symbol to verified ref data
    /// updated by relayWithProof()
    mapping(string => RefData) public verifiedRefs;

    bytes32 public constant RELAYER_ROLE = keccak256("RELAYER_ROLE");

    constructor(
        IBridge _bridge,
        uint64[] memory _oracleScriptIDs,
        uint64 _askCount,
        uint64 _ansCount,
        uint64 _pendingDuration
    ) public {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(RELAYER_ROLE, msg.sender);

        bridge = _bridge;
        oracleScriptIDs = _oracleScriptIDs;
        askCount = _askCount;
        ansCount = _ansCount;
        pendingDuration = _pendingDuration;
    }

    /// @notice Relay and save a set of price data to the contract
    /// @dev All of the lists must be of equal length
    /// @param symbols A list of symbols whose data is being relayed in this function call
    /// @param rates A list of the rates associated with each symbol
    /// @param resolveTimes A list of timestamps of when the rate data was retrieved
    /// @param requestIDs A list of BandChain request IDs in which the rate data was retrieved
    function relay(
        string[] memory symbols,
        uint64[] memory rates,
        uint64[] memory resolveTimes,
        uint64[] memory requestIDs
    ) external {
        require(hasRole(RELAYER_ROLE, msg.sender), "NOT_A_RELAYER");
        uint256 len = symbols.length;
        require(rates.length == len, "BAD_RATES_LENGTH");
        require(resolveTimes.length == len, "BAD_RESOLVE_TIMES_LENGTH");
        require(requestIDs.length == len, "BAD_REQUESTIDS_LENGTH");
        for (uint256 idx = 0; idx < len; idx++) {
            // Check pendingRefs that exceeded pendingDuration
            if (pendingRefReady(symbols[idx])) {
                RefData memory pendingRef = pendingRefs[symbols[idx]];

                // Use pendingRefs to update refs
                refs[symbols[idx]] = pendingRef;

                emit RefDataUpdate(
                    symbols[idx],
                    refs[symbols[idx]].rate,
                    refs[symbols[idx]].resolveTime,
                    refs[symbols[idx]].requestID
                );

                // refs[symbols[idx]] = pendingRefs[symbols[idx]];
                if (resolveTimes[idx] > pendingRef.resolveTime) {
                    // updated pendingRefs using the input arguments
                    pendingRefs[symbols[idx]] = RefData({
                        rate: rates[idx],
                        resolveTime: resolveTimes[idx],
                        relayTime: uint64(block.timestamp),
                        requestID: requestIDs[idx]
                    });
                    emit PendingRefDataUpdate(
                        symbols[idx],
                        rates[idx],
                        resolveTimes[idx],
                        requestIDs[idx]
                    );
                }
            }
        }
    }

    /// @notice Relay and save a set of price data to the contract using proof from Bandchain
    /// @param proof Aggregator oralce script request proof from BandChain
    function relayWithProof(bytes calldata proof) external {
        (IBridge.RequestPacket memory req, IBridge.ResponsePacket memory res) =
            bridge.relayAndVerify(proof);

        // Check request ansCount >= specified
        require(res.ansCount >= ansCount, "MIN_ANS_COUNT_NOT_REACHED");

        // Check request askCount is the same as specified
        require(req.askCount == askCount, "ASK_COUNT_NOT_MATCHED");

        // Check request oracle script is in oracleScriptIDs
        require(
            checkOracleScriptID(req.oracleScriptID),
            "UNEXPECTED_ORACLE_SCRIPT_ID"
        );

        // Decode request parameters and result fields
        StdReferenceDecoder.Params memory params =
            StdReferenceDecoder.decodeParams(req.params);
        StdReferenceDecoder.Result memory result =
            StdReferenceDecoder.decodeResult(res.result);

        for (uint256 idx = 0; idx < params.symbols.length; idx++) {
            string memory symbol = params.symbols[idx];
            if (res.resolveTime > verifiedRefs[symbol].resolveTime) {
                uint64 rate =
                    uint64(
                        uint256(result.rates[idx]).mul(1e9).div(
                            uint256(params.multiplier)
                        )
                    );

                // Update pendingRefs using the request result
                verifiedRefs[symbol] = RefData({
                    rate: rate,
                    resolveTime: res.resolveTime,
                    relayTime: uint64(block.timestamp),
                    requestID: res.requestID
                });

                emit VerifiedRefDataUpdate(
                    symbol,
                    rate,
                    res.resolveTime,
                    res.requestID
                );
            }
        }
    }

    /// @notice Returns the price data for the given base/quote pair. Revert if not available.
    /// @param base the base symbol of the token pair to query
    /// @param quote the quote symbol of the token pair to query
    function getReferenceData(string memory base, string memory quote)
        public
        view
        override
        returns (ReferenceData memory)
    {
        (uint256 baseRate, uint256 baseLastUpdate) = getRefData(base);
        (uint256 quoteRate, uint256 quoteLastUpdate) = getRefData(quote);
        return
            ReferenceData({
                rate: (baseRate * 1e18) / quoteRate,
                lastUpdatedBase: baseLastUpdate,
                lastUpdatedQuote: quoteLastUpdate
            });
    }

    /// @notice Get the latest usable price data of a token
    /// @param symbol the symbol of the token whose price to query
    function getRefData(string memory symbol)
        public
        view
        returns (uint256 rate, uint256 lastUpdate)
    {
        if (keccak256(bytes(symbol)) == keccak256(bytes("USD"))) {
            return (1e9, block.timestamp);
        }

        RefData storage verifiedRefData = verifiedRefs[symbol];

        // If relayer is currently not trusted, use data from verifiedRefs
        if (!trustRelayer) {
            require(
                verifiedRefData.resolveTime > 0,
                "VERIFIED_REFS_DATA_NOT_AVAILABLE"
            );
            return (
                uint256(verifiedRefData.rate),
                uint256(verifiedRefData.resolveTime)
            );
        }

        RefData storage refData = refs[symbol];
        RefData storage pendingRefData = pendingRefs[symbol];

        RefData memory candidateRef;

        // Use pendingRefs as candidate source if resolveTime is older than pendingDuration
        if (pendingRefReady(symbol)) {
            candidateRef = pendingRefs[symbol];
        } else {
            candidateRef = refs[symbol];
        }

        // Compare resolveTime between candidateRefs and verifiedRefs
        // and use the newer one
        if (verifiedRefs[symbol].resolveTime > candidateRef.resolveTime) {
            candidateRef = verifiedRefs[symbol];
        }

        require(
            candidateRef.resolveTime > 0,
            "CANDIDATE_REFS_DATA_NOT_AVAILABLE"
        );
        return (uint256(candidateRef.rate), uint256(candidateRef.resolveTime));
    }

    /// @notice Check if the input oracle script ID is in the list of valid IDs
    /// @param oid The oracle script ID to query the validity of
    function checkOracleScriptID(uint64 oid) internal view returns (bool) {
        for (uint256 idx = 0; idx < oracleScriptIDs.length; idx++) {
            if (oracleScriptIDs[idx] == oid) {
                return true;
            }
        }
        return false;
    }

    /// @notice Check if a token data in pendingRef is ready to be used
    /// @param symbol The symbol of the token to query the status of
    function pendingRefReady(string memory symbol) public view returns (bool) {
        return (uint64(block.timestamp) - pendingRefs[symbol].resolveTime >=
            pendingDuration &&
            uint64(block.timestamp) - pendingRefs[symbol].relayTime >=
            pendingDuration);
    }
}
