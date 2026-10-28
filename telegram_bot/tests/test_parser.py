import unittest
from datetime import date
from decimal import Decimal

from telegram_bot.parser import DEPOSIT, EXPENSE, ParseError, parse_message

TODAY = date(2026, 10, 27)


class ParserTests(unittest.TestCase):
    def test_simple_expense_infers_category(self):
        p = parse_message("350 tacos", TODAY)
        self.assertEqual((p.type, p.amount, p.note, p.category, p.date),
                         (EXPENSE, Decimal("350.00"), "tacos", "food", TODAY))

    def test_unknown_words_fall_back_to_other(self):
        self.assertEqual(parse_message("50 cosas raras", TODAY).category, "other")

    def test_deposit_has_no_category(self):
        p = parse_message("+15,000 nómina", TODAY)
        self.assertEqual((p.type, p.amount, p.category), (DEPOSIT, Decimal("15000.00"), None))

    def test_currency_symbol_and_decimals(self):
        self.assertEqual(parse_message("$89.5 uber", TODAY).amount, Decimal("89.50"))

    def test_explicit_tag_overrides_inference(self):
        self.assertEqual(parse_message("350 tacos #ocio", TODAY).category, "leisure")

    def test_island_hint_and_relative_date(self):
        p = parse_message("1200 renta @mercado_pago ayer", TODAY)
        self.assertEqual((p.island_hint, p.date, p.note), ("mercado pago", date(2026, 10, 26), "renta"))

    def test_day_month_date(self):
        self.assertEqual(parse_message("80 cine 25/10", TODAY).date, date(2026, 10, 25))

    def test_day_month_in_future_means_previous_year(self):
        self.assertEqual(parse_message("80 regalo 25/12", TODAY).date, date(2025, 12, 25))

    def test_explicit_future_date_rejected(self):
        with self.assertRaises(ParseError):
            parse_message("80 cine 01/01/2030", TODAY)

    def test_invalid_inputs(self):
        for bad in ["", "tacos 350", "0 nada", "350 x #inventada", "350 x #comida #ocio"]:
            with self.subTest(bad=bad), self.assertRaises(ParseError):
                parse_message(bad, TODAY)

    def test_explicit_minus_is_an_expense(self):
        p = parse_message("-5 chicles", TODAY)
        self.assertEqual((p.type, p.amount), (EXPENSE, Decimal("5.00")))

    def test_accents_do_not_matter(self):
        self.assertEqual(parse_message("200 Café", TODAY).category, "food")


if __name__ == "__main__":
    unittest.main()
