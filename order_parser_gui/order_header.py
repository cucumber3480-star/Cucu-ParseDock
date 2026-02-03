import re
from datetime import date

ORDER_NO_RE = re.compile(r"№\s*([0-9A-ZА-ЯІЇЄҐ\-]+)")

# very soft: tries to find the order's own date in formats like 03.02.2026 or "31" січня 2026 року
UA_MONTHS = {
    "січня": 1, "лютого": 2, "березня": 3, "квітня": 4, "травня": 5, "червня": 6,
    "липня": 7, "серпня": 8, "вересня": 9, "жовтня": 10, "листопада": 11, "грудня": 12,
}

ORDER_DATE_DMY_RE = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")
ORDER_DATE_UA_RE = re.compile(
    r'\"?(\d{1,2})\"?\s+'
    r'(січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)\s+'
    r'(\d{4})\s+року',
    re.IGNORECASE
)

def extract_order_number(lines: list[str]) -> str:
    for l in lines[:80]:
        m = ORDER_NO_RE.search(l)
        if m:
            return m.group(1)
    return ""

def extract_order_date(lines: list[str]) -> date:
    for l in lines[:120]:
        m = ORDER_DATE_DMY_RE.search(l)
        if m:
            d, mo, y = map(int, m.groups())
            try:
                return date(y, mo, d)
            except ValueError:
                pass
        m2 = ORDER_DATE_UA_RE.search(l.lower())
        if m2:
            d = int(m2.group(1))
            mo = UA_MONTHS.get(m2.group(2), 0)
            y = int(m2.group(3))
            if mo:
                try:
                    return date(y, mo, d)
                except ValueError:
                    pass
    return date.today()
