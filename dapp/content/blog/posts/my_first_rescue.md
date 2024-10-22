title  : My first rescue (sort of)
notice : A router rescue for $120k, via a simple repurposing of a remove liquidity function.
date   : 22-10-2024
author : Maka

tags   : uniswap, v2, rescue
series : Tales from the forest

## Preamble
Aside from rehashing past glory and while feeling mechanically a bit outdated, I think this can serve as a good foundation for future posts and be something we refer back to.

It's the story of a v2 router <a href='https://x.com/HHK_eth/status/1469408791217250308'>rescue for $120k</a>, using the simple exploitation (in a good way) of a remove liquidity function.
I say sort of my first rescue because while I was the one handling the ticket, it was very much my friend who found the solution and it took him answering my questions to understand
the mechanic at the time.<br>

Afterwards I became quite interested in searching for discrepancies between the intention and the potential of a given mechanic, as they can be found all over
(particularly where any interoperation between contacts occures).

#### The problem
It is still incredibly common for people to transfer tokens to the wrong address, and while this has been helped through additonal checks on transfer by the well known wallet providers,
it doesn't solve a most common cause which is attempting to interact with a contracts functions programatically.

Addresses can be confused, function arguments can be missinterpretted, and developers of all levels love to test live. This has resulted in
destinations being set incorrectly, and in many cases with no way to recover the tokens.
<blockquote class='note'>
Some of my most gut renching convos where with people who had sent dizzying sums to the Sushi token contract.
</blockquote>
However, for Uniswaps v2 router there is a way to rescue ERC20 tokens, we just need to be quick enough to grab them before someone who won't give them back.

## Technicals
In the case of the v2 router rescue we are taking advantage of the unique mechanics in one of the `SupportingFeeOnTransfer` variants from the list of `removeLiquidity` functions.
The reason this variant exists is that some tokens (commonly meme coins) will have a tax on transfer that depending at which point and how it is taken can cause the process to revert.

> While in most cases the amount transferred is the amount received from removing liquidity:

<pre>
  <code class='block language-js'>
  //UniswapV2Router
  //...
  (amountToken, amountETH) = removeLiquidity(                                     // <--- amountToken
    token,
    WETH,
    liquidity,
    amountTokenMin,
    amountETHMin,
    address(this),
    deadline
  );
    TransferHelper.safeTransfer(token, to, amountToken);                          // <--- amountToken
    IWETH(WETH).withdraw(amountETH);
    TransferHelper.safeTransferETH(to, amountETH);
  </code>
</pre>

> The variant gets its transfer amount by pulling the assets to the router and then calling `balanceOf(address(this))` on the token:

<pre>
  <code class='block language-js'>

// **** REMOVE LIQUIDITY (supporting fee-on-transfer tokens) ****
fuction removeLiquidityETHSupportingFeeOnTransferTokens(
  address token,
  uint liquidity,
  uint amountTokenMin,
  uint amountETHMin,
  address to,
  uint deadline
) public virtual override ensure(deadline) returns (uint amountETH) {
  (, amountETH) = removeLiquidity(
    token,
    WETH,
    liquidity,
    amountTokenMin,
    amountETHMin,
    address(this),
    deadline
  );
  TransferHelper.safeTransfer(token, to, IERC20(token).balanceOf(address(this))); // <-- address(this)
  IWETH(WETH).withdraw(amountETH);
  TransferHelper.safeTransferETH(to, amountETH);
}
  </code>
</pre>


See the trick?

This is a case where rather than use an amount we need to be verifiably pre entitled to, here it uses a balance check on self and passes along whatever it has.
This is how we can _loosen_ the stuck token.

We'll go over an implementation but it is essentially that simple.
However, the pressure of performing this correctly and the lack of protection for any blame or allogations that can be thrown around if you fail, should not be understated.

## Front running concerns
In terms of being front run when sending the transaction, it isn't as vulnerable as say, calling the `sweepETH` function on a Trident router.<br>
The `sweep` functions were added as a decentralised way to perform the above, but by design and without the gymnastics (a wonderful and trully decentralised solution).<br>
The problem being that if you call the function directly, any bot running simulations on the calldata will see that just naivly sending the same thing as you were about to,
without any investment beyond the gas fee, will result in an account increase and so blind front running becomes a major issue.
<blockquote class='note'>
The above can be somewhat mitigated by proxying the call through a relay that does a check on sender or hardcodes destination, as this can obfuscate the call and fail if naively simmed.
</blockquote>

