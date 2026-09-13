#!/usr/bin/env python3
"""Erzeugt aus dem internen Bestand die oeffentliche termine.csv.

    python3 exportieren.py

Der interne Bestand (../10_Literaturradar/kalender.csv) ist Patricks
Planungswerkzeug: er enthaelt Bewertungen, Andockarten, Drucktermine und
Kontaktnamen. Nichts davon gehoert in ein oeffentliches Repository.

Diese Datei erzeugt daraus die Fassung, die hier liegen darf.
Danach ist termine.csv die Wahrheit fuer den oeffentlichen Kalender und
wird von Hand oder vom Recherche-Agenten weitergepflegt.
"""
import csv, pathlib, re, sys

HIER = pathlib.Path(__file__).parent
INTERN = HIER.parent / "10_Literaturradar" / "kalender.csv"

# Was oeffentlich stehen darf. Alles andere faellt weg.
SPALTEN = ["id","name","typ","traeger","ort","kanton","region","datum_von","datum_bis",
           "datum_status","turnus","publikum","url","abrufdatum","beleg",
           "deadline_aktion","deadline_typ","kosten","zugang","alter_max","wohnsitz","notiz"]
# Weggelassen und warum:
#   zielgruppen_fit, andockart  Patricks Bewertung und Strategie
#   kontakt                     Namen von Programmverantwortlichen, Personendaten
#   groesse, agent              intern, fuer Besucher ohne Wert

# Interne Marker aus der Notiz entfernen
MARKER = re.compile(r"\[(B abgeleitet|V korrigiert|V geprueft|Dublette|gleiches Format)[^\]]*\]")
INTERN_TXT = re.compile(r"EIGENER TERMIN[^.]*\.\s*|ENTSCHEIDUNG PATRICK OFFEN:.*", re.I)

def main():
    if not INTERN.exists():
        sys.exit(f"Interner Bestand nicht gefunden: {INTERN}")
    rows = list(csv.DictReader(open(INTERN, encoding="utf-8-sig"), delimiter=";"))
    raus = 0
    out = []
    for r in rows:
        e = {s: r.get(s, "") for s in SPALTEN}
        # Drucktermine sind Patricks interne Planung, keine Frist des Veranstalters
        if r.get("deadline_typ") == "Drucktermin" or "[B abgeleitet" in r.get("notiz", ""):
            e["deadline_aktion"], e["deadline_typ"] = "", ""
            raus += 1
        # Interne Dateipfade sind auf der Website tote Links
        if e["url"].startswith("..") or e["url"].endswith(".md"):
            e["url"] = "https://schreibjahr.ch"
        n = MARKER.sub("", INTERN_TXT.sub("", e["notiz"])).strip(" .")
        e["notiz"] = " ".join(n.split())
        out.append(e)
    with open(HIER / "termine.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, SPALTEN, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writeheader(); w.writerows(out)
    print(f"termine.csv: {len(out)} Zeilen, {len(SPALTEN)} Spalten")
    print(f"  entfernt: zielgruppen_fit, andockart, kontakt, groesse, agent")
    print(f"  {raus} abgeleitete Drucktermine geleert")

if __name__ == "__main__":
    main()
