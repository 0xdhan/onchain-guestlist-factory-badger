from brownie import (
    accounts,
    network,
    GuestListFactory
)

from dotmap import DotMap
from rich.console import Console
console = Console()

import click

# remember to change these VALUES depending on your choice

GUESTlIST_FACTORY="0x84b7096CA4DDED9373e2B3AAa99e054B0f857914" #Address of already deployed guestlist factory on this chain

BADGER_VAULT="0x1aaf7f8154704d80e2380b3dbc967fd0486016e0"
IS_LP=True # if the vault's want token is a lp

MERKLE_ROOT="0x1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"

USER_DEPOSIT_CAP=100000 # $100,000
TOTAL_DEPOSIT_CAP=5000000 # $5,000,000

STABLECOIN_ADDRESS="0x04068DA6C83AFCFA0e13ba15A6696662335D5B75"

def main():

    dev = connect_account()

    guestListFactory = GuestListFactory.at(GUESTlIST_FACTORY)

    guestListFactory.createGuestList(
        dev,
        BADGER_VAULT,
        MERKLE_ROOT,
        USER_DEPOSIT_CAP,
        TOTAL_DEPOSIT_CAP,
        STABLECOIN_ADDRESS,
        IS_LP,
        {"from":dev}
    )


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev