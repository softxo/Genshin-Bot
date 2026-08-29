import typing
import time
import tempfile
from datetime import (
    datetime,
    timezone
)
from pathlib import Path
from fastapi import Cookie
from fastapi import (
    FastAPI,
    HTTPException,
    Request
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from genshin.models.auth.geetest import (
    SessionMMTv4,
    SessionMMTResult,
    SessionMMTv4Result,
)
from utils.web.sessions import (
    get_challenge_session,
    complete_challenge,
)
from utils.web.auth import (
    create_verification,
    get_verification,
    create_web_session,
    get_web_session,
    delete_web_session,
)
from utils.hoyolab.database import (
    get_accounts,
    get_reminders,
    get_reminder,
    create_reminder,
    update_reminder,
    delete_reminder,
    update_achievement_tier,
)
from utils.hoyolab.account_client import get_account_client
from utils.hoyolab.daily_note import get_resin
from utils.achievements.achievements import load_achievements
from utils.achievements.progress import load_progress
from utils.achievements.importer import import_achievements



app = FastAPI(
    title="Cyrene Authentication",
    docs_url=None,
    redoc_url=None,
)

BASE_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(
    directory=BASE_DIR / "website" / "templates"
)

app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "website" / "static"
    ),
    name="static",
)


GT_V3_URL = "https://static.geetest.com/static/js/gt.0.5.0.js"



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
        },
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "request": request,
        },
    )

@app.get(
    "/verify",
    response_class=HTMLResponse,
)
async def verify_page(
    request: Request,
    next: str | None = None,
):
    if next and (
        not next.startswith("/")
        or next.startswith("//")
    ):
        next = None

    return templates.TemplateResponse(
        request=request,
        name="verify.html",
        context={
            "request": request,
            "next": next,
        },
    )


@app.post("/api/verify/create")
async def create_web_verification():

    verification = create_verification()

    return {
        "success": True,
        "token": verification.token,
        "code": verification.code,
        "expires_in": 300,
    }


