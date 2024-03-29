# D3Bot - **D**SA **D**iscord **D**ice Bot

A bot that makes it easy to roll skill checks for 5th edition Das Schwarze Auge (The dark eye).

# Usage Examples

## Normal Rolls

The bot allows normal dice rolls with comments and modifiers

| Input       | Example Output                   | Comment                                                                                                       |
| ----------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `1d6`       | @User <br>5 = 5                  | Rolls one six-sided die                                                                                       |
| `3d20`      | @User <br>3 + 12 + 9 = 24        | First number is the amount of dice, second the number of sides                                                |
| `!2d13`     | @User <br>1 + 13 = 14            | Prefixing with `!` is optional                                                                                |
| `3w20`      | @User <br>1 + 1 + 19 = 21        | You can use `d` as in dice or `w` as in Würfel (German for dice)                                              |
| `3D20 +1`   | @User <br>2 + 4 + 6 (+1) = 13    | You can add or subtract from the total.<br> **IMPORTANT:** this works different for skill checks (see below). |
| `!d20-1-2`  | @User <br>4 (-3) = 1             | Multiple modifiers are summed up.                                                                             |
| `3d6+3 Axt` | @User Axt<br>5 + 3 + 4 (+3) = 15 | You can add a comment at the end                                                                              |

## Skill Checks

These are specific rolls for _Das Schwarze Auge_. A skill check consists of three twenty-sided dice, a skill rating and an optional modifier.

If you want to roll for Kraftakt (Body Control) and you have a Fertigkeitswert (skill rating) of 4, Belastung (Encumbrance) of 1 and Gewandtheit (Agility) of 12 and Konstitution (Constitution) of 14, you should type the following:

> 12,12,14 @ 4 - 1

```
@User
EEW:     11  11  13
Würfel:  15   8  16
FW 4     -4      -3 = -3 FP
Nicht bestanden
```

In this example you have failed the check. If you succeed, it also calculated the Qualitätsstufe (quality level).

```
@User
EEW:     11  11  13
Würfel:   4  10  14
FW 4            -1 = 3 FP
Bestanden mit QS 1
```

It also allows giving multiple modifiers which are summed up and automatically detects critical successes and botches. You can also pass a comment.

> ! 14 14 15 @ 10-1-2 Kraftakt

```
@User Kraftakt
EEW:     11  11  12
Würfel:   1   1  18
FW 10            -6 = 4 FP
Kritischer Erfolg! (QS 2)
```

or

```
@User Kraftakt
EEW:     11  11  12
Würfel:  20  20   1
FW 10    -9  -9      = -8 FP
Patzer!
```

If you have a special abilities like a skill specialization, you may want to modify the resulting skill points (`FP`).
This modifier needs to be added AFTER any general modifier.

> ! 14 14 15 @ 10 -3 +2FP Fertigkeitsspezialisierung

```
@User Fertigkeitsspezialisierung
EEW:     11  11  12
Würfel:   4   5  18
FW 10 +2         -6 = 6 FP
Bestanden mit QS 2
```

### Impossible checks

Impossible checks are detected automatically.

> !4 5 15 @ 12 -4

```
@User
EEW:      0   1   9
Probe nicht möglich
```

### Routine checks

Same applies to routine checks, but they can be forced by replying with **Force**

> ! 14 14 15 @ 17 -2

```
@User
Routineprobe: 9 FP = QS 3
```

> Force

```
@User
EEW:     12  12  13
Würfel:   5  18  16
FW 17        -6  -3 = 8 FP
Bestanden mit QS 3
```

You may prefix any skill check with _force_ or _f_ directly to force the roll.

> !force 14 14 15 @ 17 -2

```
@User
EEW:     12  12  13
Würfel:   5  18  16
FW 17        -6  -3 = 8 FP
Bestanden mit QS 3
```

### Retry and Repeat

Checks can be retried by replying **Retry** or repeated with **Repeat**. Retries are automatically modified with -1 on top of the previous modifier. Repeats will keep the initial modifier.

