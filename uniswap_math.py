import math

# Constants
Q96 = 2**96  # Q64.96 fixed-point format
ETH_UNIT = 10**18
MIN_TICK = -887272
MAX_TICK = 887272

def price_to_tick(price):
    """Converts a price to a tick value."""
    return math.floor(math.log(price, 1.0001))

def price_to_sqrtP(price):
    """Converts a price to a square root price representation in Q64.96 format."""
    return int(math.sqrt(price) * Q96)

def tick_to_sqrtP(tick):
    """Converts a tick value to a square root price."""
    return int((math.pow(1.0001, tick) ** 0.5) * Q96)

def calc_liquidity_0(amount_0, sqrtP_lower, sqrtP_upper):
    """Calculates liquidity from the given amount of token 0."""
    if sqrtP_lower > sqrtP_upper:
        sqrtP_lower, sqrtP_upper = sqrtP_upper, sqrtP_lower
    return (amount_0 * (sqrtP_lower * sqrtP_upper) / Q96) / (sqrtP_upper - sqrtP_lower)

def calc_liquidity_1(amount_1, sqrtP_lower, sqrtP_upper):
    """Calculates liquidity from the given amount of token 1."""
    if sqrtP_lower > sqrtP_upper:
        sqrtP_lower, sqrtP_upper = sqrtP_upper, sqrtP_lower
    return amount_1 * Q96 / (sqrtP_upper - sqrtP_lower)

def calc_liquidity(amount_0, amount_1, sqrtP_current, sqrtP_lower, sqrtP_upper):
    """Calculates the liquidity from the given amounts of tokens."""
    liquidity_0 = calc_liquidity_0(amount_0, sqrtP_current, sqrtP_upper)
    liquidity_1 = calc_liquidity_1(amount_1, sqrtP_current, sqrtP_lower)
    return int(min(liquidity_0, liquidity_1))

def calc_amount_0(liquidity, sqrtP_lower, sqrtP_upper):
    """Calculates the amount of token 0 given liquidity and price bounds."""
    if sqrtP_lower > sqrtP_upper:
        sqrtP_lower, sqrtP_upper = sqrtP_upper, sqrtP_lower
    return int(liquidity * Q96 * (sqrtP_upper - sqrtP_lower) / sqrtP_lower / sqrtP_upper)

def calc_amount_1(liquidity, sqrtP_lower, sqrtP_upper):
    """Calculates the amount of token 1 given liquidity and price bounds."""
    if sqrtP_lower > sqrtP_upper:
        sqrtP_lower, sqrtP_upper = sqrtP_upper, sqrtP_lower
    return int(liquidity * (sqrtP_upper - sqrtP_lower) / Q96)

