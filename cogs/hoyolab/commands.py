import discord
from discord import app_commands
from discord.ext import commands
from utils.hoyolab.login import login_with_password
from utils.constants.emojis import ERROR_EMOJIS
from utils.constants.colours import ERROR_COLOURS
from utils.hoyolab.errors import (
    HoYoLabAuthenticationError,
    HoYoLabAccountNotFoundError,
    HoYoLabAccountLockedError,
    HoYoLabAccountMutedError,
    HoYoLabVerificationError,
    HoYoLabCaptchaError,
    HoYoLabRateLimitError,
    HoYoLabError,
    build_hoyolab_error_embed,
)
from utils.hoyolab.accounts import get_genshin_accounts
from utils.hoyolab.auth import HoYoLabCredentials
from utils.hoyolab.database import (
    save_account,
    get_account,
    get_account_count,
    account_exists,
    delete_account
)
from utils.hoyolab.account_limits import get_account_limit
from utils.hoyolab.client import HoYoLabClient



class GenshinAccountSelect(discord.ui.Select):
    def __init__(
            self,
            accounts,
            credentials,
            discord_user_id
    ):
        options = []

        for account in accounts:
            options.append(
                discord.SelectOption(
                    label=account["nickname"],
                    description=(
                        f"UID: {account['game_uid']} • "
                        f"AR: {account['level']}"
                    ),
                    value=account["game_uid"]
                )
            )

        super().__init__(
            placeholder="Select a Genshin Account...",
            options=options
        )

        self.accounts = accounts
        self.credentials = credentials
        self.discord_user_id = discord_user_id

    async def callback(
            self,
            interaction: discord.Interaction
    ):
        selected_uid = self.values[0]

        account = next(
            (
                account
                for account in self.accounts
                if account["game_uid"] == selected_uid
            ),
            None
        )

        if account is None:
            embed = build_hoyolab_error_embed(
                "error",
                "Account Not Found",
                "The selected Genshin account could not be found."
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return


        if account_exists(
                self.discord_user_id,
                selected_uid
        ):
            embed = build_hoyolab_error_embed(
                "invalid_input",
                "Account Already Linked",
                (
                    f"Genshin account `{selected_uid}` is already linked to Cyrene."
                )
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return


        account_count = get_account_count(
            self.discord_user_id
        )

        # TODO: replace this with actual premium check
        is_premium = False

        account_limit = get_account_limit(
            is_premium
        )

        if account_count >= account_limit:
            embed = build_hoyolab_error_embed(
                "warning",
                "Account Limit Reached",
                (
                    f"You currently have **{account_count}/{account_limit}** HoYoLab accounts linked."
                )
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        try:
            save_account(
                self.discord_user_id,
                self.credentials,
                genshin_uid=account["game_uid"],
                genshin_server=account["region"],
                nickname=account["nickname"],
                level=account["level"]
            )

        except Exception as error:
            print("===== ACCOUNT SAVE ERROR =====")
            print(f"Type: {type(error).__name__}")
            print(f"Error: {error}")
            print("==============================")

            embed = build_hoyolab_error_embed(
                "error",
                "Failed to Link Account",
                "The account could not be saved."
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title=(
                f"{ERROR_EMOJIS['success']} "
                "Genshin Account Linked"
            ),
            description=(
                f"**Name:** {account['nickname']}\n"
                f"**UID:** {account['game_uid']}\n"
                f"**AR:** {account['level']}\n"
                f"**Server:** {account['region_name'].removesuffix(' Server')}"
            ),
            color=ERROR_COLOURS["success"]
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


class GenshinAccountView(discord.ui.View):
    def __init__(
        self,
        accounts,
        credentials,
        discord_user_id
    ):
        super().__init__(timeout=300)

        self.add_item(
            GenshinAccountSelect(
                accounts,
                credentials,
                discord_user_id
            )
        )


class HoYoLabLoginModal(discord.ui.Modal, title="HoYoLab Login"):
    account = discord.ui.TextInput(
        label="Email / Username",
        placeholder="Enter your HoYoLab email or username",
        required=True,
        max_length=100
    )

    password = discord.ui.TextInput(
        label="Password",
        placeholder="Enter your HoYoLab password",
        required=True,
        max_length=100,
        style=discord.TextStyle.short
    )

    async def on_submit(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer(
            ephemeral=True
        )

        try:
            client, result = await login_with_password(
                self.account.value,
                self.password.value
            )

            print("===== LOGIN RESULT =====")
            print(type(result))
            print(result)
            print("========================")

        except HoYoLabAccountNotFoundError:
            embed = build_hoyolab_error_embed(
                "not_found",
                "HoYoLab Account Not Found",
                "The HoYoLab account could not be found."
            )

        except HoYoLabAuthenticationError:
            embed = build_hoyolab_error_embed(
                "invalid_input",
                "Invalid Credentials",
                "The HoYoLab email/username or password is incorrect."
            )

        except HoYoLabAccountLockedError:
            embed = build_hoyolab_error_embed(
                "error",
                "Account Locked",
                "This HoYoLab account is currently locked."
            )

        except HoYoLabAccountMutedError:
            embed = build_hoyolab_error_embed(
                "error",
                "Account Restricted",
                "This HoYoLab account is currently restricted."
            )

        except HoYoLabVerificationError:
            embed = build_hoyolab_error_embed(
                "warning",
                "Verification Failed",
                "HoYoLab verification could not be completed.\n"
                "Please try again later."
            )

        except HoYoLabCaptchaError:
            embed = build_hoyolab_error_embed(
                "warning",
                "CAPTCHA Required",
                "HoYoLab requires CAPTCHA verification before you can continue."
            )

        except HoYoLabRateLimitError:
            embed = build_hoyolab_error_embed(
                "warning",
                "Too Many Requests",
                "HoYoLab is temporarily rate-limiting requests.\n"
                "Please try again later."
            )

        except HoYoLabError:
            embed = build_hoyolab_error_embed(
                "error",
                "HoYoLab Login Failed",
                "An unexpected HoYoLab error occurred."
            )

        else:
            accounts = await get_genshin_accounts(client)

            if not accounts:
                embed = build_hoyolab_error_embed(
                    "not_found",
                    "No Genshin Accounts Found",
                    "No Genshin accounts are linked to this HoYoLab account."
                )

                await interaction.followup.send(
                    embed=embed,
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title=(
                    f"{ERROR_EMOJIS['success']} "
                    "HoYoLab Login Successful"
                ),
                description=(
                    "Your HoYoLab account has been successfully authenticated.\n\n"
                    "**Select the Genshin account you want to link to Cyrene:**"
                ),
                color=ERROR_COLOURS["success"]
            )

            await interaction.followup.send(
                embed=embed,
                view=GenshinAccountView(
                    accounts,
                    result,
                    interaction.user.id
                 ),
                ephemeral=True
            )

            return

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )


class HoYoLabCookieContinueView(discord.ui.View):
    def __init__(
        self,
        ltuid_v2: str,
        ltoken_v2: str,
        ltmid_v2: str
    ):
        super().__init__(timeout=300)

        self.ltuid_v2 = ltuid_v2
        self.ltoken_v2 = ltoken_v2
        self.ltmid_v2 = ltmid_v2

    @discord.ui.button(
        label="Continue",
        style=discord.ButtonStyle.primary
    )
    async def continue_login(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            HoYoLabCookieModalStep2(
                ltuid_v2=self.ltuid_v2,
                ltoken_v2=self.ltoken_v2,
                ltmid_v2=self.ltmid_v2
            )
        )


class HoYoLabCookieModalStep1(
    discord.ui.Modal,
    title="HoYoLab Cookies • 1/2"
):
    ltuid_v2 = discord.ui.TextInput(
        label="ltuid_v2",
        placeholder="Paste your ltuid_v2 cookie...",
        required=True,
        max_length=200
    )

    ltoken_v2 = discord.ui.TextInput(
        label="ltoken_v2",
        placeholder="Paste your ltoken_v2 cookie...",
        required=True,
        max_length=500
    )

    ltmid_v2 = discord.ui.TextInput(
        label="ltmid_v2",
        placeholder="Paste your ltmid_v2 cookie...",
        required=True,
        max_length=500
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        ltuid_v2 = self.ltuid_v2.value.strip()
        ltoken_v2 = self.ltoken_v2.value.strip()
        ltmid_v2 = self.ltmid_v2.value.strip()

        embed = discord.Embed(
            title="HoYoLab Cookies • 1/2",
            description=(
                "The first three cookies have been received.\n\n"
                "Click **Continue** to enter the remaining three cookies."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            view=HoYoLabCookieContinueView(
                ltuid_v2,
                ltoken_v2,
                ltmid_v2
            ),
            ephemeral=True
        )


class HoYoLabCookieModalStep2(
    discord.ui.Modal,
    title="HoYoLab Cookies • 2/2"
):
    cookie_token_v2 = discord.ui.TextInput(
        label="cookie_token_v2",
        placeholder="Paste your cookie_token_v2 cookie...",
        required=True,
        max_length=500
    )

    account_mid_v2 = discord.ui.TextInput(
        label="account_mid_v2",
        placeholder="Paste your account_mid_v2 cookie...",
        required=True,
        max_length=500
    )

    account_id_v2 = discord.ui.TextInput(
        label="account_id_v2",
        placeholder="Paste your account_id_v2 cookie...",
        required=True,
        max_length=500
    )

    def __init__(
        self,
        *,
        ltuid_v2: str,
        ltoken_v2: str,
        ltmid_v2: str
    ):
        super().__init__()

        self.ltuid_v2_value = ltuid_v2
        self.ltoken_v2_value = ltoken_v2
        self.ltmid_v2_value = ltmid_v2

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(
            ephemeral=True
        )

        credentials = HoYoLabCredentials(
            ltuid_v2=self.ltuid_v2_value,
            ltoken_v2=self.ltoken_v2_value,
            ltmid_v2=self.ltmid_v2_value,
            cookie_token_v2=self.cookie_token_v2.value.strip(),
            account_mid_v2=self.account_mid_v2.value.strip(),
            account_id_v2=self.account_id_v2.value.strip()
        )

        print("===== COOKIE LOGIN =====")
        print("ltuid_v2: present")
        print("ltoken_v2: present")
        print("ltmid_v2: present")
        print("cookie_token_v2: present")
        print("account_mid_v2: present")
        print("account_id_v2: present")
        print("========================")

        try:
            async with HoYoLabClient(credentials) as client:
                result = await client.get_game_roles()

        except Exception as error:
            print("===== COOKIE LOGIN ERROR =====")
            print(f"Type: {type(error).__name__}")
            print(f"Error: {error}")
            print("==============================")

            embed = build_hoyolab_error_embed(
                "error",
                "Cookie Login Failed",
                "An error occurred while contacting HoYoLab."
            )

            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )

            return

        print("===== API RESULT =====")
        print(result)
        print("======================")

        if result.get("retcode") != 0:
            embed = build_hoyolab_error_embed(
                "error",
                "Cookie Login Failed",
                (
                    "HoYoLab rejected the provided cookies.\n"
                    f"Message: {result.get('message', 'Unknown error')}"
                )
            )

            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )

            return

        accounts = result.get(
            "data",
            {}
        ).get(
            "list",
            []
        )

        genshin_accounts = [
            account
            for account in accounts
            if account.get("game_biz") == "hk4e_global"
        ]

        if not genshin_accounts:
            embed = build_hoyolab_error_embed(
                "not_found",
                "No Genshin Accounts Found",
                "No Genshin accounts are linked to this HoYoLab account."
            )

            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title=(
                f"{ERROR_EMOJIS['success']} "
                "Cookie Login Successful"
            ),
            description=(
                "Your HoYoLab cookies are valid.\n\n"
                "**Select the Genshin account you want to link to Cyrene:**"
            ),
            color=ERROR_COLOURS["success"]
        )

        await interaction.followup.send(
            embed=embed,
            view=GenshinAccountView(
                genshin_accounts,
                credentials,
                interaction.user.id
            ),
            ephemeral=True
        )


class HoYoLabAccountsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Discord Login",
        style=discord.ButtonStyle.secondary,
        emoji="<:Discord:1535081024470392842>"
    )
    async def discord_login(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            HoYoLabLoginModal()
        )

    @discord.ui.button(
        label="Browser Login",
        style=discord.ButtonStyle.secondary,
        emoji="<:Browser:1535081023115894846>"
    )
    async def browser_login(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "Browser login will be implemented here.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Cookie Login",
        style=discord.ButtonStyle.secondary,
        emoji="<:Cookies:1535081025888321607>"
    )
    async def cookie_login(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            HoYoLabCookieModalStep1()
        )


class HoYoLab(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="accounts",
        description="Manage your HoYoLab accounts."
    )
    async def accounts(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="<:Link:1535081027108741201> Link HoYoLab Account(s)",
            description=(
                "Welcome to the HoYoLab Account Linking page!\n"
                "The purpose of this page is to link your HoYoLab account to Cyrene, which will enable you to view certain information about your Genshin account.\n\n"
                "**__Features__**\n"
                "- **Check your in-game Resin count in real-time** (Current Resin, Replenished in ..., Fully replenished in ..., Automatic Notifier)\n"
                "- **Check your in-game Expedition progress in real-time** (Characters on Expeditions, Time left for each character, Resources)\n"
                '- **Claim your "Daily Check-in" rewards** (Manually or Automatically)\n'
                '- **View information about your "Spiral Abyss" progression**\n'
                "*And more*\n\n"
                "To start linking, click on one of the options below."
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Your HoYoLab password is never stored by Cyrene."
        )

        await interaction.response.send_message(
            embed=embed,
            view=HoYoLabAccountsView(),
            ephemeral=True
        )

    @app_commands.command(
        name="unlink",
        description="Unlink a Genshin account from Cyrene."
    )
    @app_commands.describe(
        genshin_uid="The Genshin UID you want to unlink."
    )
    async def unlink(
            self,
            interaction: discord.Interaction,
            genshin_uid: str
    ):
        account = get_account(
            interaction.user.id,
            genshin_uid
        )

        if account is None:
            embed = build_hoyolab_error_embed(
                "not_found",
                "Account Not Found",
                (
                    f"Genshin account `{genshin_uid}` is not linked to your Cyrene account."
                )
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        deleted = delete_account(
            interaction.user.id,
            genshin_uid
        )

        if not deleted:
            embed = build_hoyolab_error_embed(
                "error",
                "Failed to Unlink Account",
                (
                    "Cyrene was unable to unlink the selected Genshin account."
                )
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title=(
                f"{ERROR_EMOJIS['success']} Genshin Account Unlinked"
            ),
            description=(
                f"Genshin account **{account['nickname']}** [`{account['genshin_uid']}`] has been successfully unlinked from Cyrene."
            ),
            color=ERROR_COLOURS["success"]
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(HoYoLab(bot))