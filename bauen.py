#!/usr/bin/env python3
"""Baut aus kalender.csv alles, was oeffentlich wird.

    python3 bauen.py

Eine Quelle, drei Ergebnisse:
    kalender.csv  ->  docs/literarisches-jahr.html   das Widget fuer die Website
                      docs/kalender.ics              zum Abonnieren
                      docs/index.html                Startseite mit beidem

kalender.csv ist die einzige Datei, die von Hand oder vom Agenten geaendert wird.
Alles unter docs/ wird bei jedem Lauf neu erzeugt und sollte nicht editiert werden.
"""
import csv, json, datetime, hashlib, pathlib, sys

HIER = pathlib.Path(__file__).parent
HEUTE = datetime.date.today()
QUELLE = "https://salonderkuenste.com/schreibjahr-2027"

# --- Was oeffentlich wird -------------------------------------------------
BESUCH = {"Festival", "Messe", "Markt", "Reihe", "Tagung"}
EINREICH = {"Ausschreibung", "Preis"}
# Eigene Termine: nur die, die nach aussen kommuniziert werden duerfen.
# Die Module mit Verlagsgaesten stehen im Einsatzplan auf "bestaetigen" und
# laesen sich oeffentlich als Zusage.
EIGEN_OK = {"2026-11_vorbereitungstag-1", "2026-12_vorbereitungstag-2",
            "2027-01_vorbereitungstag-3", "2027-01_bewerbungsschluss"}
# Portale, Verzeichnisse und Erfassungssysteme sind Werkzeuge des Betriebs,
# keine Termine. Fuer den internen Bestand richtig, fuer Besucher Ballast.
RAUS = ("A*dS Termine", "Kulturpool", "LiteraturSchweiz LiteraturLandschaft",
        "Veranstaltungserfassung", "eventfrog", "Literaturclub Audioformate", "Viceversa")
ZUGANG_TEXT = {"publikation": "Buchpublikation verlangt", "verlag": "nur über Verlage",
               "alter": "mit Altersgrenze", "wohnsitz": "an Wohnsitz gebunden",
               "unklar": "Bedingungen unklar", "offen": ""}

def tag(s):
    """Echtes Datum oder None. Format allein genuegt nicht, '2027-02-30' kommt vor."""
    try: return datetime.date.fromisoformat(s or "")
    except (ValueError, TypeError): return None

def monatsende(j, m):
    return (datetime.date(j + (m == 12), m % 12 + 1, 1) - datetime.timedelta(days=1)).day

def lies():
    p = HIER / "termine.csv"
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))

def auswaehlen(rows):
    out, eigene = [], []
    for x in rows:
        eig = x["id"] in EIGEN_OK or "vorbereitungstag" in x["id"] or "schreibjahr" in x["id"]
        if eig and x["id"] not in EIGEN_OK: continue
        if not eig and x["typ"] not in BESUCH | EINREICH: continue
        if any(x["name"].startswith(r) for r in RAUS): continue
        v, b, f = tag(x["datum_von"]), tag(x["datum_bis"]), tag(x.get("deadline_aktion"))
        # Ein Monatsdatum (2027-05-00) reicht: der Kalender gruppiert nach Monat.
        # Sonst fielen genau die Ausschreibungen heraus, deren Frist noch nicht
        # publiziert ist — und das sind die wertvollsten.
        monat = len(x["datum_von"]) == 10 and x["datum_von"][:7].count("-") == 1 \
                and x["datum_von"][5:7] != "00"
        if not v and not monat and not (x["typ"] in EINREICH and f): continue
        if v and v > datetime.date(2027, 12, 31): continue
        e = {"n": x["name"], "t": x["typ"], "o": x["ort"], "k": x["kanton"],
             "r": x["region"], "v": x["datum_von"], "s": x["datum_status"], "u": x["url"]}
        if b and v and b != v: e["b"] = x["datum_bis"]
        # Nur publizierte Einreichfristen. Abgeleitete Drucktermine bleiben intern.
        if x["typ"] in EINREICH and f and "[B abgeleitet" not in x.get("notiz", ""):
            e["f"] = x["deadline_aktion"]
        if x.get("zugang"):
            e["zg"] = x["zugang"]
            if ZUGANG_TEXT.get(x["zugang"]): e["zgt"] = ZUGANG_TEXT[x["zugang"]]
        # Was einen ganzen Monat fuellt, ist ein laufendes Angebot, kein Termin am 1.
        if b and x["datum_von"][-2:] == "01" and b.day == monatsende(b.year, b.month):
            e["lauf"] = 1; e.pop("b", None)
        if eig: e["eig"] = 1; eigene.append(e)
        out.append(e)
    # Start und Ende des Jahrgangs. Die Abschlussklausur ist terminlich belegt,
    # die eingeladenen Verlage bleiben unerwaehnt.
    out.append({"n": "Das Schreibjahr 2027 beginnt", "t": "Kurs", "o": "Olten", "k": "SO",
      "r": "DCH", "v": "2027-02-06", "b": "2027-02-07", "s": "bestaetigt", "u": QUELLE,
      "eig": 1, "no": "Auftaktklausur, zwei Tage. 14 Teilnehmende, Februar bis Dezember."})
    out.append({"n": "Das Schreibjahr 2027 endet", "t": "Kurs", "o": "Holdenweid", "k": "BL",
      "r": "DCH", "v": "2027-12-11", "b": "2027-12-12", "s": "bestaetigt", "u": QUELLE,
      "eig": 1, "no": "Abschlussklausur, zwei Tage."})
    out.sort(key=lambda z: (z["v"] if z["v"][-2:] != "00" else z["v"][:8] + "15", z["n"]))
    return out