> ! 14 14 15 @ 10-1-2 Kraftakt

```
@User Kraftakt
EEW:     11  11  12
Würfel:  20   1  18
FW 10    -9      -6 = -5 FP
Nicht bestanden
```

> Retry

```
@User Zweiter Versuch - Kraftakt
EEW:     10  10  11
Würfel:   6   9  16
FW 10            -5 = 5 FP
Bestanden mit QS 2
```

or

> Repeat

```
@User Zweite Probe - Kraftakt
EEW:     11  11  12
Würfel:   6   9  16
FW 10            -4 = 6 FP
Bestanden mit QS 2
```

### Fate Points / Schips

You can also reply with **Schips** followed by a three **Keep**/**k** or **Reroll**/**r**. This will decrease your number note called `Schips` by 1 and re-roll only the dice you marked with re-roll. This is not possible on critical successes or botches.

> ! 14 14 15 @ 10-1-2 Kraftakt

```
@User Kraftakt
EEW:     11  11  12
Würfel:  20   1  18
FW 10    -9      -6 = -5 FP
Nicht bestanden
```

> Schips rkr

or

> Schips Reroll Keep Reroll

```
@User 2 Schips verbleibend - Kraftakt
EEW:    11  11  12
Würfel:  3   1  15
FW 10           -3 = 7 FP
Bestanden mit QS 3
```

### Aptitude and Incompetent

If your character has aptitude in a certain skill, you may re-roll one die and keep the better result.
The bot supports this similarly to fate points.

> ! 14 14 15 @ 10-1-2 Kraftakt

```
@User Kraftakt
EEW:     11  11  12
Würfel:  20   1  18
FW 10    -9      -6 = -5 FP
Nicht bestanden
```

> Begabung 1

or

> Aptitude 1

```
@User Kraftakt
EEW:    11  11  12
Würfel:  3   1  18
FW 10           -6 = 4 FP
Bestanden mit QS 2
```

If your character is incompetent in a certain skill, your best die needs to be re-rolled.
This is interpreted as the lowest rolled number, using the lowest attribute value as a tiebreaker.

> ! 14 14 15 @ 10-1-2 Kraftakt

```
@User Kraftakt
EEW:     13  11  12
Würfel:   1   1  18
FW 10            -6 = 4 FP
Kritischer Erfolg! (QS 2)
```

> Unfähig

or

> Incompetent

```
@User Kraftakt
EEW:    13  11  12
Würfel:  1  20  18
FW 10       -9  -6 = -5 FP
Nicht bestanden
```

## Cumulative Checks

At the moment the bot only supports cumulative checks for one person that uses the same skill with the same base modifier throughout.

> !S5x5KR 12,12,12@2 Wildnisleben

```
@User

Runde  1: EEW  12  12  12  Würfel   7   7   3  FW2            = 2FP  QS1
Runde  2: EEW  12  12  12  Würfel  16  11  14  FW2  -4      -2=-4FP  Nicht bestanden
Runde  3: EEW  11  11  11  Würfel  12  20  11  FW2  -1  -9    =-8FP  Nicht bestanden
Runde  4: EEW  10  10  10  Würfel  11   4  11  FW2  -1      -1= 0FP  QS1
Runde  5: EEW  10  10  10  Würfel  16   1  12  FW2  -6      -2=-6FP  Nicht bestanden

Probe fehlgeschlagen nach 5 Runden (25KR)
```

Usage of fate points is not (yet) supported for cumulative checks.

## Generic Checks

These follow almost the same guidelines as skill checks but allow any number of attributes and don't support adding skill rating.
It shows the minimum needed skill rating to succeed after the arrow.

> 12,12 - 1

```
@User
EEW:    11  11
Würfel: 15   8
Nicht bestanden
```

```
@User
EEW:    11  11
Würfel:  4  10
Bestanden
```

It also allows giving multiple modifiers which are summed up and automatically detects critical successes and botches if you roll for 1 or 3 attributes.
You can also pass a comment.

> ! 14 14 15 -1-2 Kraftakt

