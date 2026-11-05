import json
import unittest
from datetime import date, datetime, time, timedelta, timezone

from open_core.recurrence import (
    RecurrenceRule,
    occurrences,
    render_template,
    rule_from_dict,
    rule_to_dict,
)


class RecurrenceEngineTests(unittest.TestCase):
    def test_daily_occurrences_respect_limit_count_and_local_zone(self):
        rule = RecurrenceRule(
            start_date=date(2026, 11, 5),
            times=[time(19), time(8)],
            count=3,
            timezone="America/Sao_Paulo",
        )
        result = occurrences(rule, through=date(2026, 11, 20))
        self.assertEqual(len(result), 3)
        self.assertEqual([item.hour for item in result], [8, 19, 8])
        self.assertEqual(result[0].utcoffset(), -timedelta(hours=3))

    def test_weekly_uses_selected_weekdays(self):
        rule = RecurrenceRule(
            start_date=date(2026, 11, 2),
            frequency="weekly",
            weekdays=[0, 4],
            times=[time(18)],
            timezone="UTC",
        )
        result = occurrences(rule, through=date(2026, 11, 13))
        self.assertEqual([item.date() for item in result], [
            date(2026, 11, 2), date(2026, 11, 6), date(2026, 11, 9), date(2026, 11, 13)
        ])

    def test_monthly_last_day_handles_short_and_leap_months(self):
        rule = RecurrenceRule(
            start_date=date(2024, 1, 31),
            frequency="monthly",
            last_day=True,
            times=[time(19)],
            timezone="UTC",
        )
        result = occurrences(rule, through=date(2024, 3, 31))
        self.assertEqual([item.date() for item in result], [
            date(2024, 1, 31), date(2024, 2, 29), date(2024, 3, 31)
        ])

    def test_exclusions_apply_to_date_and_specific_occurrence(self):
        omitted = datetime(2026, 11, 6, 19, tzinfo=timezone.utc)
        rule = RecurrenceRule(
            start_date=date(2026, 11, 5),
            frequency="daily",
            times=[time(19)],
            excluded_dates={date(2026, 11, 7)},
            excluded_datetimes={omitted},
            timezone="UTC",
        )
        result = occurrences(rule, through=date(2026, 11, 8))
        self.assertEqual([item.date() for item in result], [date(2026, 11, 5), date(2026, 11, 8)])

    def test_rule_json_round_trip_keeps_exceptions_and_timezone(self):
        original = RecurrenceRule(
            start_date=date(2026, 11, 5),
            frequency="interval",
            interval_days=3,
            times=[time(19, 30)],
            excluded_dates={date(2026, 11, 8)},
            excluded_datetimes={datetime(2026, 11, 11, 19, 30, tzinfo=timezone.utc)},
            timezone="UTC",
        )
        self.assertEqual(rule_from_dict(rule_to_dict(original)), original)
        self.assertEqual(rule_from_dict(json.dumps(rule_to_dict(original))), original)

    def test_template_localizes_values_and_preserves_unknown_tokens(self):
        when = datetime(2026, 11, 5, 19, 5)
        self.assertEqual(render_template("LIVE {tema} · {dia_semana} {data} {desconhecido}", when, "Ciência"),
                         "LIVE Ciência · quinta-feira 05/11/2026 {desconhecido}")

    def test_invalid_frequency_interval_and_empty_times_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Frequência inválida"):
            occurrences(RecurrenceRule(date(2026, 11, 5), frequency="unknown"), through=date(2026, 11, 6))
        with self.assertRaisesRegex(ValueError, "intervalo"):
            occurrences(RecurrenceRule(date(2026, 11, 5), frequency="interval", interval_days=0), through=date(2026, 11, 6))
        with self.assertRaisesRegex(ValueError, "horário"):
            occurrences(RecurrenceRule(date(2026, 11, 5), times=[]), through=date(2026, 11, 6))

    def test_template_rejects_empty_or_overlong_titles(self):
        when = datetime(2026, 11, 5, 19, 5)
        with self.assertRaisesRegex(ValueError, "não pode ficar vazio"):
            render_template("  ", when)
        with self.assertRaisesRegex(ValueError, "limite do YouTube"):
            render_template("x" * 101, when)


if __name__ == "__main__":
    unittest.main()
