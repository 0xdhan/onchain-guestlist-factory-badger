from brownie import (
    accounts,
    Vault,
    DemoStrategy,
)

from config import *

from dotmap import DotMap
from rich.console import Console
console = Console()

def mock_deploy_vault(want):
    """
    Deploys, vault and test strategy, mock token and wires them up.
    """
    token = want
    deployer = accounts[1]

    strategist = accounts[2]
    keeper = accounts[3]
    guardian = accounts[4]

    governance = accounts[5]
    proxyAdmin = accounts[6]

    badgerTree = accounts[7]
    randomUser = accounts[8]

    # token = MockToken.deploy({"from": deployer})
    # token.initialize(
    #     [deployer.address, randomUser.address], [100 * 10 ** 18, 100 * 10 ** 18]
    # )

    performanceFeeGovernance = 1000
    performanceFeeStrategist = 1000
    withdrawalFee = 50
    managementFee = 50

    vault = Vault.deploy({"from": deployer})
    vault.initialize(
        token,
        governance,
        keeper,
        guardian,
        governance,
        strategist,
        badgerTree,
        "",
        "",
        [
            performanceFeeGovernance,
            performanceFeeStrategist,
            withdrawalFee,
            managementFee,
        ],
    )
    # NOTE: Vault starts unpaused

    strategy = DemoStrategy.deploy({"from": deployer})
    strategy.initialize(vault, [token], {"from":deployer})
    # NOTE: Strategy starts unpaused

    vault.setStrategy(strategy, {"from": governance})

    return DotMap(
        deployer=deployer,
        vault=vault,
        strategy=strategy,
        want=token,
        governance=governance,
        proxyAdmin=proxyAdmin,
        randomUser=randomUser,
        performanceFeeGovernance=performanceFeeGovernance,
        performanceFeeStrategist=performanceFeeStrategist,
        withdrawalFee=withdrawalFee,
        badgerTree=badgerTree
    )