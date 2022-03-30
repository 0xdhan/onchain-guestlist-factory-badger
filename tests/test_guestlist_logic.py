# Modified from https://github.com/Badger-Finance/badger-sett-1.5/blob/main/tests/test_guestlist.py

import brownie
from brownie import *

AddressZero = "0x0000000000000000000000000000000000000000"
MaxUint256 = str(int(2 ** 256 - 1))

## Test where you add a guestlist
def test_add_guestlist(deployer, governance, randomUser, vault, guestlist, want):
    # Adding deployer to guestlist
    guestlist.setGuests([deployer], [True], {"from": governance})

    # Sets guestlist on Vault (Requires Vault's governance)
    vault.setGuestList(guestlist.address, {"from": governance})

    depositAmount = (
        1e18 if want.balanceOf(deployer) >= 1e18 else want.balanceOf(deployer)
    )

    assert depositAmount != 0

    # Deposit
    want.approve(vault, MaxUint256, {"from": deployer})

    before_shares = want.balanceOf(vault)

    assert before_shares == 0

    vault.deposit(depositAmount, {"from": deployer})

    after_shares = want.balanceOf(vault)

    assert after_shares == depositAmount

    # Deposit from user who is not in guestlist should fail
    want.approve(vault, MaxUint256, {"from": randomUser})
    depositAmount = (
        1e18 if want.balanceOf(randomUser) >= 1e18 else want.balanceOf(randomUser)
    )
    assert depositAmount != 0
    with brownie.reverts():
        vault.deposit(depositAmount, {"from": randomUser})


## Test where you add a guestlist, remove it and anyone can deposit
def test_add_remove_guestlist(deployer, governance, randomUser, vault, guestlist, want):
    # Adding deployer to guestlist
    guestlist.setGuests([deployer], [True], {"from": governance})

    # Sets guestlist on Vault (Requires Vault's governance)
    vault.setGuestList(guestlist.address, {"from": governance})

    depositAmount = (
        1e18 if want.balanceOf(deployer) >= 1e18 else want.balanceOf(deployer)
    )

    assert depositAmount != 0

    # Deposit
    want.approve(vault, MaxUint256, {"from": deployer})

    before_shares = want.balanceOf(vault)

    assert before_shares == 0

    vault.deposit(depositAmount, {"from": deployer})

    after_shares = want.balanceOf(vault)

    assert after_shares == depositAmount

    # Deposit from user who is not in guestlist should fail
    want.approve(vault, MaxUint256, {"from": randomUser})
    depositAmount = (
        1e18 if want.balanceOf(randomUser) >= 1e18 else want.balanceOf(randomUser)
    )
    assert depositAmount != 0
    with brownie.reverts():
        vault.deposit(depositAmount, {"from": randomUser})

    # Removing guestlist ie. setting it to AddresZero
    vault.setGuestList(AddressZero, {"from": governance})

    # Deposit from randomUser should work now after guestlist is removed
    depositAmount = (
        1e18 if want.balanceOf(randomUser) >= 1e18 else want.balanceOf(randomUser)
    )
    assert depositAmount != 0
    vault.deposit(depositAmount, {"from": randomUser})


## Test where you deposit when guestlist is set
def test_deposit_guestlist(deployer, governance, randomUser, vault, guestlist, want):
    # Adding deployer to guestlist
    guestlist.setGuests([deployer], [True], {"from": governance})

    # Sets guestlist on Vault (Requires Vault's governance)
    vault.setGuestList(guestlist.address, {"from": governance})

    depositAmount = (
        1e18 if want.balanceOf(deployer) >= 1e18 else want.balanceOf(deployer)
    )

    assert depositAmount != 0

    # Deposit
    want.approve(vault, MaxUint256, {"from": deployer})

    before_shares = want.balanceOf(vault)

    assert before_shares == 0

    vault.deposit(depositAmount // 10, [], {"from": deployer})

    after_shares = want.balanceOf(vault)

    assert after_shares == depositAmount // 10

    want.approve(vault, MaxUint256, {"from": randomUser})
    depositAmount = (
        1e18 if want.balanceOf(randomUser) >= 1e18 else want.balanceOf(randomUser)
    )
    assert depositAmount != 0

    vault.depositFor(deployer, depositAmount, [], {"from": randomUser})

## Test with guestlist -> user Limit
def test_userlimit_guestlist_in_want(deployer, governance, randomUser, vault, guestlist, want):
    # NOTE: set userCap = 2e18
    guestlist.setUserDepositCapInWant(2e18, {"from": governance})
    # Adding deployer and randomUser to guestlist
    guestlist.setGuests([deployer, randomUser], [True, True], {"from": governance})

    # Sets guestlist on Vault (Requires Vault's governance)
    vault.setGuestList(guestlist.address, {"from": governance})

    whale = deployer

    want.approve(vault, MaxUint256, {"from": whale})
    want.approve(vault, MaxUint256, {"from": randomUser})

    # Whale in guestlist trying to deposit a 10 ETH into vaults should fail
    depositAmount = 10e18
    assert depositAmount <= want.balanceOf(whale)
    with brownie.reverts():
        vault.deposit(depositAmount, {"from": whale})

    # randomUser in guestlist depositing 1 ether should work
    depositAmount = (
        1e18 if want.balanceOf(randomUser) >= 1e18 else want.balanceOf(randomUser)
    )
    assert depositAmount != 0
    vault.deposit(depositAmount, {"from": randomUser})

    ## NOTE: increasing userCap to 10 ether
    guestlist.setUserDepositCapInWant(10e18, {"from": governance})
    assert guestlist.userDepositCap() == 10e18

    # Now Whale should be able to deposit
    depositAmount = 10e18
    assert depositAmount <= want.balanceOf(whale)
    vault.deposit(depositAmount, {"from": whale})


## Test with guestlist -> want Limit
def test_wantlimit_guestlist_in_want(deployer, governance, randomUser, vault, guestlist, want):
    # NOTE: set userCap = 2e18
    guestlist.setUserDepositCapInWant(2e18, {"from": governance})
    # NOTE: set totalCap = 50e18
    guestlist.setTotalDepositCapInWant(50e18, {"from": governance})

    # Adding deployer and randomUser to guestlist
    guestlist.setGuests([deployer, randomUser], [True, True], {"from": governance})

    # Sets guestlist on Vault (Requires Vault's governance)
    vault.setGuestList(guestlist.address, {"from": governance})

    whale1 = deployer
    whale2 = randomUser

    want.approve(vault, MaxUint256, {"from": whale1})
    want.approve(vault, MaxUint256, {"from": whale2})

    # Change totalCap to a smaller value
    # totalCap = 3e18
    guestlist.setTotalDepositCapInWant(3e18, {"from": governance})
    assert guestlist.totalDepositCap() == 3e18

    # Whale1 apes and deposits 2 ether
    depositAmount = 2e18
    assert depositAmount <= want.balanceOf(whale1)
    vault.deposit(depositAmount, {"from": whale1})

    # Whale2 also tries to ape in with max userCap amount of 2 ether but as totalCap = 3e18, deposit should fail
    depositAmount = 2e18
    assert depositAmount <= want.balanceOf(whale2)
    with brownie.reverts():
        vault.deposit(depositAmount, {"from": whale2})

    # Increasing totalCap to 4 ether
    # totalCap = 4e18
    guestlist.setTotalDepositCapInWant(4e18, {"from": governance})
    assert guestlist.totalDepositCap() == 4e18

    # Now Whale2 deposit should go through :)
    depositAmount = 2e18
    assert depositAmount <= want.balanceOf(whale2)
    vault.deposit(depositAmount, {"from": whale2})