import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

def bs_price(S, K, T, r, vol, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * vol**2) * T) / (vol * np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def equation(sigma, market_price, S, K, T, r, option_type='call'):
    return bs_price(S, K, T, r, sigma, option_type) - market_price

def implied_vol(market_price, S, K, T, r, option_type='call'):
    try:
        return brentq(equation, 1e-19, 5, args=(market_price, S, K, T, r, option_type))
    except (ValueError, RuntimeError):
        return np.nan


def test_known_textbook_price():
    # Hull's textbook example: S=42, K=40, T=0.5, r=0.10, vol=0.20 -> call ≈ 4.76
    price = bs_price(S=42, K=40, T=0.5, r=0.10, vol=0.20, option_type='call')
    assert abs(price - 4.76) < 0.01

def test_put_call_parity():
    S, K, T, r, vol = 100, 100, 0.5, 0.05, 0.2
    call = bs_price(S, K, T, r, vol, 'call')
    put = bs_price(S, K, T, r, vol, 'put')
    lhs = call - put
    rhs = S - K * np.exp(-r * T)
    assert abs(lhs - rhs) < 1e-8

def test_iv_solver_recovers_input_vol():
    S, K, T, r, true_vol = 100, 105, 30/365, 0.05, 0.22
    price = bs_price(S, K, T, r, true_vol, 'call')
    recovered = implied_vol(price, S, K, T, r, 'call')
    assert abs(recovered - true_vol) < 1e-4

def test_deep_itm_call_converges_to_intrinsic():
    # Deep ITM: price should approach S - K*exp(-rT) as vol shrinks
    price = bs_price(S=200, K=50, T=30/365, r=0.05, vol=0.15, option_type='call')
    intrinsic = 200 - 50 * np.exp(-0.05 * 30/365)
    assert abs(price - intrinsic) < 1.0
