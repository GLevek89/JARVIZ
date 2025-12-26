from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import re

import requests
from bs4 import BeautifulSoup
from dateutil import tz


HELLTIDES_SCHEDULE_URL = "https://helltides.com/schedule"


@dataclass
class D4Event:
    kind: str               # "helltide" | "worldboss" | "legion" | "event"
    starts_at: datetime     # timezone-aware
    label: str = ""


def _now_local():
    return datetime.now(tz=tz.tzlocal())


def _parse_time_local(s: str) -> Optional[datetime]:
    try:
        dt_naive = datetime.strptime(s.strip(), "%m/%d/%Y %I:%M %p")
        return dt_naive.replace(tzinfo=tz.tzlocal())
    except Exception:
        return None


def fetch_events(limit: int = 30, timeout: float = 10.0) -> List[D4Event]:
    r = requests.get(
        HELLTIDES_SCHEDULE_URL,
        timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    lines = [
        ln.strip()
        for ln in text.splitlines()
        if re.search(r"\d{1,2}/\d{1,2}/\d{4}", ln)
    ][: max(limit, 1)]

    events: List[D4Event] = []
    for ln in lines:
        m = re.match(
            r"^(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s+[AP]M)(.*)$",
            ln,
        )
        if not m:
            continue

        dt_part = m.group(1).strip()
        tail = m.group(2).strip()

        dt_local = _parse_time_local(dt_part)
        if not dt_local:
            continue

        boss_names = {"Avarice", "Ashava", "Wandering Death", "Azmodan"}
        if tail in boss_names:
            kind = "worldboss"
            label = tail
        else:
            kind = "event"
            label = tail

        events.append(D4Event(kind=kind, starts_at=dt_local, label=label))

    now = _now_local()
    events = [e for e in events if e.starts_at > now]
    events.sort(key=lambda e: e.starts_at)
    return events


def next_by_kind(events: List[D4Event]) -> Dict[str, Optional[D4Event]]:
    next_worldboss = next((e for e in events if e.kind == "worldboss"), None)
    generics = [e for e in events if e.kind == "event"]

    next_helltide = generics[0] if len(generics) >= 1 else None
    next_legion = generics[1] if len(generics) >= 2 else None

    return {
        "helltide": next_helltide,
        "legion": next_legion,
        "worldboss": next_worldboss,
    }
