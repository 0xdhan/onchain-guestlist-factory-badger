from brownie import (
    accounts,
    GuestList,
    GuestListFactory
)

from config import *

from dotmap import DotMap
from rich.console import Console
console = Console()

def mock_deploy_guestlist_using_factory(vault, random_owner, deployer, stableCoin, userDepositCap, totalDepositCap, isLp):
    dev = deployer
    merkleRoot = "0x1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"

    assert userDepositCap > 0
    assert totalDepositCap > 0

    # deploy guestlist factory
    factory = GuestListFactory.deploy(
        [UNISWAPV2_ROUTER, SUSHISWAP_ROUTER],
        CURVE_ROUTER,
        zero_address, # for the solidly router
        {"from":dev}
        )

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

    assert guestlist_proxy.owner() == random_owner

    assert guestlist_proxy.userDepositCap() > 0
    assert guestlist_proxy.totalDepositCap() > 0

    console.print("[green]Guestlist was deployed at: [/green]", guestlist_proxy.address)

    return DotMap(
        owner=random_owner,
        guestlist=guestlist_proxy,
        stableCoin = stableCoin,
        userDepositCap = userDepositCap,
        totalDepositCap = totalDepositCap,
        merkleRoot = merkleRoot,
        vault = vault
    )
