from random import random
from brownie import (
    accounts,
    interface,
    GuestList,
    GuestListFactory
)
from config import *
from brownie import *

from scripts.mock_deploy_vault import mock_deploy_vault

userDepositCap = 100000 # $100000 dollars
totalDepositCap = 5000000 # $5M dollars

def test_guestlist_factory():
    stableCoin =  interface.IERC20(USDT)

    # deploy vault with WBTC as want
    want = WBTC
    isLp = False
    _deploy_guestlist_logic(stableCoin, want, isLp)

    # now deploy and test with a LP Token
    want = WBTC_ETH
    isLp = True
    _deploy_guestlist_logic(stableCoin, want, isLp)

    # print("[green]Guestlist was deployed at: [/green]", guestlist_proxy.address)

def _deploy_guestlist_logic(stableCoin, want, isLp):
    deployed_vault = mock_deploy_vault(want)
    vault = deployed_vault.vault
    dev = deployed_vault.deployer
    merkleRoot = "0x1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"

    # deploy guestlist factory
    factory = GuestListFactory.deploy(
        [UNISWAPV2_ROUTER, SUSHISWAP_ROUTER],
        CURVE_ROUTER,
        zero_address, # for the solidly router
        {"from":dev}
        )

    random_owner = accounts[2] # some random owner to set up for the guestlist
    # deploy guestlist using factory
    tx = factory.createGuestList(
        random_owner,
        vault,
        merkleRoot,
        userDepositCap,
        totalDepositCap,
        stableCoin,
        isLp,
        {"from":dev}
    )

    guestlist_proxy = GuestList.at(tx.return_value)

    guestlist_proxy.setUserDepositCap(100000, USDT, {"from": random_owner})
    guestlist_proxy.setTotalDepositCap(5000000, USDT, {"from": random_owner})

    assert guestlist_proxy.owner() == random_owner
    assert (guestlist_proxy.userDepositCap() > 0)
    assert (guestlist_proxy.totalDepositCap() > 0)
    assert (guestlist_proxy.guestRoot() == merkleRoot)
    assert (guestlist_proxy.wrapper() == vault)