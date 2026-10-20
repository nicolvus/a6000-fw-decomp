import unittest
from decimal import Decimal

from budget import Guard, actual_cost


class BudgetTests(unittest.TestCase):
    def test_rejects_full_context_reservation_over_dollar(self):
        with self.assertRaises(ValueError):
            Guard(Decimal('0.68')).reserve()

    def test_stops_at_preventive_threshold(self):
        with self.assertRaises(ValueError):
            Guard(Decimal('0.85')).reserve()

    def test_reserves_before_response_and_stops_if_unknown(self):
        guard = Guard()
        guard.reserve()
        with self.assertRaises(ValueError):
            guard.reserve()

    def test_cache_and_reasoning_are_not_double_counted(self):
        usage = {'prompt_tokens': 1000, 'prompt_cache_hit_tokens': 600,
                 'prompt_cache_miss_tokens': 400, 'completion_tokens': 200,
                 'completion_tokens_details': {'reasoning_tokens': 150}}
        self.assertEqual(actual_cost(usage, False), Decimal('0.0001818'))
        self.assertEqual(actual_cost(usage, True), Decimal('0.0003636'))

    def test_missing_usage_fails_closed(self):
        with self.assertRaises((ValueError, KeyError)):
            actual_cost({'prompt_tokens': 2}, False)

    def test_pro_model_rejected(self):
        guard = Guard()
        guard.reserve()
        with self.assertRaises(ValueError):
            guard.settle('deepseek-v4-pro', {}, False)


if __name__ == '__main__':
    unittest.main()
