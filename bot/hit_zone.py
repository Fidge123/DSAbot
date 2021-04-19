import random
from typing import Optional, Any

from discord import Message

from bot.response import Response
from bot.stats import save_check

sizes = {
    "small": "s",
    "medium": "m",
    "large": "l",
    "huge": "xl",
    "klein": "s",
    "mittel": "m",
    "groß": "l",
    "riesig": "xl",
    "s": "s",
    "m": "m",
    "l": "l",
    "xl": "xl",
}

categories = {
    "humanoid": "h",
    "human": "h",
    "mensch": "h",
    "non-humanoid": "n",
    "non-human": "n",
    "wesen": "n",
    "kreatur": "n",
}


def parse(message: str) -> Optional[Any]:
    words = message.split(" ")

    try:
        has_keyword = any(
            [word in ["hz", "hitzone", "tz", "trefferzone"] for word in words]
        )
        size = sizes.get(
            [word.lower() for word in words if sizes.get(word.lower(), False)][0]
        )
        category = categories.get(
            [w.lower() for w in words if categories.get(w.lower(), False)][0]
        )

        if has_keyword and size and category:
            return size, category
    except:
        return None

    return None


def humanoid(zone_die, limits):
    if zone_die <= limits[0]:
        return "Kopf"
    if zone_die <= limits[1]:
        return "Torso"
    if zone_die <= limits[2]:
        if zone_die % 2 == 0:
            return "rechter Arm"
        else:
            return "linker Arm"
    else:
        if zone_die % 2 == 0:
            return "rechtes Bein"
        else:
            return "linkes Bein"


def non_humanoid4(zone_die, limits):
    if zone_die <= limits[0]:
        return "Kopf"
    if zone_die <= limits[1]:
        return "Torso"
    if zone_die <= limits[2]:
        return "vordere Beine"
    else:
        return "hintere Beine"


def non_humanoid6(zone_die, limits):
    if zone_die <= limits[0]:
        return "Kopf"
    if zone_die <= limits[1]:
        return "Torso"
    if zone_die <= limits[2]:
        return "vordere Gliedmaßen"
    if zone_die <= limits[3]:
        return "mittlere Gliedmaßen (z.B. Flügel)"
    if zone_die <= limits[4]:
        return "hintere Gliedmaßen"
    else:
        return "Schwanz"


def hitzone_effect(zone):
    if zone == "Kopf":
        return "Wundeffekt ab KO/2 Schadenspunkte: Eine Stufe Betäubung"
    if zone == "Torso":
        return "Wundeffekt ab KO/2 Schadenspunkte: Zusätzlich 1W3+1 SP"
    if "Arm" in zone:
        return "Wundeffekt ab KO/2 Schadenspunkte: Lässt Objekt fallen, außer Schilder und 2H-Waffen"
    else:
        return "Wundeffekt ab KO/2 Schadenspunkte: Geht zu Boden und erleidet Status _Liegend_"


def create_response(message: Message) -> Optional[Response]:
    parse_result = parse(message.content)

    if parse_result:
        size, category = parse_result
        zone_die = random.randint(1, 20)
        area = []

        if category == "h":
            if size == "s":
                hit = humanoid(zone_die, [6, 10, 18])
                area.append(f"Humanoid (klein): {hit} getroffen")
                area.append(hitzone_effect(hit))
            if size == "m":
                hit = humanoid(zone_die, [2, 12, 16])
                area.append(f"Humanoid (mittel): {hit} getroffen")
                area.append(hitzone_effect(hit))
            if size == "l":
                hit = humanoid(zone_die, [2, 6, 16])
                area.append(f"Humanoid (groß): {hit} getroffen")
                area.append(hitzone_effect(hit))
        if category == "n":
            if size == "s":
                area.append(
                    f"Non-Humanoid (klein): {non_humanoid4(zone_die, [4, 12, 16])} getroffen"
                )
            if size == "m":
                area.append(
                    f"Non-Humanoid (mittel): {non_humanoid4(zone_die, [4, 10, 16])} getroffen"
                )
            if size == "l":
                area.append(
                    f"Non-Humanoid, vierbeinig (groß): {non_humanoid4(zone_die, [5, 11, 16])} getroffen"
                )
                area.append(
                    f"Non-Humanoid, sechs Gliedmaßen (groß): {non_humanoid6(zone_die, [4, 12, 14, 16, 18])} getroffen"
                )
            if size == "xl":
                area.append(
                    f"Non-Humanoid (riesig): {non_humanoid6(zone_die, [2, 10, 14, 16, 18])} getroffen"
                )

        save_check(
            message.author,
            "HitZone",
            [zone_die],
            20,
        )

        response = "{mention} {result}\n{zones}".format(
            mention=message.author.mention,
            result="- Ergebnis: " + str(zone_die),
            zones="\n".join(area),
        )

        return Response(message.channel.send, response)

    return None
