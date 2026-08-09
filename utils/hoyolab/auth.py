from dataclasses import dataclass


@dataclass
class HoYoLABCredentials:
    ltuid: str | None = None
    ltoken: str | None = None

    ltuid_v2: str | None = None
    ltoken_v2: str | None = None
    ltmid_v2: str | None = None

    cookie_token_v2: str | None = None
    account_mid_v2: str | None = None
    account_id_v2: str | None = None

    def as_cookies(self) -> dict[str, str]:
        cookies = {}

        if self.ltuid:
            cookies["ltuid"] = self.ltuid

        if self.ltoken:
            cookies["ltoken"] = self.ltoken

        if self.ltuid_v2:
            cookies["ltuid_v2"] = self.ltuid_v2

        if self.ltoken_v2:
            cookies["ltoken_v2"] = self.ltoken_v2

        if self.ltmid_v2:
            cookies["ltmid_v2"] = self.ltmid_v2

        if self.cookie_token_v2:
            cookies["cookie_token_v2"] = self.cookie_token_v2

        if self.account_mid_v2:
            cookies["account_mid_v2"] = self.account_mid_v2

        if self.account_id_v2:
            cookies["account_id_v2"] = self.account_id_v2

        return cookies


def credentials_from_web_login(
        result
) -> HoYoLABCredentials:
    return HoYoLABCredentials(
        ltuid_v2=result.ltuid_v2,
        ltoken_v2=result.ltoken_v2,
        ltmid_v2=result.ltmid_v2,
        cookie_token_v2=result.cookie_token_v2,
        account_mid_v2=result.account_mid_v2,
        account_id_v2=result.account_id_v2
    )