# --- Kalenderdatei zum Abonnieren ----------------------------------------
def ics(termine):
    def esc(s):
        return str(s or "").replace("\\", "\\\\").replace(",", "\\,") \
                           .replace(";", "\;").replace("\n", " ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0",
         "PRODID:-//Salon der Kuenste//Literarisches Jahr//DE", "CALSCALE:GREGORIAN",
         "METHOD:PUBLISH", "X-WR-CALNAME:Das literarische Jahr",
         "X-WR-CALDESC:Festivals, Messen, Lesereihen und Ausschreibungen der Schweiz. "
         "Zusammengetragen vom Salon der Kuenste.",
         "X-WR-TIMEZONE:Europe/Zurich", "REFRESH-INTERVAL;VALUE=DURATION:P1D",
         "X-PUBLISHED-TTL:P1D"]
    stempel = HEUTE.strftime("%Y%m%d") + "T080000Z"
    n = 0
    for z in termine:
        p = z["v"].split("-")
        j, m = int(p[0]), int(p[1])
        t = int(p[2]) if p[2] != "00" else 1
        try: von = datetime.date(j, m, t)
        except ValueError: continue
        bis = tag(z.get("b")) or (datetime.date(j, m, monatsende(j, m)) if p[2] == "00" else von)
        uid = hashlib.md5((z["n"] + z["v"]).encode()).hexdigest()[:16]
        besch = [z["t"]]
        if z.get("f"): besch.append("Einreichfrist " + z["f"])
        if z.get("zgt"): besch.append(z["zgt"])
        if z["s"] != "bestaetigt": besch.append("Termin noch nicht bestaetigt")
        besch += [z["u"], "Aus dem Kalender des Salon der Kuenste"]
        L += ["BEGIN:VEVENT", f"UID:lj-{uid}@salonderkuenste", f"DTSTAMP:{stempel}",
              f"DTSTART;VALUE=DATE:{von:%Y%m%d}",
              f"DTEND;VALUE=DATE:{bis + datetime.timedelta(days=1):%Y%m%d}",
              f"SUMMARY:{esc(('Schreibjahr: ' if z.get('eig') else '') + z['n'])}",
              f"DESCRIPTION:{esc(' | '.join(besch))}", f"LOCATION:{esc(z['o'])}",
              f"URL:{esc(z['u'])}"]
        if z.get("f") and (fr := tag(z["f"])):
            L += ["BEGIN:VALARM", "TRIGGER:-P14D", "ACTION:DISPLAY",
                  f"DESCRIPTION:{esc('Einreichfrist naht: ' + z['n'][:50])}", "END:VALARM"]
        L.append("END:VEVENT"); n += 1
    L.append("END:VCALENDAR")
    return "\r\n".join(L), n

