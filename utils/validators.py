import re
import random
import string


def is_valid_steam_nickname(nickname):
    nickname = nickname.strip()
    if not nickname or len(nickname) > 32:
        return False
    return True


def is_valid_evm_address(address):
    pattern = r"^0x[a-fA-F0-9]{40}$"
    return re.match(pattern, address) is not None


def is_valid_trade_url(link):
    return link.startswith("https://steamcommunity.com/tradeoffer/new/?") and "partner=" in link and "token=" in link


def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = length))


def final_price_format(new_price):
    try:
        normalize_format = new_price.replace(",", ".")
        final_price = float(normalize_format)
        return final_price
    except ValueError:
        return False


def is_valid_price(new_price):
    try:
        min_price = 10 #here you can chance min price if you want
        return new_price >= min_price
    except ValueError:
        return False
