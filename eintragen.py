#!/usr/bin/env python3
"""Einen gemeldeten Termin in termine.csv aufnehmen.

    python3 eintragen.py

Fragt die noetigen Angaben ab, baut die Zeile, prueft sie und baut den
Kalender neu. Danach nur noch:  git add -A && git commit -m "..." && git push
"""
import csv, datetime, re, subprocess, sys, unicodedata, pathlib

HIER = pathlib.Path(__file__).parent
CSV = HIER / "termine.csv"
HEUTE = datetime.date.today().isoformat()

TYPEN = ["Festival", "Messe", "Reihe", "Einzelveranstaltung", "Preis",
         "Ausschreibung", "Kurs", "Tagung", "Markt"]
REGIONEN = {"DCH": "Deutschschweiz", "FCH": "Romandie", "ICH": "Ticino",
            "national": "schweizweit"}
STATUS = {"bestaetigt": "steht so auf der offiziellen Seite",
          "angekuendigt": "Vorankündigung oder Presse",
          "erwartet": "aus dem Vorjahr abgeleitet, nicht publiziert"}
ZUGANG = {"": "keine Ausschreibung", "offen": "jede und jeder darf einreichen",
          "publikation": "Buchveröffentlichung verlangt", "verlag": "nur über Verlage",
          "alter": "Altersgrenze", "wohnsitz": "an Wohnsitz gebunden",
          "unklar": "Bedingungen nicht auffindbar"}

def frag(text, pflicht=True, vorgabe=""):
    while True:
        a = input(f"{text}{f' [{vorgabe}]' if vorgabe else ''}: ").strip() or vorgabe
        if a or not pflicht: return a
        print("   Das Feld wird gebraucht.")

def waehl(text, optionen):
    print(f"\n{text}")
    keys = list(optionen) if isinstance(optionen, dict) else optionen
    for i, k in enumerate(keys, 1):
        erk = f"  — {optionen[k]}" if isinstance(optionen, dict) and optionen[k] else ""
        print(f"  {i}. {k or '(keines)'}{erk}")
    while True:
        a = input("Nummer: ").strip()
        if a.isdigit() and 1 <= int(a) <= len(keys): return keys[int(a) - 1]
        print("   Bitte eine der Nummern.")

def datum(text, pflicht=True):
    while True:
        a = frag(text + " (TT.MM.JJJJ, oder nur MM.JJJJ wenn der Tag offen ist)", pflicht)
        if not a and not pflicht: return ""
        if m := re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", a):
            t, mo, j = map(int, m.groups())
            try: return datetime.date(j, mo, t).isoformat()
            except ValueError: print("   Diesen Tag gibt es nicht."); continue
        if m := re.fullmatch(r"(\d{1,2})\.(\d{4})", a):
            return f"{m.group(2)}-{int(m.group(1)):02d}-00"
        print("   Format: 14.11.2026 oder 11.2026")

def slug(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:42]

def main():
    if not CSV.exists(): sys.exit(f"Nicht gefunden: {CSV}")
    kopf = open(CSV, encoding="utf-8-sig").readline().strip().split(";")
    vorhanden = {r["id"] for r in csv.DictReader(open(CSV, encoding="utf-8-sig"), delimiter=";")}

    print("\n  Neuer Termin für das literarische Jahr")
    print("  " + "─" * 46)
    name = frag("\nName der Veranstaltung")
    typ = waehl("Was ist es?", TYPEN)
    von = datum("\nBeginnt am")
    bis = datum("Endet am (leer = gleicher Tag)", pflicht=False) or von
    ort = frag("\nOrt")
    kanton = frag("Kanton (zwei Buchstaben, CH für landesweit)").upper()[:2]
    region = waehl("Sprachraum", REGIONEN)
    traeger = frag("\nVeranstalter", pflicht=False)
    url = frag("Link zur offiziellen Seite")
    if not url.startswith("http"): url = "https://" + url
    print("\n  Der Beleg ist ein wörtliches Zitat von dieser Seite, das den Termin")
    print("  bestätigt. Höchstens fünfzehn Wörter. Ohne ihn kein Eintrag.")
    beleg = frag("Beleg")
    status = waehl("\nWie sicher ist das Datum?", STATUS)
    kosten = frag("\nEintritt oder Kosten (leer = offen)", pflicht=False) or "OFFEN"

    zugang = frist = fristtyp = ""
    if typ in ("Ausschreibung", "Preis"):
        frist = datum("\nEinreichfrist (leer wenn keine)", pflicht=False)
        if frist: fristtyp = "Einreichfrist"
        zugang = waehl("Wer darf einreichen?", ZUGANG)

    neu = {k: "" for k in kopf}
    neu.update({"id": f"{von[:7]}_{slug(name)}", "name": name, "typ": typ,
        "traeger": traeger, "ort": ort, "kanton": kanton, "region": region,
        "datum_von": von, "datum_bis": bis, "datum_status": status,
        "turnus": "einmalig" if typ == "Einzelveranstaltung" else "jaehrlich",
        "publikum": "Breitenpublikum", "url": url, "abrufdatum": HEUTE,
        "beleg": beleg, "deadline_aktion": frist or "KEINE",
        "deadline_typ": fristtyp or "KEINE", "kosten": kosten, "zugang": zugang,
        "notiz": "von Veranstalter gemeldet"})
    if neu["id"] in vorhanden:
        neu["id"] += "-2"

    print("\n  " + "─" * 46)
    for k in ("id", "name", "typ", "datum_von", "datum_bis", "datum_status", "ort", "url"):
        print(f"  {k:14} {neu[k]}")
    if zugang: print(f"  {'zugang':14} {zugang}")
    if input("\n  So eintragen? [j/n] ").strip().lower() not in ("j", "ja", "y", ""):
        sys.exit("  Abgebrochen, nichts geändert.")

    with open(CSV, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, kopf, delimiter=";", quoting=csv.QUOTE_MINIMAL).writerow(neu)
    print("\n  Eingetragen. Baue den Kalender neu:\n")
    subprocess.run([sys.executable, "bauen.py"], cwd=HIER)
    print(f'\n  Wenn es stimmt, veröffentlichen mit:\n'
          f'    git add -A && git commit -m "Termin: {name[:40]}" && git push\n')

if __name__ == "__main__":
    main()
