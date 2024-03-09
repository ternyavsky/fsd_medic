import random


def get_code_cache_name(user_hash):
    return f"{user_hash}_ver_code"


def generate_random_digits_string(number):
    # Генерируем 5 случайных цифр и объединяем их в строку
    random_digits = [str(random.randint(0, 9)) for _ in range(number)]
    random_digits_string = "".join(random_digits)
    return random_digits_string
