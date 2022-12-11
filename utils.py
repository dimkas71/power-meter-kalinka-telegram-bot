import aiogram.utils.markdown as md


def enter_counter_info_message():
    return md.text(
        "Введіть номер лічильника:",
        "Номер лічильника повинен задаватись у форматі",
        "ХХХХХ, де Х \- це цифра\. Не менш ніж 7 символів",
        sep="\n")


def enter_contract_info_message():
    return md.text(
        "Введіть номер договору",
        "Наприклад 123 Б",
        sep="\n"
    )


def parse(message: str) -> [str, int]:
    factory, value_as_str = message.split(":")
    if not factory.strip():
        raise ValueError("factory number should not be empty")
    if not value_as_str:
        raise ValueError("value should not be empty")
    return factory.strip(), int(value_as_str)
