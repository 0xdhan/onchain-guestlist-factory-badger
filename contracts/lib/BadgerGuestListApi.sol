// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;

interface BadgerGuestListApi {
    function authorized(
        address guest,
        uint256 amount,
        bytes32[] calldata merkleProof
    ) external view returns (bool);

    function setGuests(address[] calldata _guests, bool[] calldata _invited)
        external;
}