```
@User Kraftakt
EEW:    11  11  12
Würfel:  1   1  18
Kritischer Erfolg!
```

or

```
@User Kraftakt
EEW:    11  11  12
Würfel: 20  20   1
Patzer!
```

> 17-4 Wuchtschlag II

```
@User Wuchtschlag II
EEW:    13
Würfel:  1 --> 3
Kritischer Erfolg!
```

```
@User Wuchtschlag II
EEW:    13
Würfel:  1 --> 18
Unbestätigter kritischer Erfolg
```

```
@User Wuchtschlag II
EEW:    13
Würfel: 20 --> 18
Patzer!
```

```
@User Wuchtschlag II
EEW:    13
Würfel: 20 --> 5
Unbestätigter Patzer
```

Impossible checks are detected automatically.

> 8 -3 -2 -4 Angst Schmerz WuchtschlagII

```
@User
EEW:     -1
Probe nicht möglich
```

You can also reply with **Schips** followed by a number of **Keep**/**k** or **Reroll**/**r**. This will decrease your number note called `Schips` by 1 and re-roll only the dice you marked with re-roll. This is not possible on critical successes or botches.

> 11-4 Parieren gegen Finte 2

```
@User Parieren gegen Finte 2
EEW:     7
Würfel: 17
Nicht bestanden
```

> Schips r

or

> Schips Reroll

```
@User 0 Schips verbleibend - Parieren gegen Finte 2
EEW:     7
Würfel:  5
Bestanden
```

## Attribute Check

No specific rolls are implemented yet. You can use the generic roll as a workaround.

## Close Combat

No specific rolls are implemented yet. You can use the generic roll as a workaround.

## Ranged Combat

No specific rolls are implemented yet. You can use the generic roll as a workaround.

## Regelwiki Integration

You can get links (and content) from https://ulisses-regelwiki.de by typing

> wiki [TITLE]

This will find the articles with similar titles (using `fuzzysearch`) and if it is a perfect match, load the content from the linked article to display it directly inline.

> wiki Wuchtschlag

```
@User
Wuchtschlag I-III (100%): http://ulisses-regelwiki.de/index.php/KSF_Wuchtschlag.html
**Wuchtschlag I-III**
(Basismanöver)
**Regel:**Die Attacke wird um 2 pro Stufe der Sonderfertigkeit erschwert. Bei Erfolg werden die Trefferpunkte um 2 pro Stufe der Sonderfertigkeit erhöht.
**Erschwernis:**–2/–4/–6
**Voraussetzungen:**Stufe I: KK 13; Stufe II: KK 15, Wuchtschlag I; Stufe III: KK 17, Wuchtschlag II
**Kampftechniken:**Hiebwaffen, Kettenwaffen, Raufen, Schwerter, Stangenwaffen, Zweihandhiebwaffen, Zweihandschwerter
**AP-Wert:**Stufe I/II/III: 15/20/25 Abenteuerpunkte
**Publikationen:**
Regelwerk, Seite 250
Der Rote Schlächter, Seite 60
```

> wiki Ignifaxius

```
Ignifaxius (100%): http://ulisses-regelwiki.de/index.php/ZS_Ignifaxius.html
Ignifaxius
**Probe:** MU/KL/CH
**Wirkung:** Aus den Fingern des Zaubernden schießt einen Flammenstrahl, der in gerader Linie sein Ziel trifft. Der Magier muss keine zusätzliche Aktion aufwenden,um nach dem Wirken des Zaubers zu treffen. Das Treffen ist in der Zauberdauer inbegriffen.
Das getroffene Ziel erleidet 2W6+(QS x 2) TrefferpunkteSchaden.
Der Flammenstrahl zählt als Fernkampfangriff mit einer Schusswaffe und kann entsprechend geblockt werden, und auch ein Ausweichen ist möglich. An Schilden erzeugt er Strukturschaden, wenn er auf sie trifft. Der Strahl trifft automatisch, wenn man sich nicht verteidigt.
Trifft der Flammenstrahl sein Ziel, werden die TP durch den RS des Ziels vermindert. Entflammbare Ziele werden bei 1-3 auf 1W6 angezündet und erleidet somit den Status Brennend auf kleiner Fläche.
**Zauberdauer:** 2 Aktionen
**AsP-Kosten:** 8 AsP (Kosten sind nicht modifizierbar)
**Reichweite:** 16 Schritt

[...]

**Publikationen:**
Regelwerk (3. überarbeiten. Aufl.), Seite 293
Aventurische Magie, Seite 157
Aventurische Magie 3 Bonusmaterial und Errata, Seite 10
```

