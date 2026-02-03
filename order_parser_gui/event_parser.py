import re
from datetime import date

# We keep it permissive: rank can appear near the start, but not necessarily at char 0.
RANK_RE = re.compile(
    r"\b(солдат(?:а)?|молодш(ого)?\s+сержант(?:а)?|старш(ого)?\s+сержант(?:а)?|"
    r"сержант(?:а)?|лейтенант(?:а)?|старш(ого)?\s+лейтенант(?:а)?|капітан(?:а)?|майор(?:а)?)\b",
    re.IGNORECASE
)

MONTHS = {
    "січня": 1, "лютого": 2, "березня": 3, "квітня": 4, "травня": 5, "червня": 6,
    "липня": 7, "серпня": 8, "вересня": 9, "жовтня": 10, "листопада": 11, "грудня": 12,
}

# event dates in orders are usually: з "29" січня 2026 року
EVENT_DATE_UA_RE = re.compile(
    r'з\s+\"?(\d{1,2})\"?\s+'
    r'(січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)\s+'
    r'(\d{4})\s+року',
    re.IGNORECASE
)

# sometimes: з 29.01.2026
EVENT_DATE_DMY_RE = re.compile(r"з\s+(\d{1,2})\.(\d{1,2})\.(\d{4})\b", re.IGNORECASE)

# Category detection is ORDERED (priority matters!)
CATEGORY_RULES = [
    ("szch", [
        "сзч", "самовільно", "самовiльно", "зник", "зниклий", "безвісти", "розшук"
    ]),
    ("departure", [
        "виключити", "увільнити", "увiльнити", "звільнити", "звiльнити", "вибув", "зняти з усіх видів забезпечення"
    ]),
    ("medical", [
        "на лікування", "на лiкування", "виписка", "госпітал", "госпiтал", "влк", "лікарсько", "медичн"
    ]),
    ("business_trip", [
        "відрядити", "вiдрядити", "у відрядження", "у вiдрядження", "відрядженн"
    ]),
    ("arrival", [
        "зарахувати", "призначити", "прибув", "прийняв", "приступив", "зарахован"
    ]),
]

def detect_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in t:
                return cat
    return "other"

def extract_event_date(text: str, fallback: date) -> date:
    t = text.lower()
    m = EVENT_DATE_UA_RE.search(t)
    if m:
        d = int(m.group(1))
        mo = MONTHS.get(m.group(2), 0)
        y = int(m.group(3))
        if mo:
            try:
                return date(y, mo, d)
            except ValueError:
                return fallback
    m2 = EVENT_DATE_DMY_RE.search(t)
    if m2:
        d, mo, y = map(int, m2.groups())
        try:
            return date(y, mo, d)
        except ValueError:
            return fallback
    return fallback

def parse_paragraph_as_event(paragraph: str, order_number: str, order_date: date) -> dict | None:
    if not paragraph:
        return None
    if not RANK_RE.search(paragraph):
        return None

    ev_date = extract_event_date(paragraph, order_date)
    category = detect_category(paragraph)

    return {
        "date": ev_date.strftime("%d.%m.%Y"),
        "order": order_number or "—",
        "category": category,
        "raw": paragraph,
        "snippet": paragraph if len(paragraph) <= 220 else paragraph[:220] + "…",
    }