@app.get("/api/verify/status")
async def verification_status(
    token: str
):
    verification = get_verification(token)

    if verification is None:
        raise HTTPException(
            status_code=404,
            detail="Verification request expired.",
        )

    if verification.user_id is None:
        return {
            "verified": False,
        }

    session = await create_web_session(
        verification.user_id
    )

    response = JSONResponse(
        content={
            "verified": True,
        }
    )

    response.set_cookie(
        key="cyrene_session",
        value=session.token,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return response


@app.post("/api/auth/logout")
async def logout(
    cyrene_session: str | None = Cookie(
        default=None
    )
):
    if cyrene_session:
        await delete_web_session(
            cyrene_session
        )

    response = JSONResponse(
        content={
            "success": True,
        }
    )

    response.delete_cookie(
        key="cyrene_session"
    )

    return response


@app.get("/api/auth/status")
async def auth_status(
    cyrene_session: str | None = Cookie(
        default=None
    )
):
    session = await get_web_session(
        cyrene_session
    )

    if session is None:
        return {
            "authenticated": False,
        }

    return {
        "authenticated": True,
        "user_id": session.user_id,
    }


async def get_authenticated_user(
    cyrene_session: str | None
) -> int:

    session = await get_web_session(
        cyrene_session
    )

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    return session.user_id


@app.get(
    "/planner",
    response_class=HTMLResponse,
)
async def planner(
    request: Request,
    cyrene_session: str | None = Cookie(default=None)
):
    session = await get_web_session(
        cyrene_session
    )

    if session is None:
        return RedirectResponse(
            url="/verify?next=/planner",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context={
            "request": request,
        },
    )


@app.get("/api/planner")
async def planner_data(
    cyrene_session: str | None = Cookie(default=None)
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    accounts = await get_accounts(
        user_id
    )

    reminders = await get_reminders(
        user_id
    )

    planner_accounts = []

    for account in accounts:

        client = await get_account_client(
            user_id,
            account["genshin_uid"]
        )

        if client is None:
            continue

        try:
            async with client:
                response = await client.get_genshin_daily_note(
                    client.genshin_uid,
                    client.genshin_server
                )

            current_resin, max_resin, recovery = get_resin(
                response
            )

        except Exception as error:
            print("===== WEBSITE PLANNER RESIN ERROR =====")
            print(type(error).__name__)
            print(error)
            print("========================================")

            continue

        replenished_at = None
        full_resin_at = None

        if current_resin < max_resin:

            remaining_resin = max_resin - current_resin

            replenished_at = (
                    int(time.time())
                    + recovery
            )

            full_resin_at = (
                    int(time.time())
                    + recovery
                    + ((remaining_resin - 1) * 480)
            )

        planner_accounts.append(
            {
                "genshin_uid": account["genshin_uid"],
                "nickname": account.get("nickname"),
                "level": account.get("level"),
                "genshin_server": account["genshin_server"],
                "current_resin": current_resin,
                "max_resin": max_resin,
                "replenished_at": replenished_at,
                "full_resin_at": full_resin_at,
            }
        )

    planner_reminders = []

    for reminder in reminders:

        if not reminder.get("enabled"):
            continue

        config = reminder.get("config") or {}

        account = next(
            (
                account
                for account in accounts
                if account["genshin_uid"]
                   == reminder["genshin_uid"]
            ),
            None,
        )

        planner_reminders.append(
            {
                "id": reminder["id"],
                "account_nickname": (
                    account.get("nickname")
                    if account
                    else None
                ),
                "type": reminder["reminder_type"],
                "mode": reminder["reminder_mode"],
                "genshin_uid": reminder["genshin_uid"],
                "config": config,
            }
        )

    return {
        "accounts": planner_accounts,
        "reminders": planner_reminders,
    }


@app.post("/api/planner/reminders")
async def create_planner_reminder(
    data: dict,
    cyrene_session: str | None = Cookie(default=None)
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    reminder_type = data.get("type")
    reminder_mode = data.get("mode", "automatic")
    genshin_uid = data.get("genshin_uid")
    config = data.get("config") or {}
    delivery_type = data.get("delivery_type", "dm")

    valid_types = {
        "resin",
        "expedition",
        "teapot",
        "transformer",
        "custom",
    }

    valid_modes = {
        "automatic",
        "manual",
    }

    valid_delivery_types = {
        "dm",
    }

    if reminder_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid reminder type."
        )

    if reminder_mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail="Invalid reminder mode."
        )

    if delivery_type not in valid_delivery_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid delivery type."
        )

    if not isinstance(config, dict):
        raise HTTPException(
            status_code=400,
            detail="Invalid reminder configuration."
        )

    accounts = await get_accounts(
        user_id
    )

    if not accounts:
        raise HTTPException(
            status_code=404,
            detail="No Genshin account linked."
        )

    if not genshin_uid:
        raise HTTPException(
            status_code=400,
            detail="A Genshin account is required."
        )

    account = next(
        (
            account
            for account in accounts
            if account["genshin_uid"] == genshin_uid
        ),
        None,
    )

    if account is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid Genshin account."
        )

    # --------------------------------
    # Resin validation
    # --------------------------------

    if reminder_type == "resin":

        amount = config.get("amount")

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="Invalid Resin amount."
            )

        if not 1 <= amount <= 200:
            raise HTTPException(
                status_code=400,
                detail="Resin must be between 1 and 200."
            )

        config["amount"] = amount

    # --------------------------------
    # Automatic reminder restrictions
    # --------------------------------

    if reminder_mode == "automatic":

        if reminder_type == "custom":
            raise HTTPException(
                status_code=400,
                detail="Custom reminders cannot use automatic mode."
            )

    reminder_id = await create_reminder(
        discord_user_id=user_id,
        reminder_type=reminder_type,
        genshin_uid=genshin_uid,
        config=config,
        delivery_type=delivery_type,
        reminder_mode=reminder_mode,
        next_trigger_at=datetime.now(timezone.utc),
    )

    return {
        "success": True,
        "id": reminder_id,
    }


