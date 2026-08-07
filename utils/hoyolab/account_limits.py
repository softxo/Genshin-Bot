DEFAULT_ACCOUNT_LIMIT = 3
PREMIUM_ACCOUNT_LIMIT = 10


def get_account_limit(is_premium: bool = False) -> int:
    if is_premium:
        return PREMIUM_ACCOUNT_LIMIT

    return DEFAULT_ACCOUNT_LIMIT