# --- Strukturierte Daten fuer Suchmaschinen -------------------------------
def jsonld(termine, anzahl=40):
    """Die naechsten Veranstaltungen als schema.org/Event.

    Inhalt in einem iframe zaehlt fuer Google nicht zur einbettenden Seite.
    Dieser Block schon: Patrick setzt ihn als Code-Baustein auf die Wix-Seite,
    dann kennt Google die Termine, obwohl sie im iframe stehen."""
    heute = HEUTE.isoformat()
    kommend = [z for z in termine
               if not z.get("eig") and z["v"] >= heute
               and z["t"] in ("Festival", "Messe", "Markt", "Tagung")][:anzahl]
    ev = []
    for z in kommend:
        v = z["v"] if z["v"][-2:] != "00" else z["v"][:8] + "01"
        e = {"@type": "Event", "name": z["n"], "startDate": v,
             "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
             "eventStatus": "https://schema.org/EventScheduled",
             "location": {"@type": "Place", "name": z["o"],
                          "address": {"@type": "PostalAddress",
                                      "addressLocality": z["o"], "addressCountry": "CH"}},
             "url": z["u"]}
        if z.get("b"): e["endDate"] = z["b"]
        ev.append(e)
    return json.dumps({"@context": "https://schema.org", "@type": "ItemList",
        "name": "Das literarische Jahr",
        "description": "Festivals, Messen, Lesereihen und Ausschreibungen der "
                       "Schweizer Literaturszene. Zusammengetragen vom Salon der Kuenste.",
        "itemListElement": [{"@type": "ListItem", "position": i, "item": e}
                            for i, e in enumerate(ev, 1)]},
        ensure_ascii=False, indent=2), len(ev)

# --- Zusammenbauen --------------------------------------------------------
FONT = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&'
        'family=IBM+Plex+Sans+Condensed:wght@400;500;600&display=swap">')

def main():
    rows = lies()
    t = auswaehlen(rows)
    daten = json.dumps(t, ensure_ascii=False, separators=(",", ":"))
    lies_teil = lambda n: (HIER / "bauteile" / n).read_text(encoding="utf-8")
    stand = HEUTE.strftime("%-d. ") + ["Januar","Februar","März","April","Mai","Juni","Juli",
        "August","September","Oktober","November","Dezember"][HEUTE.month-1] + HEUTE.strftime(" %Y")
    js = lies_teil("w_js2.html").replace('stand:"13. September 2026"', f'stand:"{stand}"')

    docs = HIER / "docs"; docs.mkdir(exist_ok=True)
    (docs / "literarisches-jahr.html").write_text(
        '<!DOCTYPE html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>Das literarische Jahr</title>\n' + FONT + lies_teil("w_css.html") +
        '</head>\n<body>\n' + lies_teil("w_body.html") +
        f"<script>const TERMINE={daten};</script>\n" + js + '</body>\n</html>\n',
        encoding="utf-8")
    kal, n_ics = ics(t)
    with open(docs / "kalender.ics", "w", encoding="utf-8", newline="") as f:
        f.write(kal)   # CRLF steht schon im Text, siehe RFC 5545
    (docs / "index.html").write_text(STARTSEITE.replace("{{ANZAHL}}", str(len(t)))
        .replace("{{STAND}}", stand).replace("{{FONT}}", FONT), encoding="utf-8")

    ld, n_ld = jsonld(t)
    # Die Daten als eigene Datei, damit der Baustein in Wix sie laden kann und
    # nie wieder angefasst werden muss.
    (docs / "termine.jsonld").write_text(ld, encoding="utf-8")
    (docs / "seo-baustein.html").write_text(SEO_BAUSTEIN, encoding="utf-8")

    offen = sum(1 for z in t if z.get("zg") == "offen")
    kb = (docs / "literarisches-jahr.html").stat().st_size // 1024
    print(f"termine.csv  {len(rows)} Zeilen")
    print(f"  -> docs/literarisches-jahr.html  {len(t)} Termine, {kb} KB")
    print(f"  -> docs/kalender.ics             {n_ics} Eintraege")
    print(f"  -> docs/index.html")
    print(f"  -> docs/termine.jsonld           {n_ld} Veranstaltungen als schema.org/Event")
    print(f"  -> docs/seo-baustein.html        der Baustein fuer Wix, bleibt unveraendert")
    print(f"  davon ohne Buchpublikation zugaenglich: {offen}")
    if not offen:
        print("  Hinweis: Filter 'ohne Buchpublikation' blendet sich aus, solange 0.")

