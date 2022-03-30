# Badger Onchain Guestlist Factory

The GuestListFactory.sol is the factory contract through which new guestlist contracts can be deployed.

The GuestListFactory is multichain compatible. On deployment of this contract you have to provide 3 parameters

```
      address[] _uniswapRouters,
      address _curveRouter,
      address _solidlyRouter
```

The curveRouter and solidlyRouter is simple, where you have to input the curveRouter address and the solidlyRouter address
of that chain respectively.

But "uniswapRouters" takes an array of UniswapV2Router addresses. This is because most chains have multiple forks of UniSwapV2
like sushiswap, spooky, quickswap, etc.

This router addresses will be used by the guestlist contracts to calculate the value of the want in the USD.

In case there is no router of that type in that chain, input zero address for the others and an empty list in case of \_uniswapRouters.

Next to deploy a GuestList Contract using the GuestListFactory, you have to call its createGuestList() method which takes the following
parameters:

```
      address _owner : address of new owner for the guestlist,
      address _wrapper : address of the vault,
      bytes32 _guestRoot : the merkle root,
      uint256 _userDepositCap : maximum deposit by a single user in dollars,
      uint256 _totalDepositCap : maximum deposit to the vault in dollars,
      address _stableCoin : address of the stablecoin which will be used to find the price of the vault want in the given routers,
      bool _isLp : if the want token for the vault is a lp token or not. This value will also be stored in the guestlist contract storage to later decide if the vault want is an lp or not for pricing functions.
```

As defined in the bounty, the userDepositCap is to be given in dollar amounts (10000 = $10000).
Internally the contract will convert it to equivalent want amount and update the userDepositCap param in the contract.

There are two cases here. Either the want of the vault is a noraml ERC20 token or an LP token.
The price derivation for a LP token is a little different than a normal ERC20 token.

First step is to get the price of one want token in terms of USD. Then we can use that to convert userDepositCap from USD to want.

#### Case 1: If the vault want is a normal token

Then the getOptimalPrice() method is triggered. This will check the exchange_rate of 1 Unit Want Token against the provided stableCoin, in all the routers and output the best rate.

Note: The stablecoin address provided will be used to find the exchange rate of the want in routers. For example, if the provided want is WBTC & the stableCoin is USDT, then the contract will look for the WBTC price in the WBTC/USDT pools in the given routers. So make sure to provide an stablecoin with good liquidity like USDT, USDC, DAI, etc.

#### Case 2: If the vault want is a LP token

Then the getLpPrice() method will be triggered. This will first separate the LP token into its underlying tokens. Then it will use the getOptimalPrice() method to find the unit price of each individual underlying token. Then it will take the underlying reserves in the lp and the totalSupply of the lp token. Finally we find the LP unit price using the following formula

```
   ((token0Price * token0Reserve) + (token1Price * token1Reserve)) / totalSupply
```

Once we have the unit price of the vault want token, we convert the userDepositCap & totalDepositCap from USD to want using the internal method \_stableToWant().

Two other methods where the pricing logic is used are the setUserDepositCap() and setTotalDepositCap() methods. The parameters are

```
uint256 _cap: The cap in dollars
address _stableCoin: The address of the stablecoin to be used to get the price of the want against in the routers

```

Including, this I have also added two other methods setUserDepositCapInWant() & setTotalDepositCapInWant(). This takes only one param

```
   uint256 _cap: The cap in terms of want amounts
```

So instead of dollars, if you want to update the respective caps in terms of want amounts then you may use this. This will directly update the userDepositCap & totalDepositCap storage variables without any price conversion.

Rest of the guest list authorization methods has been kept same as badger's TestVipCappedGuestListBbtcUpgradeable.sol file.

## Tests

Tests for the pricing logic & the guestlist factory has been added. Test for the guestlist authorization logic has been taken from the original badger's test file with a little modification.

To run tests run

```
   brownie test -s
```

## Gas Costs

Note: Since the contract will loop through all the uniswapv2 routers provided, so the gas cost will also depend on the number
of routers provided.

Also Lp token pricing gas cost is higher than normal token because, in the lp token we separate it and then get optimal price of each
underlying token individually including some more calculation.

#### When Vault's want is LP Token

<img width="711" alt="Screenshot 2022-03-14 at 7 17 41 PM" src="https://user-images.githubusercontent.com/101333892/158185424-6cda6506-2abf-4d08-bf35-7ec4918ebeb1.png">

#### When Vault's want is nomral ERC20 token

<img width="707" alt="Screenshot 2022-03-14 at 7 14 16 PM" src="https://user-images.githubusercontent.com/101333892/158185434-7e93faa1-75c4-424c-a53a-f3e81a47d7ec.png">

## Deployments (FTM Chain)

(Production deployment scripts have been added to the scripts folder)

1. GuestListFactory: [0x84b7096CA4DDED9373e2B3AAa99e054B0f857914](https://ftmscan.com/address/0x84b7096CA4DDED9373e2B3AAa99e054B0f857914#readContract)
2. Sample Guestlist 1 (using factory): [0xa612cb192e7b6c98982888e31d1c55aebdc831cd](https://ftmscan.com/address/0xa612cb192e7b6c98982888e31d1c55aebdc831cd)
3. Sample Guestlist 2 (using factory): [0x61645813E25AcA5491369171D462a397CB252262](https://ftmscan.com/address/0x61645813E25AcA5491369171D462a397CB252262)

## Further Improvements

1. <strong>Optimizing the getLpPrice() method</strong> : One thing we can do is, if any of the underlying tokens is a stablecoin, then we can directly take its unit price as 1 unit token since all stablecoins are roughly equal to 1 USD. This will save us a lot of gas. But for this we will need to know if a token is a stablecoin or not. Maybe we can do this by deploying a StableCoinRegistry which stores a mapping of stablecoin addreses.
2. <strong>Making the router addresses on the guestlist factory changeable by factory owner.</strong> Currently the router addresses once entered on GuestListFactory deployment cant be changed later. Maybe if you think that you need to update them in the future, then you may add some more authorized set methods to set the router addresses.