@app.patch("/api/planner/reminders/{reminder_id}")
async def update_planner_reminder(
    reminder_id: int,
    data: dict,
    cyrene_session: str | None = Cookie(default=None)
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    reminder = await get_reminder(
        user_id,
        reminder_id
    )

    if reminder is None:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found."
        )

    enabled = data.get("enabled")
    config = data.get("config")

    if enabled is not None:
        if not isinstance(enabled, bool):
            raise HTTPException(
                status_code=400,
                detail="Invalid enabled value."
            )

    if config is not None:
        if not isinstance(config, dict):
            raise HTTPException(
                status_code=400,
                detail="Invalid reminder configuration."
            )

        if reminder["reminder_type"] == "resin":

            amount = config.get("amount")

            if amount is not None:

                try:
                    amount = int(amount)
                except (TypeError, ValueError):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid Resin amount."
                    )

                if not 1 <= amount <= 200:
                    raise HTTPException(
                        status_code=400,
                        detail="Resin must be between 1 and 200."
                    )

                config["amount"] = amount

    updated = await update_reminder(
        discord_user_id=user_id,
        reminder_id=reminder_id,
        enabled=enabled,
        config=config,
    )

    if not updated:
        raise HTTPException(
            status_code=400,
            detail="Nothing to update."
        )

    return {
        "success": True,
    }


@app.delete("/api/planner/reminders/{reminder_id}")
async def delete_planner_reminder(
    reminder_id: int,
    cyrene_session: str | None = Cookie(default=None)
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    deleted = await delete_reminder(
        user_id,
        reminder_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found."
        )

    return {
        "success": True,
    }


@app.get(
    "/events",
    response_class=HTMLResponse
)
async def events_page(
    request: Request,
    cyrene_session: str | None = Cookie(default=None),
    account_id: int | None = None,
):
    session = await get_web_session(
        cyrene_session
    )

    if session is None:
        return RedirectResponse(
            url="/verify?next=/events",
            status_code=303,
        )

    user_id = session.user_id

    accounts = await get_accounts(
        user_id
    )

    theater_data = {
        "best_round": 0,
        "arcanums": 0,
        "medals": 0,
        "end_time": 0,
    }
    selected_account = None

    if accounts:

        # Use the requested account if it belongs to this user.
        if account_id is not None:
            selected_account = next(
                (
                    account
                    for account in accounts
                    if account["id"] == account_id
                ),
                None,
            )

        # Otherwise, use the first account.
        if selected_account is None:
            selected_account = accounts[0]

        try:
            print("===== EVENTS ACCOUNT =====")
            print("Selected:", selected_account["nickname"])
            print("UID:", selected_account["genshin_uid"])
            print("==========================")

            client = await get_account_client(
                user_id,
                selected_account["genshin_uid"]
            )

            if client is not None:
                async with client:
                    theater = await client.get_imaginarium_theater()

                current_cycle = theater["data"][0]
                stat = current_cycle["stat"]

                print("===== THEATER SCHEDULE =====")
                print(current_cycle["schedule"])
                print("============================")

                acts = current_cycle["detail"]["rounds_data"]

                arcanums = sum(
                    1
                    for act in acts
                    if act.get("is_tarot") is True
                )

                elements = set()
                trial_characters = []

                for act in acts:
                    for avatar in act.get("avatars", []):

                        element = avatar.get("element")

                        if element:
                            elements.add(element)

                        if avatar.get("avatar_type") == 1:
                            trial_characters.append({
                                "name": avatar.get("name"),
                                "image": avatar.get("image"),
                            })

                if stat["max_round_id"] > 0:

                    theater_data = {
                        "has_data": stat["max_round_id"] > 0,
                        "best_round": stat["max_round_id"],
                        "arcanums": arcanums,
                        "medals": stat["medal_num"],
                        "elements": sorted(elements),
                        "trial_characters": trial_characters,
                    }

        except Exception as error:
            print("===== IMAGINARIUM THEATER ERROR =====")
            print(f"Type: {type(error).__name__}")
            print(f"Error: {error}")
            print("======================================")

    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={
            "request": request,
            "theater": theater_data,
            "accounts": accounts,
            "selected_account": selected_account,
        },
    )