def quote_exact_input(amount_in, liquidity, current_sqrtP, zero_for_one):
    """
    Executes an exact input swap.
    - zero_for_one = True: Swap token0 for token1
    - zero_for_one = False: Swap token1 for token0
    """
    if zero_for_one:
        new_sqrtP = int((liquidity * Q96 * current_sqrtP) // (liquidity * Q96 + amount_in * current_sqrtP))
        amount_out = calc_amount_1(liquidity, new_sqrtP, current_sqrtP)
    else:
        price_difference = (amount_in * Q96) // liquidity
        new_sqrtP = int(current_sqrtP + price_difference)
        amount_out = calc_amount_0(liquidity, new_sqrtP, current_sqrtP)

    new_price = (new_sqrtP / Q96) ** 2
    new_tick = price_to_tick(new_price)

    return new_sqrtP, new_price, new_tick, amount_out

def quote_exact_output(amount_out, liquidity, current_sqrtP, zero_for_one):
    """
    Executes an exact output swap.
    - zero_for_one = True: Swap token0 for token1
    - zero_for_one = False: Swap token1 for token0
    """
    if zero_for_one:
        price_difference = (amount_out * Q96) // liquidity
        new_sqrtP = int(current_sqrtP + price_difference)
        amount_in = calc_amount_0(liquidity, new_sqrtP, current_sqrtP)
    else:
        new_sqrtP = int((liquidity * Q96 * current_sqrtP) // (liquidity * Q96 + amount_out * current_sqrtP))
        amount_in = calc_amount_1(liquidity, new_sqrtP, current_sqrtP)

    new_price = (new_sqrtP / Q96) ** 2
    new_tick = price_to_tick(new_price)

    return new_sqrtP, new_price, new_tick, amount_in

# Set up initial values
current_tick = price_to_tick(40_000_000)
sqrtP_lower = tick_to_sqrtP(MIN_TICK)
sqrtP_current = tick_to_sqrtP(current_tick)
sqrtP_upper = tick_to_sqrtP(MAX_TICK)

# Inputs: Amounts of tokens
amount_0 = 2 * ETH_UNIT  # 2 ETH
amount_1 = 80_000_000 * ETH_UNIT  # 80,000,000 tokens

# Compute liquidity from ETH and token amounts
liquidity = calc_liquidity(amount_0, amount_1, sqrtP_current, sqrtP_lower, sqrtP_upper)
print(f"Liquidity Provided (L): {liquidity}")

print(f"amount0: {calc_amount_0(liquidity, sqrtP_upper, sqrtP_current)}")
print(f"amount1: {calc_amount_1(liquidity, sqrtP_lower, sqrtP_current)}")

# Swap Exact Input

amount_in_1 = 10_000 * ETH_UNIT
new_sqrtP, new_price, new_tick, amount_out_0 = quote_exact_input(amount_in_1, liquidity, sqrtP_current, False)
print(f"""Swap Exact Input:
    {amount_in_1 / ETH_UNIT} TKN -> {amount_out_0 / ETH_UNIT} ETH
    New sqrtP: {new_sqrtP}
    New Price: {new_price}
    New Tick: {new_tick}
    Amount In: {amount_in_1}
    Amount Out: {amount_out_0}""")

print("-------------------")
sqrtP_current_new = tick_to_sqrtP(new_tick)
new_sqrtP, new_price, new_tick_2, amount_out_0 = quote_exact_input(amount_in_1, liquidity, sqrtP_current_new, False)
print(f"""Swap Exact Input:
    {amount_in_1 / ETH_UNIT} TKN -> {amount_out_0 / ETH_UNIT} ETH
    New sqrtP: {new_sqrtP}
    New Price: {new_price}
    New Tick: {new_tick_2}
    Amount In: {amount_in_1}
    Amount Out: {amount_out_0}""")
print("-------------------")

amount_in_0 = 0.001 * ETH_UNIT
new_sqrtP, new_price, new_tick, amount_out_1 = quote_exact_input(amount_in_0, liquidity, sqrtP_current, True)
print(f"""Swap Exact Input:
    {amount_in_0 / ETH_UNIT} ETH -> {amount_out_1 / ETH_UNIT} TKN
    New sqrtP: {new_sqrtP}
    New Price: {new_price}
    New Tick: {new_tick}
    Amount In: {amount_in_0}
    Amount Out: {amount_out_1}""")

# # Swap Exact Output
amount_out_1 = 10_000 * ETH_UNIT
new_sqrtP, new_price, new_tick, amount_in_0 = quote_exact_output(amount_out_1, liquidity, sqrtP_current, True)
print(f"""Swap Exact Output:
    {amount_out_1 / ETH_UNIT} TKN <- {amount_in_0 / ETH_UNIT} ETH
    New sqrtP: {new_sqrtP}
    New Price: {new_price}
    New Tick: {new_tick}
    Amount In: {amount_in_0}
    Amount Out: {amount_out_1}""")

amount_out_0 = 0.001 * ETH_UNIT
new_sqrtP, new_price, new_tick, amount_in_1 = quote_exact_output(amount_out_0, liquidity, sqrtP_current, False)
print(f"""Swap Exact Output:
    {amount_out_0 / ETH_UNIT} ETH <- {amount_in_1 / ETH_UNIT} TKN
    New sqrtP: {new_sqrtP}
    New Price: {new_price}
    New Tick: {new_tick}
    Amount In: {amount_in_1}
    Amount Out: {amount_out_0}""")
