// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface IGuestList {
    function setUserDepositCap(uint256 cap_, address _stableCoin) external;

    function setTotalDepositCap(uint256 cap_, address _stableCoin) external;

    function initialize(
        address _wrapper,
        bytes32 _guestRoot,
        address[] calldata _uniswapRouters,
        address _solidlyRouter,
        address _curveRouter,
        uint256 _userDepositCap,
        uint256 _totalDepositCap,
        address _stableCoin,
        bool _isLp
    ) external;
}
