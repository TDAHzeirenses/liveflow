# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import calendar
import json
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


@dataclass
class RecurrenceRule:
    start_date: date
    times: list[time] = field(default_factory=lambda: [time(19, 0)])
    frequency: str = "daily"  # once, daily, weekly, monthly, interval
    end_date: date | None = None
    count: int | None = None
    interval_days: int = 1
    weekdays: list[int] = field(default_factory=list)  # Monday=0
    month_day: int = 1
    last_day: bool = False
    excluded_dates: set[date] = field(default_factory=set)
    timezone: str = "America/Sao_Paulo"
    excluded_datetimes: set[datetime] = field(default_factory=set)


def rule_to_dict(rule: RecurrenceRule) -> dict:
    return {
        "start_date": rule.start_date.isoformat(),
        "times": [value.isoformat(timespec="minutes") for value in rule.times],
        "frequency": rule.frequency,
        "end_date": rule.end_date.isoformat() if rule.end_date else None,
        "count": rule.count,
        "interval_days": rule.interval_days,
        "weekdays": list(rule.weekdays),
        "month_day": rule.month_day,
        "last_day": rule.last_day,
        "excluded_dates": sorted(value.isoformat() for value in rule.excluded_dates),
        "excluded_datetimes": sorted(value.isoformat() for value in rule.excluded_datetimes),
        "timezone": rule.timezone,
    }


def rule_from_dict(value: dict | str) -> RecurrenceRule:
    data = json.loads(value) if isinstance(value, str) else value
    return RecurrenceRule(
        date.fromisoformat(data["start_date"]),
        [time.fromisoformat(item) for item in data["times"]],
        data["frequency"],
        date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
        data.get("count"), data.get("interval_days", 1), data.get("weekdays", []),
        data.get("month_day", 1), data.get("last_day", False),
        {date.fromisoformat(item) for item in data.get("excluded_dates", [])},
        data.get("timezone", "America/Sao_Paulo"),
        {datetime.fromisoformat(item) for item in data.get("excluded_datetimes", [])},
    )


def _monthly_date(year: int, month: int, day: int, last_day: bool) -> date:
    limit = calendar.monthrange(year, month)[1]
    return date(year, month, limit if last_day else min(day, limit))


def occurrences(rule: RecurrenceRule, *, through: date | None = None,
                max_occurrences: int | None = None) -> list[datetime]:
    """Generate local aware datetimes, sorted and bounded by end_date/through/count."""
    if not rule.times:
        raise ValueError("Adicione pelo menos um horário.")
    if max_occurrences is not None and max_occurrences < 1:
        raise ValueError("O limite de ocorrências deve ser positivo.")
    if rule.frequency not in {"once", "daily", "weekly", "monthly", "interval"}:
        raise ValueError("Frequência inválida.")
    if rule.frequency == "interval" and rule.interval_days < 1:
        raise ValueError("O intervalo deve ser de pelo menos um dia.")
    if rule.count is not None and rule.count < 1:
        raise ValueError("A quantidade deve ser positiva.")
    try:
        zone = ZoneInfo(rule.timezone)
    except Exception as exc:
        # Windows does not ship an IANA database. São Paulo has observed fixed
        # UTC-03:00 since 2019; keep the default usable offline while the
        # optional tzdata package supplies all other IANA rules.
        if rule.timezone == "America/Sao_Paulo":
            zone = timezone(timedelta(hours=-3), "America/Sao_Paulo")
        elif rule.timezone in {"UTC", "Etc/UTC"}:
            zone = timezone.utc
        else:
            raise ValueError("Fuso horário indisponível. Instale o pacote tzdata.") from exc
    limit = min([d for d in (rule.end_date, through) if d is not None], default=None)
    if limit and limit < rule.start_date:
        return []
    max_day = limit or (rule.start_date + timedelta(days=366 * 5))
    days: list[date] = []
    if rule.frequency == "once":
        days = [rule.start_date]
    elif rule.frequency == "monthly":
        cursor = rule.start_date.replace(day=1)
        while cursor <= max_day:
            candidate = _monthly_date(cursor.year, cursor.month, rule.month_day, rule.last_day)
            if candidate >= rule.start_date:
                days.append(candidate)
            cursor = date(cursor.year + (cursor.month == 12), 1 if cursor.month == 12 else cursor.month + 1, 1)
    else:
        cursor = rule.start_date
        while cursor <= max_day:
            delta = (cursor - rule.start_date).days
            if rule.frequency == "daily" or (rule.frequency == "interval" and delta % rule.interval_days == 0):
                days.append(cursor)
            elif rule.frequency == "weekly" and cursor.weekday() in (rule.weekdays or [rule.start_date.weekday()]):
                days.append(cursor)
            cursor += timedelta(days=1)
    results: list[datetime] = []
    for day in days:
        if day in rule.excluded_dates:
            continue
        for at in sorted(rule.times):
            occurrence = datetime.combine(day, at, tzinfo=zone)
            if occurrence not in rule.excluded_datetimes:
                results.append(occurrence)
            if max_occurrences is not None and len(results) >= max_occurrences:
                return results
            if rule.count and len(results) >= rule.count:
                return results
    return results


def render_template(template: str, when: datetime, theme: str = "") -> str:
    local = when
    names = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    months = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    values = {
        "data": local.strftime("%d/%m/%Y"), "data_curta": local.strftime("%d/%m"),
        "dia": f"{local.day:02d}", "dia_semana": names[local.weekday()],
        "mes": f"{local.month:02d}", "mes_nome": months[local.month - 1],
        "ano": str(local.year), "hora": local.strftime("%H:%M"), "tema": theme,
    }
    import re
    rendered = re.sub(r"\{([a-z_]+)\}", lambda m: values.get(m.group(1), m.group(0)), template)
    if len(rendered) > 100:
        raise ValueError(f"O título ficou com {len(rendered)} caracteres (limite do YouTube: 100).")
    if not rendered.strip():
        raise ValueError("O título não pode ficar vazio.")
    return rendered
