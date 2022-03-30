// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@openzeppelin-contracts-upgradeable/proxy/ClonesUpgradeable.sol";
import "@openzeppelin-contracts-upgradeable/access/OwnableUpgradeable.sol";

import {GuestList} from "./GuestList.sol";
import {IGuestList} from "./interfaces/IGuestList.sol";

contract GuestListFactory {
    address public immutable guestlist_implementation;
    address public immutable SOLIDLY_ROUTER;
    address public immutable CURVE_ROUTER;
    address[] public UNISWAP_ROUTERS;

    event GuestListDeployed(address);

    constructor(
        address[] memory _uniswapRouters,
        address _curveRouter,
        address _solidlyRouter
    ) public {
        guestlist_implementation = address(new GuestList());
        UNISWAP_ROUTERS = _uniswapRouters;
        CURVE_ROUTER = _curveRouter;
        SOLIDLY_ROUTER = _solidlyRouter;
    }

    /**
      @notice deploys a new guestlist contract
      @param _owner : address of new owner for the guestlist,
      @param _wrapper : address of the vault,
      @param _guestRoot : the merkle root,
      @param _userDepositCap : maximum deposit by a single user in dollars,
      @param _totalDepositCap : maximum deposit to the vault in dollars,
      @param _stableCoin : address of the stablecoin which will be used to find the price of the vault want in the given routers,
      @param _isLp : if the want token for the vault is a lp token or not. This value will also be stored in the guestlist contract storage to later decide if the vault want is an lp or not for pricing functions
     */
    function createGuestList(
        address _owner,
        address _wrapper,
        bytes32 _guestRoot,
        uint256 _userDepositCap,
        uint256 _totalDepositCap,
        address _stableCoin,
        bool _isLp
    ) external returns (address) {
        address guestlist = ClonesUpgradeable.clone(guestlist_implementation);

        IGuestList(guestlist).initialize(
            _wrapper,
            _guestRoot,
            UNISWAP_ROUTERS,
            SOLIDLY_ROUTER,
            CURVE_ROUTER,
            _userDepositCap,
            _totalDepositCap,
            _stableCoin,
            _isLp
        );

        OwnableUpgradeable(guestlist).transferOwnership(_owner);

        emit GuestListDeployed(guestlist);

        return guestlist;
    }
}
