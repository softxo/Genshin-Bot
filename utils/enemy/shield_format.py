from utils.constants import COLOURED_ELEMENT_EMOJIS, SHIELD_EMOJIS, REFERENCE_NAMES, STAT_EMOJIS

TYPE_NAMES = {
    "physical": "Physical",
    "pyro": "Pyro",
    "hydro": "Hydro",
    "electro": "Electro",
    "cryo": "Cryo",
    "dendro": "Dendro",
    "anemo": "Anemo",
    "geo": "Geo",
    "void": "Void",
    "deepdark": "Deepdark"
}


def format_shields(shields):

    if not shields:
        return "None"

    text = []

    for shield in shields:

        if shield["type"] == "elementless":
            emoji = SHIELD_EMOJIS.get(shield["type"], "")

            hp = shield["hp"]
            hp_emoji = STAT_EMOJIS.get("hp", "")

            percent = hp["multiplier"] * 100

            reference = REFERENCE_NAMES.get(
                hp["reference"],
                hp["reference"].replace("_", " ").title()
            )

            text.append(
                f"{emoji} **Elementless Shield**\n"
                f"{hp_emoji} **HP**: {percent:.0f}% of **{reference}**"
            )


        elif shield["type"] == "elemental":
            emoji = COLOURED_ELEMENT_EMOJIS.get(
                shield["element"],
                ""
            )

            element = TYPE_NAMES.get(
                shield["element"],
                shield["element"].replace("_", " ").title()
            )

            if "gauge" in shield:

                text.append(
                    f"{emoji} **{element} Shield**\n"
                    f"**Gauge:** {shield['gauge']['value']}U"
                )


            elif "hp" in shield:

                hp = shield["hp"]
                hp_emoji = STAT_EMOJIS.get("hp", "")

                percent = hp["multiplier"] * 100

                reference = REFERENCE_NAMES.get(
                    hp["reference"],
                    hp["reference"].replace("_", " ").title()
                )

                text.append(
                    f"{emoji} **{element} Shield**\n"
                    f"{hp_emoji} **HP:** {percent:.0f}% of **{reference}**"
                )

        elif shield["type"] in ("void", "deepdark"):
            emoji = SHIELD_EMOJIS.get(shield["type"], "")

            shield_type = TYPE_NAMES[shield["type"]]

            hp = shield["hp"]
            hp_emoji = STAT_EMOJIS.get("hp", "")

            percent = hp["multiplier"] * 100

            reference = REFERENCE_NAMES.get(
                hp["reference"],
                hp["reference"].replace("_", " ").title()
            )

            text.append(
                f"{emoji} **{shield_type} Shield**\n"
                f"{hp_emoji} **HP:** {percent:.0f}% of **{reference}**"
            )

    return "\n\n".join(text)