SEO_BAUSTEIN = '''<!-- Strukturierte Daten fuer Google.
     Wix: Einstellungen > Erweitert > Custom Code > Code hinzufuegen
     Name:      Literaturagenda Termine
     Platzierung: Head
     Seiten:    nur die Seite Literaturagenda
     Laden:     Sofort laden

     Einmal einsetzen, nie wieder anfassen. Der Baustein holt die Termine
     bei jedem Seitenaufruf frisch von der Kalenderadresse. Aendert sich
     der Kalender, aendert sich das hier automatisch mit. -->
<script>
(function(){
  fetch("https://pcastellani-bot.github.io/literarisches-jahr/termine.jsonld")
    .then(function(a){ return a.ok ? a.json() : null; })
    .then(function(daten){
      if(!daten) return;
      var s = document.createElement("script");
      s.type = "application/ld+json";
      s.textContent = JSON.stringify(daten);
      document.head.appendChild(s);
    })
    .catch(function(){ /* ohne strukturierte Daten laedt die Seite normal weiter */ });
})();
</script>
'''

STARTSEITE = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Das literarische Jahr — Salon der Künste</title>
{{FONT}}
<style>
:root{--grund:#FFF7EB;--karte:#FFFCF6;--kante:#E7DBC8;--kante2:#CDBBA0;
  --tinte:#2A211B;--leise:#6E5E4F;--still:#9A8873;--orange:#CC6E25;--blau:#005081;
  --serif:'Newsreader',Georgia,serif;
  --sans:'IBM Plex Sans Condensed','Helvetica Neue',Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --grund:#191410;--karte:#231C16;--kante:#3B3027;--kante2:#57483C;
  --tinte:#F1E7DA;--leise:#B8A895;--still:#8C7C6A;--orange:#E8934F;--blau:#6FAAD6}}
*{box-sizing:border-box}
body{background:var(--grund);color:var(--tinte);font-family:var(--sans);
  font-size:15px;line-height:1.5;margin:0;padding:40px 20px 60px}
main{max-width:640px;margin:0 auto}
h1{font-family:var(--serif);font-weight:500;font-size:32px;margin:0 0 6px;
  letter-spacing:-.015em;line-height:1.1}
.unter{color:var(--leise);font-size:14px;margin:0 0 28px}
h2{font-family:var(--serif);font-size:17px;font-weight:600;margin:26px 0 6px}
p{margin:0 0 10px;color:var(--leise);font-size:14px}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;
  background:var(--karte);border:1px solid var(--kante);padding:2px 6px;border-radius:2px;
  color:var(--tinte);word-break:break-all}
.knopf{display:inline-block;font-size:14px;font-weight:500;padding:8px 18px;margin:4px 6px 4px 0;
  border:1px solid var(--blau);background:var(--blau);color:#fff;text-decoration:none;border-radius:2px}
.knopf:hover{background:var(--tinte);border-color:var(--tinte)}
.knopf.leer{background:transparent;color:var(--blau)}
.knopf.leer:hover{background:var(--blau);color:#fff}
iframe{width:100%;height:640px;border:1px solid var(--kante2);border-radius:2px;
  margin-top:10px;background:var(--karte)}
footer{margin-top:34px;padding-top:14px;border-top:1px solid var(--kante);
  font-size:12px;color:var(--still)}
footer a{color:var(--still)}
</style>
</head>
<body>
<main>
  <h1>Das literarische Jahr</h1>
  <p class="unter">{{ANZAHL}} Termine der Schweizer Literaturszene bis Dezember 2027.
    Festivals, Messen, Lesereihen und Ausschreibungen, jeder Eintrag mit Quelle.
    Zusammengetragen vom Salon der Künste. Stand {{STAND}}.</p>

  <a class="knopf" href="literarisches-jahr.html">Kalender öffnen</a>
  <a class="knopf leer" href="kalender.ics">Abonnieren</a>

  <h2>In die eigene Website einbauen</h2>
  <p>Diesen Code in einen HTML-Baustein setzen, in Wix unter
    Hinzufügen, Einbetten, HTML einbetten:</p>
  <p><code>&lt;iframe src="https://pcastellani-bot.github.io/literarisches-jahr/literarisches-jahr.html"
    width="100%" height="800" style="border:0" title="Das literarische Jahr"&gt;&lt;/iframe&gt;</code></p>

  <h2>Abonnieren</h2>
  <p>Wer den Kalender im eigenen Programm haben will, abonniert diese Adresse.
    Sie aktualisiert sich von selbst:</p>
  <p><code>webcal://pcastellani-bot.github.io/literarisches-jahr/kalender.ics</code></p>

  <iframe src="literarisches-jahr.html" title="Vorschau des Kalenders"></iframe>

  <footer>
    Angaben ohne Gewähr. Termine bitte beim Veranstalter prüfen.
    <a href="https://salonderkuenste.com/schreibjahr-2027">Das Schreibjahr 2027</a>
  </footer>
</main>
</body>
</html>
'''

if __name__ == "__main__":
    main()
