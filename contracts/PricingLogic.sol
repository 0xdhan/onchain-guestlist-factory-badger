// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@openzeppelin-contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin-contracts-upgradeable/token/ERC20/SafeERC20Upgradeable.sol";

import "../interfaces/erc20/IERC20.sol";
import "../interfaces/uniswap/IUniswapV2Pair.sol";
import "../interfaces/uniswap/IUniswapRouterV2.sol";
import "../interfaces/solidly/IBaseV1Router01.sol";
import "../interfaces/curve/ICurveRouter.sol";

contract PricingLogic is OwnableUpgradeable {
    using SafeERC20Upgradeable for IERC20;
    using SafeMathUpgradeable for uint256;

    address[] public UNISWAP_ROUTERS;
    address public SOLIDLY_ROUTER;
    address public CURVE_ROUTER;

    function __Pricing_init(
        address[] calldata _uniswapRouters,
        address _solidlyRouter,
        address _curveRouter
    ) public initializer {
        __Ownable_init();
        UNISWAP_ROUTERS = _uniswapRouters;
        SOLIDLY_ROUTER = _solidlyRouter;
        CURVE_ROUTER = _curveRouter;
    }

    /**
     * @notice get LP token price in _tokenOut denomination
     */
    function getLpPrice(address _lpToken, address _tokenOut)
        public
        view
        returns (uint256)
    {
        address token0 = IUniswapV2Pair(_lpToken).token0();
        address token1 = IUniswapV2Pair(_lpToken).token1();
        uint256 totalSupply = IUniswapV2Pair(_lpToken).totalSupply();

        (uint256 r0, uint256 r1, ) = IUniswapV2Pair(_lpToken).getReserves();

        uint256 px0 = getOptimalPrice(token0, _tokenOut);
        uint256 px1 = getOptimalPrice(token1, _tokenOut);

        return (r0.mul(px0).add(r1.mul(px1))).div(totalSupply);
    }

    /**
     * @notice get the optimal price for one unit _tokenIn in denomination of _tokenOut
     */
    function getOptimalPrice(address _tokenIn, address _tokenOut)
        public
        view
        returns (uint256 price)
    {
        uint256 amountIn = 10**IERC20(_tokenIn).decimals(); // One unit of tokenIn
        if (_tokenIn == _tokenOut) {
            // if tokenIn is equal to tokenOut
            // the price of one token will be simply one unit of tokenOut
            return amountIn;
        }
        uint256 quote;
        // first check all the uniswap routers
        for (uint256 i = 0; i < UNISWAP_ROUTERS.length; i++) {
            if (UNISWAP_ROUTERS[i] != address(0)) {
                quote = getUniswapV2Quote(
                    _tokenIn,
                    _tokenOut,
                    amountIn,
                    UNISWAP_ROUTERS[i]
                );

                if (quote > price) {
                    price = quote;
                }
            }
        }

        // curve router
        if (CURVE_ROUTER != address(0)) {
            quote = getCurveQuote(_tokenIn, _tokenOut, amountIn);
            if (quote > price) {
                price = quote;
            }
        }

        // solidly router
        if (SOLIDLY_ROUTER != address(0)) {
            quote = getSolidlyQuote(_tokenIn, _tokenOut, amountIn);
            if (quote > price) {
                price = quote;
            }
        }
    }

    /**
     * @notice returns the price of _amountIn number of _tokenIn in _tokenOut denomination using uniswapV2
     */
    function getUniswapV2Quote(
        address _tokenIn,
        address _tokenOut,
        uint256 _amountIn,
        address _router
    ) public view returns (uint256 quote) {
        address[] memory path = new address[](2);
        path[0] = _tokenIn;
        path[1] = _tokenOut;

        try IUniswapRouterV2(_router).getAmountsOut(_amountIn, path) returns (
            uint256[] memory amounts
        ) {
            quote = amounts[amounts.length - 1]; // Last one is the outToken
        } catch (bytes memory) {
            // We ignore as it means it's zero
        }
    }

    /**
     * @notice returns the price of _amountIn number of _tokenIn in _tokenOut denomination using solidly
     */
    function getSolidlyQuote(
        address _tokenIn,
        address _tokenOut,
        uint256 _amountIn
    ) public view returns (uint256 quote) {
        (quote, ) = IBaseV1Router01(SOLIDLY_ROUTER).getAmountOut(
            _amountIn,
            _tokenIn,
            _tokenOut
        );
    }

    /**
     * @notice returns the price of _amountIn number of _tokenIn in _tokenOut denomination using curve
     */
    function getCurveQuote(
        address _tokenIn,
        address _tokenOut,
        uint256 _amountIn
    ) public view returns (uint256 quote) {
        (, quote) = ICurveRouter(CURVE_ROUTER).get_best_rate(
            _tokenIn,
            _tokenOut,
            _amountIn
        );
    }
}
