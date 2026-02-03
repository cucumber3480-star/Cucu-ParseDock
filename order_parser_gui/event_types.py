from enum import Enum

class EventType(str, Enum):
    ARRIVAL = "Надходження"
    RESTORE = "Поновлення служби"
    TRANSFER = "Переведення"
    DEPARTURE = "Вибуття"
