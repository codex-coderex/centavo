from decimal import Decimal, ROUND_HALF_UP


def to_minor_units(amount, decimal_places: int = 2) -> int:
    value = Decimal(str(amount))
    multiplier = Decimal(10) ** decimal_places
    return int((value * multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def from_minor_units(amount_minor: int, decimal_places: int = 2) -> Decimal:
    return Decimal(amount_minor) / (Decimal(10) ** decimal_places)