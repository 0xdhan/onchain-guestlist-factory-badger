from brownie import (
    accounts,
    interface
)

from config import *

import pytest
from dotmap import DotMap

from scripts.mock_deploy_vault import mock_deploy_vault
from scripts.mock_deploy_guestlist_using_factory import mock_deploy_guestlist_using_factory

@pytest.fixture
def deployed_vault():
    """
    Deploys, vault and test strategy and wires them up.
    """
    want = WETH
    isLp = False
    deployed_vault = mock_deploy_vault(want)

    return DotMap(
        deployer = deployed_vault.deployer,
        vault = deployed_vault.vault,
        want = deployed_vault.want,
        governance = deployed_vault.governance,
        randomUser = deployed_vault.randomUser,
        isLp = isLp
    )
    
@pytest.fixture
def deployed_guestlist(deployed_vault):
    """
        Deploy guestlist using the guestlist factory
    """
    deployed_guestlist = mock_deploy_guestlist_using_factory(
        deployed_vault.vault,
        deployed_vault.governance, # owner of the guestlist
        deployed_vault.deployer, # deployer for the guestlist
        USDT, # stable coin to be used in the guestlist pricing logic
        10000, # user deposit cap in dollars
        500000, # total deposit cap in dollars
        deployed_vault.isLp # if want of the vault is lp or not
    )

    return DotMap(
        governance = deployed_guestlist.owner,
        guestlist = deployed_guestlist.guestlist,
        stableCoin = deployed_guestlist.stableCoin,
        userDepositCap = deployed_guestlist.userDepositCap,
        totalDepositCap = deployed_guestlist.totalDepositCap,
        merkleRoot = deployed_guestlist.merkleRoot,
        vault = deployed_guestlist.vault
    )

@pytest.fixture
def guestlist(deployed_guestlist):
    return deployed_guestlist.guestlist

@pytest.fixture
def vault(deployed_guestlist):
    return deployed_guestlist.vault

@pytest.fixture
def deployer():
    # some WETH whale
    return accounts.at("0x56178a0d5f301baf6cf3e1cd53d9863437345bf9", force=True)

@pytest.fixture
def governance(deployed_guestlist):
    return deployed_guestlist.governance

@pytest.fixture
def randomUser():
    return accounts.at("0x6a3528677e598b47952749b08469ce806c2524e7", force=True)

@pytest.fixture
def guestlist(deployed_guestlist):
    return deployed_guestlist.guestlist

@pytest.fixture
def want(deployed_vault):
    return interface.IERC20(deployed_vault.want)