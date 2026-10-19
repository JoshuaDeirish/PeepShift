import secrets


def generate_initial_pin(first_name, last_name, phone):
    digits = "".join(c for c in str(phone) if c.isdigit())
    last_four = digits[-4:] if len(digits) >= 4 else digits.rjust(4, "0")

    initials = (
        (first_name[:1] + last_name[:1]).upper()
        if first_name and last_name
        else f"{secrets.randbelow(100):02d}"
    )
    return f"{initials}{last_four}"