> wiki igni

```
@User
Ignifaxius (80%): http://ulisses-regelwiki.de/index.php/ZS_Ignifaxius.html
Ignisphaero (80%): http://ulisses-regelwiki.de/index.php/ZS_Ignisphaero.html
```

## Numeric Notes

You can save a keyword-number combination

> note:note_id->42

> note_id is now 42

If the note already existed it will be updated

> note:note_id->+2

> note_id is now 44

> note:note_id->-2

> note_id is now 42

If you want to overwrite a note, you can use `=` instead of `->`

> note: note_id=1337

> note_id is now 1337

You can see all your notes as a list by writing `notes`

> notes

> note_id : 1337
> other : 1

You can delete notes with

> delete note note_id

> @User note_id war 1337 und wurde nun gelöscht.

## Hit Zones

You can generate a hit zone by using

> hitzone humanoid small

> @User - Ergebnis: 5
> Humanoid (klein): Kopf getroffen
> Wundeffekt ab KO/2 Schadenspunkte: Eine Stufe Betäubung

# Development

## Discord Token

If you don't have a token, [create a new app](https://discord.com/developers/applications) and activate the bot account for that app.
Use the token from the "Bot" section (NOT the client secret).

Once you have a token, create a file `.env` and add your token.

```
DISCORD_TOKEN=<YOUR TOKEN HERE>
```

## How to add the bot to your discord server

Select your [application](https://discord.com/developers/applications) and go to the **OAuth2** in the list on the left.
Here you need to generate a URL that will allow you to add the bot to any of your servers.

To generate this URL, select _bot_ in the **SCOPES** section.
A new section **BOT PERMISSIONS** appears.
You need to select:

- _Send Messages_
- _Add Reactions_
- _Read Message History_
- _Mention Everyone_

Afterwards copy the URL from the **SCOPES** section (e.g. `https://discord.com/api/oauth2/authorize?client_id=YOUR-CLIENT-ID&permissions=206912&scope=bot`) and open it in a new tab.
Now you can add the bot to your server if you have the correct server permissions.

To interact with the bot, make sure it has permissions to read in the relevant channel, the script is running (see below) and you write `SUMMON`.
If everything works, the bot will respond with `I am listening for rolls here`.

## How to install dependencies and run the script

The bot uses `pipenv` for dependency management.
If you don't have `pipenv` installed, you can install via one of the following commands or by following the [official documentation](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).

```sh-session
# Using pip
$ pip install -U pipenv

# macOS with brew
$ brew install pipenv

# Fedora
$ sudo dnf install pipenv
```

Once `pipenv` is installed, you need to install the dependencies and dev dependencies and enable the `pre-commit` hooks (optional).

```sh-session
$ pipenv install --dev

$ pipenv run pre-commit install
```

Afterwards execute the script via `pipenv`

```sh-session
$ pipenv run start
```

or active the `virtualenv` to run it as you would normally.

```sh-session
$ pipenv shell
Loading .env environment variables…
Launching subshell in virtual environment…

$ python bot/__main__.py
...

$ exit
```

## Run tests

Use the following command to run tests and generate coverage.

```sh-session
pipenv run test
```

To generate a coverage report run the command below.

```sh-session
pipenv run cov
```

## Create local copy of regelwiki

Add postgres URL to `.env` file.

```
DATABASE_URL=postgres://localhost/DSABot
```

This file will be loaded automatically by pipenv.

To start the generation, run

```
$ pipenv run wiki
```
