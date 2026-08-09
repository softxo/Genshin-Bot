import typing
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from genshin.models.auth.geetest import SessionMMTResult, SessionMMT
from utils.web.sessions import (
    get_challenge_session,
    complete_challenge,
)

app = FastAPI(
    title="Cyrene Authentication",
    docs_url=None,
    redoc_url=None,
)


GT_V4_URL = "https://static.geetest.com/v4/gt4.js"


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
    print("=======================")

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

            <title>Cyrene • HoYoLAB Verification</title>

            <script src="{GT_V4_URL}"></script>

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
                const mmt = {mmt.model_dump_json()};

                const captcha = initGeetest4(
                    {{
                        captchaId: mmt.captcha_id ?? mmt.gt,
                        riskType: mmt.risk_type,
                        userInfo: mmt.session_id
                            ? JSON.stringify({{
                                mmt_key: mmt.session_id
                            }})
                            : undefined,
                        product: "bind",
                        language: "eng"
                        protocol: "https://"
                    }},
                    (captcha) => {{

                        captcha.onReady(() => {{
                            captcha.showCaptcha();
                        }});

                        captcha.onSuccess(async () => {{

                            const result = captcha.getValidate();

                            await fetch(
                                "/challenge/{token}/send-data",
                                {{
                                    method: "POST",

                                    headers: {{
                                        "Content-Type":
                                            "application/json"
                                    }},

                                    body: JSON.stringify({{
                                        ...(mmt.session_id && {{
                                            session_id:
                                                mmt.session_id
                                        }}),

                                        ...(mmt.check_id && {{
                                            check_id:
                                                mmt.check_id
                                        }}),

                                        ...result
                                    }})
                                }}
                            );

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
                                        <h1>
                                            ✓ Verification Complete
                                        </h1>

                                        <p>
                                            You may now return to Discord.
                                            Cyrene will continue automatically.
                                        </p>
                                    </div>
                                </div>
                            `;
                        }});
                        
                        captcha.onError((error) => {{
                        console.error("==== GEETEST ERROR ====");
                        console.error(error);
                        console.error("=======================");
                    }});
                }}
            );
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
        result = SessionMMTResult(**data)

    except Exception as error:
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