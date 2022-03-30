// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;

import {IERC20} from "../../interfaces/erc20/IERC20.sol";

interface BadgerWrapperApi is IERC20 {
    function token() external view returns (address);

    function pricePerShare() external view returns (uint256);

    function totalWrapperBalance(address account)
        external
        view
        returns (uint256);

    function totalVaultBalance(address account) external view returns (uint256);
}
