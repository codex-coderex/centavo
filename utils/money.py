from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


CURRENCY_CODE = "PHP"
CURRENCY_SYMBOL = "₱"
DECIMAL_PLACES = 2
MINOR_UNITS_PER_MAJOR = Decimal("100")


def to_minor_units(amount) -> int:
    """
    Convert a PHP amount to centavos.
    """
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid money amount")

    minor = (value * MINOR_UNITS_PER_MAJOR).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )

    return int(minor)


def from_minor_units(amount_minor: int) -> Decimal:
    """
    Convert centavos back to PHP pesos.
    """
    return Decimal(amount_minor) / MINOR_UNITS_PER_MAJOR


def format_money(amount_minor: int) -> str:
    """
    Format centavos as PHP.
    """
    amount = from_minor_units(amount_minor)
    return f"{CURRENCY_SYMBOL}{amount:,.{DECIMAL_PLACES}f}"