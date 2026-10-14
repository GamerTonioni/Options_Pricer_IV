import unittest

from options_pricer import black_scholes, implied_volatility, calculate_greeks


class TestOptionsPricer(unittest.TestCase):

    def test_call_price_is_positive(self):
        price = black_scholes(
            spot=100,
            strike=100,
            time_to_expiry=0.25,
            risk_free_rate=0.04,
            volatility=0.25,
            option_type="call",
        )
        self.assertGreater(price, 0)

    def test_put_price_is_positive(self):
        price = black_scholes(
            spot=100,
            strike=100,
            time_to_expiry=0.25,
            risk_free_rate=0.04,
            volatility=0.25,
            option_type="put",
        )
        self.assertGreater(price, 0)

    def test_implied_volatility_recovers_input(self):
        original_vol = 0.25

        market_price = black_scholes(
            spot=100,
            strike=100,
            time_to_expiry=0.25,
            risk_free_rate=0.04,
            volatility=original_vol,
            option_type="call",
        )

        recovered_vol = implied_volatility(
            market_price=market_price,
            spot=100,
            strike=100,
            time_to_expiry=0.25,
            risk_free_rate=0.04,
            option_type="call",
        )

        self.assertAlmostEqual(
            recovered_vol, original_vol, places=4
        )

    def test_invalid_option_type_raises_error(self):
        with self.assertRaises(ValueError):
            black_scholes(
                spot=100,
                strike=100,
                time_to_expiry=0.25,
                risk_free_rate=0.04,
                volatility=0.25,
                option_type="invalid",
            )
    
    def test_call_delta_is_between_zero_and_one(self):
        greeks = calculate_greeks(
            100, 100, 0.25, 0.04, 0.25, "call"
        )
        self.assertGreater(greeks["delta"], 0)
        self.assertLess(greeks["delta"], 1)

    def test_gamma_is_positive(self):
        greeks = calculate_greeks(
            100, 100, 0.25, 0.04, 0.25, "call"
        )
        self.assertGreater(greeks["gamma"], 0)
    

    def test_vega_is_positive(self):
        greeks = calculate_greeks(
            100, 100, 0.25, 0.04, 0.25, "call"
        )
        self.assertGreater(greeks["vega"], 0)

    def test_call_theta_is_negative(self):
        greeks = calculate_greeks(
            100, 100, 0.25, 0.04, 0.25, "call"
        )
        self.assertLess(greeks["theta"], 0)

    def test_call_rho_is_positive(self):
        greeks = calculate_greeks(
            100, 100, 0.25, 0.04, 0.25, "call"
        )
        self.assertGreater(greeks["rho"], 0)
    
    
    def test_implied_volatility_rejects_negative_market_price(self):
        with self.assertRaisesRegex(
            ValueError, "Market price must be positive"
        ):
            implied_volatility(
                market_price=-1,
                spot=100,
                strike=100,
                time_to_expiry=0.25,
                risk_free_rate=0.04,
            )

    def test_implied_volatility_rejects_impossible_call_price(self):
        with self.assertRaises(ValueError):
            implied_volatility(
                market_price=150,
                spot=100,
                strike=100,
                time_to_expiry=0.25,
                risk_free_rate=0.04,
                option_type="call",
            )

    def test_implied_volatility_rejects_invalid_option_type(self):
        with self.assertRaisesRegex(ValueError, "Option type"):
            implied_volatility(
                market_price=5,
                spot=100,
                strike=100,
                time_to_expiry=0.25,
                risk_free_rate=0.04,
                option_type="invalid",
            )

    def test_implied_volatility_rejects_zero_time_to_expiry(self):
        with self.assertRaises(ValueError):
            implied_volatility(
                market_price=5,
                spot=100,
                strike=100,
                time_to_expiry=0,
                risk_free_rate=0.04,
            )




if __name__ == "__main__":
    unittest.main()
