import math

def price_to_tick(p):
    return math.floor(math.log(p, 1.0001))

price_to_tick(5000)
# > 85176

q96 = 2**96
def price_to_sqrtp(p):
    return int(math.sqrt(p) * q96)

price_to_sqrtp(40000000)
# print(price_to_sqrtp(40000000))
# > 5602277097478614198912276234240

def sqrt_price_to_price(s):
    return math.pow(s / q96, 2)
eth = 1 * 10 ** 18
print(int(40000000 - sqrt_price_to_price(501066558273621464884319660560427)))