Here it's a little more involved, quite importantly we are increasing our balance of some token but decreasing our balance of the native coin, which is harder for a blind sim to account for.

Additionally the rescue requires an investment in aquiring the liquidity that will be used to pull the tokens, and we need to perform the actions atomically from our own contract
which can block or obfuscate the call, so a naive simulation shouldn't pick up on it.<br>
As such I've only seen one of these rescues be front run in the same block as the rescue attempt (sub $100 thankfully), where as I have seen many sweeps be front run for not more than dust.

In most cases if you have time to see the tokens at the router then it's worth trying to rescue them, and you _should_ be safe to deploy or call without a private transaction.

## A basic rescue contract
The rescue contract from the case above was written by a friend in Solidity, and was practically identicle to the one I have written in Vyper below.<br>
The version I deploy these days (v2 rescues are still a thing) doesn't use any hardcoded args with even the router being passed, so it can be deployed
ahead of time and facilitate forked protocols. It has some mild gas savings by receiving a byte stream instead of abi encodings, and working directly on the
pools untill the final router call is needed.

> Worth noting that the following simple contract, in its implementation, has been used in around half a dozen rescues ranging in value (as that is the scary thing about those types of mistakes,
there is no cap on amount).

<pre>
  <code class='block language-py'>
# @author  : Maka
# @version : 0.3.3

interface IERC20:
  def balanceOf(account: address) -> uint256: view
  def approve(spender: address, amount: uint256) -> bool: nonpayable

interface SushiRouter:
  def removeLiquidityETHSupportingFeeOnTransferTokens(
      token: address,
      liquidity: uint256,
      amountTokenMin: uint256,
      amountETHMin: uint256,
      to:address,
      deadline: uint256
  ) -> uint256: nonpayable

  def addLiquidity(
      tokenA: address,
      tokenB: address,
      amountADesired: uint256,
      amountBDesired: uint256,
      amountAMin: uint256,
      amountBMin: uint256,
      to: address,
      deadline: uint256
  ) -> (uint256, uint256, uint256): nonpayable

  def swapExactTokensForTokens(
    amountIn: uint256,
    amountOutMin: uint256,
    path: DynArray[address, 2],
    to: address,
    deadline: uint256
  ): nonpayable

token  : constant(address) = # ...
weth   : constant(address) = # ...
router : constant(address) = # ...
slp    : constant(address) = # ...

guardian: public(address)

@external
@payable
def __init__():
  self.guardian = msg.sender
  # Wrap eth to weth
  raw_call(weth, method_id('deposit()'), value = msg.value, max_outsize=0)

  # Get a simple swap amount
  amountIn: uint256 = (IERC20(weth).balanceOf(self) / 2)

  path: DynArray[address, 2] = [weth, token]

  # Approve weth and swap for stranded token
  IERC20(weth).approve(router, IERC20(weth).balanceOf(self))
  SushiRouter(router).swapExactTokensForTokens(amountIn, 0, path, self, block.timestamp)

  # Approve the token we just swapped for, then add liquidity to the pool for eth and the stranded token
  IERC20(token).approve(router, IERC20(token).balanceOf(self))
  SushiRouter(router).addLiquidity(token, weth, IERC20(token).balanceOf(self), amountIn, 0, 0, self, block.timestamp)

  # Approve the lp then remove liquidity and the stranded token to the specified destination
  IERC20(slp).approve(router, IERC20(slp).balanceOf(self))
  SushiRouter(router).removeLiquidityETHSupportingFeeOnTransferTokens(
    token,
    IERC20(slp).balanceOf(self),
    0,
    0,
    self.guardian,
    block.timestamp
  )
  </code>
</pre>

In the next post we'll look at computing pool and init code hashes and how it relates to rescues, or rather an inability to rescue tokens, that has led to large sums being forever stuck at poorly deployed v2 routers all across the space.

Till next time.

<div class='handwritten'>1 love</div>
