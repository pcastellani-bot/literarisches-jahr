# Läufe

## 2026-09-13

**Ergebnis: keine Änderung an `termine.csv`.** Der monatliche Nachtrag konnte
diesmal nicht durchgeführt werden, weil die Ausführungsumgebung keinen
Netzwerkzugriff auf externe Seiten zulässt.

### Was passiert ist

Für alle drei Aufgaben wurden Recherche-Agenten eingesetzt:

- **Aufgabe 1** (Nachschärfen): alle 47 Zeilen mit `datum_status = erwartet`
  wurden zur Prüfung eingeplant.
- **Aufgabe 2** (Fristen): alle 28 Zeilen mit `deadline_aktion` in den
  nächsten vier Monaten (bis 2027-01-13) wurden zur Prüfung eingeplant.
- **Aufgabe 3** (Neues): eine gezielte Suche nach neuen Ausschreibungen und
  Festivals für das zweite Halbjahr 2027 wurde beauftragt.

Beim Versuch, die jeweiligen `url`-Felder aufzurufen, hat sich gezeigt, dass
`WebFetch` für jede getestete Domain mit `EGRESS_BLOCKED` abgewiesen wurde —
bestätigt auch für neutrale Kontroll-Domains wie wikipedia.org und
example.com. Ein direkter `curl`-Versuch über die Shell schlug ebenfalls mit
einem 403 des Egress-Proxys fehl (organisationsweite Policy, kein
Einzelfall). Erreichbar war einzig die serverseitige `WebSearch`-Funktion,
die aber nur KI-zusammengefasste Suchtreffer liefert, keinen tatsächlich
abgerufenen Seiteninhalt. Mehrere Agenten haben zudem beobachtet, dass diese
Zusammenfassungen konkrete Daten erfunden haben, die durch keine der
angezeigten Quellen gedeckt waren (z. B. ein erfundenes Datum für
"Zürich liest '27", eine falsch zugeordnete Jahreszahl bei den Weinfelder
Buchtagen).

Da die Grundregel dieses Kalenders lautet "keine Zeile ohne aufgerufene
Quelle, nicht aus einer Suchergebnis-Zusammenfassung", wurden **keine**
Zeilen in `termine.csv` verändert. Das gilt auch für Fälle, in denen die
Suchzusammenfassung ein bestehendes Datum bestätigt zu haben schien —
ohne echten Seitenabruf ist das kein Beleg im Sinne der Regeln.

### Im Einzelnen

- **Erwartet-Zeilen geprüft:** 47 von 47. Bestätigt: 0. Bei allen 47 blieb
  `datum_status = erwartet` unverändert.
- **Fristen geprüft:** 28 von 28. Geändert: 0. Zurückgezogen: 0.
- **Neue Einträge:** 0 hinzugefügt.
- **Gesucht, aber nicht übernommen** (unbestätigte Hinweise aus der Suche,
  die ein künftiger Lauf mit echtem Seitenzugriff prüfen sollte):
  - Leipziger Buchmesse 2027, mögliches Datum 18.–21. März 2027
    (deckt sich mit dem bereits gespeicherten Datum, aber nicht bestätigt)
  - Literaturfestival Zürich 2027, möglicher Termin Mitte Juli 2027
  - A*dS-Ausschreibungsseite (a-d-s.ch/foerderungen/ausschreibungen) als
    Sammelstelle für neue Calls
  - Zentralschweizer Literaturwettbewerb, nächste Ausschreibung
    voraussichtlich Frühling 2027
  - Dienemann-Stiftung Literaturpreis "Das zweite Buch" (voraussichtlich
    `zugang = publikation`, daher für diesen Kalender wahrscheinlich
    weniger relevant)
  - Prix Vanil Noir: ein Hinweis auf eine mögliche Fristverschiebung auf
    28. Februar 2027 (statt 29. Dezember 2026) — nicht bestätigt, unbedingt
    im nächsten Lauf zuerst prüfen
  - Mehrere Zeilen, bei denen die Suchzusammenfassung nahelegt, dass
    `zugang` präziser gefasst werden könnte (z. B. `2026-10_aks-atelier-x`
    und `2026-10_be-tete-a-tete` eher `wohnsitz` statt `publikation`,
    `2026-12_prix-ecriture-gruyeres` eher `alter` statt `offen`,
    `2027-04_festival-histoire-et-cite` eher `offen`) — ebenfalls nicht
    übernommen, da nicht gegen eine echte Seite verifiziert.

### Empfehlung für den nächsten Lauf

Diese Ausführungsumgebung müsste mit Netzwerkzugriff auf externe Domains
(oder zumindest auf die betroffenen Organisations-Websites) konfiguriert
sein, damit `WebFetch`/`curl` tatsächlich Seiten laden können. Solange das
nicht der Fall ist, kann der monatliche Nachtrag nur protokollieren, dass er
nichts Verifizierbares beitragen konnte — Daten "aus dem Gedächtnis" oder
aus reinen Suchzusammenfassungen zu übernehmen, würde die Kernregel des
Kalenders (`bestaetigt` heisst wirklich bestätigt) verletzen.