@app.get(
    "/achievements",
    response_class=HTMLResponse,
)
async def achievements(
    request: Request,
    cyrene_session: str | None = Cookie(default=None)
):
    session = await get_web_session(
        cyrene_session
    )

    if session is None:
        return RedirectResponse(
            url="/verify?next=/achievements",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="achievements.html",
        context={
            "request": request,
        },
    )


@app.get("/api/achievements")
async def achievements_data(
    cyrene_session: str | None = Cookie(default=None)
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    achievements = load_achievements()
    saved_progress = await load_progress(user_id)

    categories = {}

    total_tiers = 0
    completed_tiers = 0

    for achievement in achievements:

        achievement_id = achievement.get("id")
        category = achievement.get("category")

        if not achievement_id or not category:
            continue

        tiers = achievement.get("tiers", [])

        if category not in categories:
            categories[category] = {
                "total": 0,
                "completed": 0,
            }

        achievement_progress = saved_progress.get(
            achievement_id,
            {}
        )

        tier_progress = achievement_progress.get(
            "tiers",
            {}
        )

        for tier in tiers:

            tier_number = str(
                tier.get("tier")
            )

            saved_tier = tier_progress.get(
                tier_number,
                {}
            )

            completed = saved_tier.get(
                "completed",
                False
            )

            current = saved_tier.get(
                "current",
                0
            )

            progress = tier.get(
                "progress"
            )

            timestamp = saved_tier.get(
                "timestamp"
            )

            note = saved_tier.get(
                "note"
            )

            tier["progress"] = progress
            tier["completed"] = completed
            tier["current"] = current
            tier["timestamp"] = timestamp
            tier["note"] = note

            total_tiers += 1
            categories[category]["total"] += 1

            if completed:
                completed_tiers += 1
                categories[category]["completed"] += 1

    return {
        "achievements": achievements,
        "categories": categories,
        "total": total_tiers,
        "completed": completed_tiers,
    }


@app.patch("/api/achievements/{achievement_id}/tiers/{tier}")
async def update_achievement_tier_api(
    achievement_id: str,
    tier: int,
    request: Request,
    cyrene_session: str | None = Cookie(default=None),
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated."
        )

    body = await request.json()

    completed = body.get("completed")

    if not isinstance(completed, bool):
        raise HTTPException(
            status_code=400,
            detail="The 'completed' field must be a boolean."
        )

    updated = await update_achievement_tier(
        discord_user_id=user_id,
        achievement_id=achievement_id,
        tier=tier,
        completed=completed,
    )

    return {
        "success": True,
        "updated": updated,
        "achievement_id": achievement_id,
        "tier": tier,
        "completed": completed
    }


@app.patch("/api/achievements/{achievement_id}/tiers/{tier}/note")
async def update_achievement_tier_note_api(
    achievement_id: str,
    tier: int,
    request: Request,
    cyrene_session: str | None = Cookie(default=None),
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated."
        )

    body = await request.json()

    note = body.get("note")

    if note is not None and not isinstance(note, str):
        raise HTTPException(
            status_code=400,
            detail="The 'note' field must be a string or null."
        )

    if isinstance(note, str):
        note = note.strip()

        if not note:
            note = None

    updated = await update_achievement_tier(
        discord_user_id=user_id,
        achievement_id=achievement_id,
        tier=tier,
        note=note,
    )

    return {
        "success": True,
        "updated": updated,
        "achievement_id": achievement_id,
        "tier": tier,
        "note": note,
    }


@app.post("/api/achievements/import")
async def import_achievements_api(
    request: Request,
    cyrene_session: str | None = Cookie(default=None),
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated."
        )

    form = await request.form()

    uploaded_file = form.get(
        "file"
    )

    if uploaded_file is None:
        raise HTTPException(
            status_code=400,
            detail="No achievement export was provided."
        )

    if not hasattr(
        uploaded_file,
        "read"
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid upload."
        )

    with tempfile.NamedTemporaryFile(
        suffix=".json",
        delete=False
    ) as temp_file:

        content = await uploaded_file.read()

        temp_file.write(content)

        temp_path = temp_file.name

    try:

        result = await import_achievements(
            user_id=user_id,
            export_file=temp_path,
        )

    finally:

        Path(temp_path).unlink(
            missing_ok=True
        )

    return result


@app.get(
    "/challenge/{token}",
    response_class=HTMLResponse,
)
async def challenge(token: str):
    session = get_challenge_session(token)

    if session is None:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Cyrene • Challenge Expired</title>
            </head>
            <body>
                <h1>Challenge Expired</h1>
                <p>
                    This authentication challenge has expired
                    or is no longer valid.
                </p>
            </body>
            </html>
            """,
            status_code=410,
        )

    if session.completed:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Cyrene • Challenge Completed</title>
            </head>
            <body>
                <h1>Challenge Already Completed</h1>
                <p>
                    This authentication challenge has already
                    been completed.
                </p>
            </body>
            </html>
            """,
            status_code=410,
        )

    mmt = session.mmt

    print("===== GEETEST MMT =====")
    print(mmt)
    print(mmt.model_dump())
    print(f"Type: {type(mmt).__name__}")
    print("=======================")

    is_v4 = isinstance(mmt, SessionMMTv4)

    if is_v4:
        gt_url = "https://static.geetest.com/v4/gt4.js"

        captcha_script = f"""
        const mmt = {mmt.model_dump_json()};

        const initParams = {{
            captchaId: mmt.captcha_id ?? mmt.gt,
            riskType: mmt.risk_type,
            userInfo: mmt.session_id
                ? JSON.stringify({{
                    mmt_key: mmt.session_id
                }})
                : undefined,
            apiServers: ["api-na.geetest.com"],
            product: "bind",
            language: "en"
        }};

        console.log("===== GEETEST INIT =====");
        console.log(initParams);
        console.log("========================");

        initGeetest4(
            initParams,
            (captcha) => {{

                captcha.onReady(() => {{
                    console.log("Geetest v4 ready");
                    captcha.showCaptcha();
                }});

                captcha.onSuccess(async () => {{

                    const result = captcha.getValidate();

                    console.log("===== GEETEST RESULT =====");
                    console.log(result);
                    console.log("==========================");

                    const response = await fetch(
                        "/challenge/{token}/send-data",
                        {{
                            method: "POST",

                            headers: {{
                                "Content-Type": "application/json"
                            }},

                            body: JSON.stringify({{
                                ...(mmt.session_id && {{
                                    session_id: mmt.session_id
                                }}),

                                ...(mmt.check_id && {{
                                    check_id: mmt.check_id
                                }}),

                                ...result
                            }})
                        }}
                    );

                    if (!response.ok) {{
                        console.error(
                            "Failed to submit CAPTCHA:",
                            await response.text()
                        );
                        return;
                    }}

                    showSuccess();
                }});

                captcha.onError((error) => {{
                    console.error("==== GEETEST ERROR ====");
                    console.error(error);
                    console.error("======================");
                }});
            }}
        );
        """

    else:
        gt_url = "https://static.geetest.com/static/js/gt.0.5.0.js"

        captcha_script = f"""
        const mmt = {mmt.model_dump_json()};

        const initParams = {{
            gt: mmt.gt,
            challenge: mmt.challenge,
            new_captcha: mmt.new_captcha,
            api_server: "api-na.geetest.com",
            https: /^https/i.test(window.location.protocol),
            product: "bind",
            lang: "en"
        }};

        console.log("===== GEETEST INIT =====");
        console.log(initParams);
        console.log("========================");

        initGeetest(
            initParams,
            (captcha) => {{

                captcha.onReady(() => {{
                    console.log("Geetest v3 ready");
                    captcha.verify();
                }});

                captcha.onSuccess(async () => {{

                    const result = captcha.getValidate();

                    console.log("===== GEETEST RESULT =====");
                    console.log(result);
                    console.log("==========================");

                    const response = await fetch(
                        "/challenge/{token}/send-data",
                        {{
                            method: "POST",

                            headers: {{
                                "Content-Type": "application/json"
                            }},

                            body: JSON.stringify({{
                                session_id: mmt.session_id,
                                geetest_challenge:
                                    result.geetest_challenge,
                                geetest_validate:
                                    result.geetest_validate,
                                geetest_seccode:
                                    result.geetest_seccode
                            }})
                        }}
                    );

                    if (!response.ok) {{
                        console.error(
                            "Failed to submit CAPTCHA:",
                            await response.text()
                        );
                        return;
                    }}

                    showSuccess();
                }});

                captcha.onError((error) => {{
                    console.error("==== GEETEST ERROR ====");
                    console.error(error);
                    console.error("======================");
                }});
            }}
        );
        """

    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1.0"
            >

            <meta
                name="referrer"
                content="no-referrer"
            >

            <title>Cyrene • HoYoLAB Verification</title>

            <script src="{gt_url}"></script>

            <style>
                body {{
                    margin: 0;
                    min-height: 100vh;

                    display: flex;
                    align-items: center;
                    justify-content: center;

                    background-color: #0f1117;
                    color: #ffffff;

                    font-family: Arial, sans-serif;
                }}

                .container {{
                    width: min(90%, 500px);
                    padding: 40px;

                    background-color: #181b24;
                    border-radius: 16px;

                    text-align: center;
                    box-sizing: border-box;
                }}

                h1 {{
                    margin-bottom: 16px;
                }}

                p {{
                    color: #b8bdc9;
                    line-height: 1.6;
                }}

                #captcha {{
                    margin-top: 24px;
                }}
            </style>
        </head>

        <body>
            <div class="container">

                <h1>Verification Required</h1>

                <p>
                    Cyrene encountered a CAPTCHA during your
                    HoYoLAB authentication.
                </p>

                <p>
                    Complete the CAPTCHA below to continue.
                </p>

                <div id="captcha"></div>

            </div>

            <script>

                function showSuccess() {{
                    document.body.innerHTML = `
                        <div
                            style="
                                min-height:100vh;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                background:#0f1117;
                                color:white;
                                font-family:Arial,sans-serif;
                                text-align:center;
                            "
                        >
                            <div>
                                <h1>✓ Verification Complete</h1>

                                <p>
                                    You may now return to Discord.
                                    Cyrene will continue automatically.
                                </p>
                            </div>
                        </div>
                    `;
                }}

                {captcha_script}

            </script>
        </body>
        </html>
        """,
    )


@app.post(
    "/challenge/{token}/send-data",
)
async def challenge_send_data(
    token: str,
    data: dict[str, typing.Any],
):
    session = get_challenge_session(token)

    if session is None:
        raise HTTPException(
            status_code=410,
            detail="This challenge has expired.",
        )

    if session.completed:
        raise HTTPException(
            status_code=410,
            detail="This challenge has already been completed.",
        )

    try:
        if isinstance(session.mmt, SessionMMTv4):
            result = SessionMMTv4Result(**data)
        else:
            result = SessionMMTResult(**data)

    except Exception as error:
        print("===== CAPTCHA RESULT ERROR =====")
        print(f"Type: {type(error).__name__}")
        print(f"Error: {error}")
        print(f"Data: {data}")
        print("================================")

        raise HTTPException(
            status_code=400,
            detail="Invalid CAPTCHA result.",
        ) from error

    complete_challenge(
        token,
        result,
    )

    return {
        "success": True,
    }