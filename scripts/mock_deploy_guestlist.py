from brownie import (
    accounts,
    GuestList,
    AdminUpgradeabilityProxy
)

from config import *

from dotmap import DotMap
from rich.console import Console
console = Console()

def mock_deploy_guestlist(vault, deployer, stableCoin, userDepositCap, totalDepositCap, isLp):
    dev = deployer
    merkleRoot = "0x1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"

    guestlist_logic = GuestList.deploy({"from": dev})

    # Initializing arguments
    args = [vault,
        merkleRoot,
        [UNISWAPV2_ROUTER, SUSHISWAP_ROUTER],
        zero_address, # for the solidly router
        CURVE_ROUTER,
        userDepositCap,
        totalDepositCap,
        stableCoin]

    guestlist_logic.initialize(vault,
        merkleRoot,
        [UNISWAPV2_ROUTER, SUSHISWAP_ROUTER],
        zero_address, # for the solidly router
        CURVE_ROUTER,
        userDepositCap,
        totalDepositCap,
        stableCoin,
        isLp,
         {"from":dev})

    # args = [vault]

    # guestlist_proxy = AdminUpgradeabilityProxy.deploy(
    #     guestlist_logic,
    #     dev,
    #     guestlist_logic.initialize.encode_input(*args),
    #     {"from": dev},
    # )

    # time.sleep(1)

    # ## We delete from deploy and then fetch again so we can interact
    # AdminUpgradeabilityProxy.remove(guestlist_proxy)
    # guestlist_proxy = GuestList.at(guestlist_proxy.address)

    # console.print("[green]Guestlist was deployed at: [/green]", guestlist_proxy.address)

    return DotMap(
        deployer=dev,
        guestlist=guestlist_logic,
        stableCoin = stableCoin,
        userDepositCap = userDepositCap,
        totalDepositCap = totalDepositCap,
        merkleRoot = merkleRoot,
        vault = vault
    )
