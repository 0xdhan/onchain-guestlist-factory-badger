from brownie import (
    accounts,
    network,
    GuestList,
    GuestListFactory
)

from dotmap import DotMap
from rich.console import Console
console = Console()

import click

# remember to change these VALUES depending on the chain you are deploying to 
# current addresses are for deploying on Fantom Chain
uniswapv2_routers = ["0xF491e7B69E4244ad4002BC14e878a34207E38c29", "0x16327E3FbDaCA3bcF7E38F5Af2599D2DDc33aE52"]
curve_router="0x74E25054e98fd3FCd4bbB13A962B43E49098586f"
solidly_router="0xa38cd27185a464914D3046f0AB9d43356B34829D"

def main():

    dev = connect_account()

    factory = GuestListFactory.deploy(uniswapv2_routers,curve_router, solidly_router, {'from': dev}, publish_source=True)

def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev