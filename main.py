import math

# Constants for Uniswap V3
Q96 = 2**96  # Uniswap uses Q64.96 fixed-point format

# Min and max tick values in Uniswap V3
MIN_TICK = -887272
MAX_TICK = 887272

# Function to convert price to tick
def price_to_tick(p):
    return math.floor(math.log(p, 1.0001))

# Function to convert price to sqrt price
def price_to_sqrtP(p):
    return int(math.sqrt(p) * Q96)

# Function to convert tick to sqrt price
def tick_to_sqrtP(tick):
    return int((math.pow(1.0001, tick) ** 0.5) * Q96)

curr_tick = price_to_tick(40_000_000)

sqrtP_low = tick_to_sqrtP(MIN_TICK)
sqrtP_cur = tick_to_sqrtP(curr_tick)
sqrtP_upp = tick_to_sqrtP(MAX_TICK)

# Liquidity formulas
def calc_liquidity0(amount, pa, pb):
    if pa > pb:
        pa, pb = pb, pa
    return (amount * (pa * pb) / Q96) / (pb - pa)

def calc_liquidity1(amount, pa, pb):
    if pa > pb:
        pa, pb = pb, pa
    return amount * Q96 / (pb - pa)

# Inputs: Amounts of tokens
eth = 10**18
amount0 = 2 * eth  # 2 ETH
amount1 = 80_000_000 * eth  # 80,000,000 tokens

# Compute liquidity from ETH and token amounts
L0 = calc_liquidity0(amount0, sqrtP_cur, sqrtP_upp)
L1 = calc_liquidity1(amount1, sqrtP_cur, sqrtP_low)

# Pick the minimum liquidity
L = int(min(L0, L1))

print(f"Liquidity Provided (L): {L}")

def calc_amount0(liq, pa, pb):
    if pa > pb:
        pa, pb = pb, pa
    return int(liq * Q96 * (pb - pa) / pa / pb)


def calc_amount1(liq, pa, pb):
    if pa > pb:
        pa, pb = pb, pa
    return int(liq * (pb - pa) / Q96)

amount0 = calc_amount0(L, sqrtP_upp, sqrtP_cur)
amount1 = calc_amount1(L, sqrtP_low, sqrtP_cur)
print(f"amount0: {amount0}")
print(f"amount1: {amount1}")

# Selling Token1 (i.e. TKN) For Token0

# If we put in 10,000 tokens
OneForZero_amount_in = 10_000 * eth
OneForZero_price_diff = (OneForZero_amount_in * Q96) // L
OneForZero_price_next = sqrtP_cur + OneForZero_price_diff
print("New price:", (OneForZero_price_next / Q96) ** 2)
print("New sqrtP:", OneForZero_price_next)
print("New tick:", price_to_tick((OneForZero_price_next / Q96) ** 2))

OneForZero_amount_in = calc_amount1(L, OneForZero_price_next, sqrtP_cur)
amount_out = calc_amount0(L, OneForZero_price_next, sqrtP_cur)

print("TKN in:", OneForZero_amount_in / eth)
print("ETH out:", amount_out / eth)

# Selling Token0 (i.e. ETH) For Token1

ZeroForOne_amount_in = 0.001 * eth

print(f"\nSelling {ZeroForOne_amount_in/eth} ETH")

ZeroForOne_price_next = int((L * Q96 * sqrtP_cur) // (L * Q96 + ZeroForOne_amount_in * sqrtP_cur))

print("New price:", (ZeroForOne_price_next / Q96) ** 2)
print("New sqrtP:", ZeroForOne_price_next)
print("New tick:", price_to_tick((ZeroForOne_price_next / Q96) ** 2))

ZeroForOne_amount_in = calc_amount0(L, ZeroForOne_price_next, sqrtP_cur)
amount_out = calc_amount1(L, ZeroForOne_price_next, sqrtP_cur)

print("ETH in:", ZeroForOne_amount_in / eth)
print("TKN out:", amount_out / eth)
