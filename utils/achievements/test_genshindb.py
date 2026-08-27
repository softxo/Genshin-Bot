import requests
import json


def test_achievement(name: str):

    response = requests.get(
        "https://genshin-db-api.vercel.app/api/v5/achievements",
        params={
            "query": name,
            "dumpResult": "true",
            "queryLanguages": "English",
            "resultLanguage": "English",
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    print(json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    test_achievement("Requiem of the Icewind")