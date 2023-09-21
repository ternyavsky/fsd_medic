from django.core.cache import cache
import random
import re


def get_code_cache_name(user_hash):
    return f"{user_hash}_ver_code"


def phone_normalize(number: str) -> str:
    out_str = ""
    is_firs_symb = True
    for symb in number:
        digits = "0123456789"
        if is_firs_symb:
            digits = '+' + digits
            is_firs_symb = False
        if symb in digits:
            out_str += symb
    if type(out_str) != str or len(out_str) < 5:
        return ""
    if out_str[0] == '+' and out_str[1] == '7':
        out_str = '7' + out_str[2::]
    elif out_str[0] == '8':
        out_str = '7' + out_str[1::]
    return out_str


def is_valid_phone_number(phone_number: str) -> bool:
    phone_number = phone_normalize(phone_number)
    print(phone_number)
    pattern = r'^(7[7,9]\d{9})$'
    match = re.match(pattern, phone_number) or re.match(r'^\+998[2-9]\d{8}$', phone_number)
    return bool(match)


def generate_random_digits_string(number):
    # Генерируем 5 случайных цифр и объединяем их в строку
    random_digits = [str(random.randint(0, 9)) for _ in range(number)]
    random_digits_string = ''.join(random_digits)
    return random_digits_string


def send_verification_code_msg(user_hash, number_to):
    code = generate_random_digits_string(5)
    print("DOCTOR VERIFICATION CODE = ", code)
    cache.set(get_code_cache_name(user_hash), code, 60 * 3)
