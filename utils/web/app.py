import typing
import time
from datetime import datetime, timezone
from pathlib import Path
from fastapi import Cookie
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
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
    create_reminder,
    update_reminder,
    delete_reminder,
)
from utils.hoyolab.account_client import get_account_client
from utils.hoyolab.daily_note import get_resin



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
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="verify.html",
        context={
            "request": request,
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

    session = create_web_session(
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
        delete_web_session(
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
    session = get_web_session(
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

    session = get_web_session(
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
    session = get_web_session(
        cyrene_session
    )

    if session is None:
        return templates.TemplateResponse(
            request=request,
            name="verify.html",
            context={
                "request": request,
            },
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

        if current_resin < max_resin:
            replenished_at = (
                int(time.time())
                + recovery
            )

        planner_accounts.append({
            "genshin_uid": account["genshin_uid"],
            "nickname": account.get("nickname"),
            "level": account.get("level"),
            "genshin_server": account["genshin_server"],
            "current_resin": current_resin,
            "max_resin": max_resin,
            "replenished_at": replenished_at,
        })

    planner_reminders = []

    for reminder in reminders:

        config = reminder.get("config") or {}

        planner_reminders.append({
            "id": reminder["id"],
            "type": reminder["reminder_type"],
            "mode": reminder["reminder_mode"],
            "genshin_uid": reminder["genshin_uid"],
            "enabled": reminder["enabled"],
            "config": config,
        })

    return {
        "accounts": planner_accounts,
        "reminders": planner_reminders,
    }



@app.post("/api/planner/resin/reminder")
async def planner_resin_reminder(
    data: dict,
    cyrene_session: str | None = Cookie(default=None)
):
    user_id = await get_authenticated_user(
        cyrene_session
    )

    amount = data.get("amount")
    enabled = data.get("enabled")

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

    accounts = await get_accounts(
        user_id
    )

    if not accounts:
        raise HTTPException(
            status_code=404,
            detail="No Genshin account linked."
        )

    account = accounts[0]

    reminders = await get_reminders(
        user_id
    )

    reminder = next(
        (
            reminder
            for reminder in reminders
            if reminder["genshin_uid"]
            == account["genshin_uid"]
            and reminder["reminder_type"] == "resin"
            and reminder["reminder_mode"] == "automatic"
        ),
        None
    )

    if reminder is None:

        if enabled is False:
            return {
                "success": True,
                "enabled": False,
                "amount": None,
            }

        if amount is None:
            raise HTTPException(
                status_code=400,
                detail="A Resin amount is required."
            )

        reminder_id = await create_reminder(
            discord_user_id=user_id,
            reminder_type="resin",
            genshin_uid=account["genshin_uid"],
            config={
                "amount": amount
            },
            delivery_type="dm",
            reminder_mode="automatic",
            next_trigger_at=datetime.now(timezone.utc)
        )

    else:

        config = reminder.get("config") or {}

        if amount is not None:
            config["amount"] = amount

        if enabled is None:
            enabled = reminder["enabled"]

        await update_reminder(
            discord_user_id=user_id,
            reminder_id=reminder["id"],
            enabled=enabled,
            config=config,
        )

    return {
        "success": True,
        "enabled": enabled,
        "amount": amount,
    }


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