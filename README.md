# Das literarische Jahr

Terminkalender der Schweizer Literaturszene bis Dezember 2027, als Baustein für
[schreibjahr.ch](https://salonderkuenste.com/schreibjahr-2027).
Ein Projekt des Salon der Künste.

**Live:** https://pcastellani-bot.github.io/literarisches-jahr/

## Wie es funktioniert

```
termine.csv             ← die einzige Datei, die du änderst
      │
      │  bauen.py              (läuft automatisch bei jeder Änderung)
      ▼
docs/literarisches-jahr.html   ← was die Website einbettet
docs/kalender.ics              ← was man abonnieren kann
docs/index.html                ← Startseite mit beidem
```

Alles unter `docs/` wird bei jedem Lauf **neu erzeugt**. Ändere dort nichts von
Hand, es wird beim nächsten Bauen überschrieben.

## Ein Veranstalter meldet einen Termin

```
python3 eintragen.py
```

Fragt alles ab, baut die Zeile, prüft sie und baut den Kalender neu.
Danach veröffentlichen:

```
git add -A && git commit -m "Termin: ..." && git push
```

Die Adresse, an die Meldungen gehen, steht in `bauteile/w_js2.html` ganz oben
unter `meldeAdresse`.

## Einen Termin von Hand nachtragen

1. Oben auf `termine.csv` klicken, dann auf das Stiftsymbol
2. Eine neue Zeile anfügen, Felder mit Semikolon trennen
3. Unten auf «Commit changes» klicken

Zwei Minuten später ist die Website aktuell. Geht auch vom Handy.

**Pflichtfelder:** `id`, `name`, `typ`, `ort`, `kanton`, `region`, `datum_von`,
`datum_bis`, `datum_status`, `url`, `abrufdatum`, `beleg`.
Das vollständige Schema mit allen erlaubten Werten steht in
`../10_Literaturradar/SCHEMA.md`.

**Die drei Felder, auf die es ankommt:**

| Feld | Warum |
|---|---|
| `datum_status` | `bestaetigt` nur, wenn das Datum wirklich publiziert ist. `erwartet` heisst: aus dem Vorjahr abgeleitet. Auf der Website erscheint dann «noch nicht bestätigt» |
| `url` + `beleg` | Ohne Quelle kein Eintrag. Der `beleg` ist ein kurzes wörtliches Zitat von der Seite |
| `zugang` | Bei Ausschreibungen: `offen` heisst, dass keine Buchpublikation verlangt wird. Das ist der Filter, der den Kalender von anderen unterscheidet |

## Etwas ist kaputt

Unter «Actions» sieht man jeden Lauf. Ein rotes Kreuz heisst, dass `bauen.py`
gestolpert ist, meistens wegen einer Zeile mit falscher Feldzahl. Die Fehlermeldung
nennt die Zeile. Solange ein Lauf rot ist, bleibt die Website auf dem letzten
funktionierenden Stand stehen.

## Woher die Daten kommen

Erhoben im September 2026 von einem Multiagentsystem, dokumentiert in
`../10_Literaturradar/`. 217 Einträge, jeder mit Quelle und Abrufdatum, 64 Prozent
davon einzeln gegen die Quelle geprüft. Was nicht belegt werden konnte, steht in
den Lückendateien statt im Kalender.

Der Bestand veraltet planbar: Für Herbst 2027 war im September 2026 wenig
publiziert. Ein monatlicher Lauf schärft nach, was als `erwartet` markiert ist.
