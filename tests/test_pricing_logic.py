from brownie import (
    accounts,
    interface,
    GuestList,
)
from config import *
from brownie import *

from scripts.mock_deploy_guestlist_using_factory import mock_deploy_guestlist_using_factory
from scripts.mock_deploy_vault import mock_deploy_vault

userDepositCap = 100000 # $100000 dollars
totalDepositCap = 5000000 # $5M dollars

def test_pricing_logic():
    stableCoin =  interface.IERC20(USDT)
    # deploy vault with WBTC as want
    deployed_vault = mock_deploy_vault(WBTC)
    isLp = False
    vault = deployed_vault.vault
    dev = deployed_vault.deployer

    deployed_guestlist = mock_deploy_guestlist_using_factory(vault, dev, dev, stableCoin, userDepositCap, totalDepositCap, isLp)
    dev = deployed_guestlist.owner
    guestlist = deployed_guestlist.guestlist
    want = interface.IERC20(vault.token())

    assert (want == WBTC)

    depositCapTest(guestlist, stableCoin, want, dev)
    
    # test each individual quote methods for normal token one by one first
    uniswap_quote = uniswapV2QuoteTest(guestlist, stableCoin, want, UNISWAPV2_ROUTER)
    sushi_quote = uniswapV2QuoteTest(guestlist, stableCoin, want, SUSHISWAP_ROUTER)
    solidly_quote  =solidlyQuoteTest(guestlist, stableCoin, want)
    curve_quote = curveQuoteTest(guestlist, stableCoin, want)

    quotes = [uniswap_quote, sushi_quote, solidly_quote, curve_quote]
    # test the optimal price code
    optimalPriceTest(guestlist, stableCoin, want, quotes)

def test_pricing_logic_lp():
    stableCoin =  interface.IERC20(USDT)
    want = WBTC_ETH

    _pricing_logic_lp_test(stableCoin, want)

def test_pricing_logic_lp_with_one_part_of_lp_token_same_as_stableCoin():
    stableCoin = interface.IERC20(USDT)
    want = WBTC_USDT

    # here second token of the lp is USDT, which is similar as our outToken which is also USDT
    _pricing_logic_lp_test(stableCoin, want)


def _pricing_logic_lp_test(stableCoin, want):
    # deploy the vault again with a LP token (WBTC/WETH) as want
    deployed_vault = mock_deploy_vault(want)
    isLp = True
    dev = deployed_vault.deployer
    vault = deployed_vault.vault
    assert (want == vault.token())
    
    want = Contract.from_explorer(want)

    deployed_guestlist = mock_deploy_guestlist_using_factory(vault,dev, dev, stableCoin, userDepositCap, totalDepositCap, isLp)

    dev = deployed_guestlist.owner
    guestlist = deployed_guestlist.guestlist

    actual_lp_price = guestlist.getLpPrice(want, stableCoin)

    # calculate expected lp price
    (r0, r1, _) = want.getReserves()
    px0 = guestlist.getOptimalPrice(want.token0(), stableCoin)
    px1 = guestlist.getOptimalPrice(want.token1(), stableCoin)
    totalSupply = want.totalSupply()

    expected_lp_price = ((r0 * px0) + (r1 * px1)) //  totalSupply

    assert actual_lp_price == expected_lp_price

    depositCapLpTokenTest(guestlist, stableCoin, want, dev)
    

def depositCapTest(guestlist, stableCoin, want, dev):
    optimal_price  = guestlist.getOptimalPrice(want, stableCoin)
    _depositCapTestLogic(optimal_price, guestlist, stableCoin, want, dev)

def depositCapLpTokenTest(guestlist, stableCoin, want, dev):
    optimal_price = guestlist.getLpPrice(want, stableCoin)
    _depositCapTestLogic(optimal_price, guestlist, stableCoin, want, dev)

def _depositCapTestLogic(optimal_price, guestlist, stableCoin, want, dev):
    guestlist.setUserDepositCap(userDepositCap, stableCoin, {"from": dev})
    expected_cap_in_want = (userDepositCap * (10 ** (stableCoin.decimals() + want.decimals()))) // optimal_price
    actual_cap_in_want = guestlist.userDepositCap()
    assert (expected_cap_in_want == actual_cap_in_want)

    guestlist.setTotalDepositCap(5000000, stableCoin, {"from": dev})
    expected_cap_in_want = (totalDepositCap * (10 ** (stableCoin.decimals() + want.decimals()))) // optimal_price
    actual_cap_in_want = guestlist.totalDepositCap()
    assert (expected_cap_in_want == actual_cap_in_want)


def optimalPriceTest(guestlist, stableCoin, want, quotes):
    expected_optimal_quote = max(quotes)
    acutal_optimal_quote = guestlist.getOptimalPrice(want, stableCoin)

    assert (expected_optimal_quote == acutal_optimal_quote)

def uniswapV2QuoteTest(guestlist, stableCoin, want, router_address):
    if router_address != zero_address:
        router = Contract.from_explorer(router_address)
        amount = 10 ** want.decimals()
        path = [want, stableCoin]

        try:
            expected_quotes = router.getAmountsOut(amount, path)
            expected_quote = expected_quotes[-1]
        except:
            expected_quote = 0
        actual_quote = guestlist.getUniswapV2Quote(want, stableCoin, amount, router)

        assert (expected_quote == actual_quote)

        return actual_quote

def solidlyQuoteTest(guestlist, stableCoin, want):
    if (SOLIDLY_ROUTER != zero_address):
        router = Contract.from_explorer(SOLIDLY_ROUTER)
        amount = 10 ** want.decimals()

        expected_quote = router.getAmountOut(amount, want, stableCoin)[0]
        actual_quote = guestlist.getSolidlyQuote(want, stableCoin, amount)

        assert (expected_quote == actual_quote)

        return actual_quote

def curveQuoteTest(guestlist, stableCoin, want):
    if (CURVE_ROUTER != zero_address):
        router = Contract.from_explorer(CURVE_ROUTER)
        amount = 10 ** want.decimals()

        expected_quote = router.get_best_rate(want, stableCoin, amount)[1]
        actual_quote = guestlist.getCurveQuote(want, stableCoin, amount)

        assert (expected_quote == actual_quote)

        return actual_quote