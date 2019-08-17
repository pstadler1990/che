# Vue.js basiertes CMS mit Static page generation

Grundidee: Vue.js Backend (Admin- / Redaktionsbereich) mit Login per JWT.
Dort werden die Seiten erstellt bzw. bearbeitet und die Einstellungen für die Webseite geändert.
Diese Daten werden als Dateien (flat cms) abgelegt (JSON-basiert).

Anschließend (und bei jeder Änderung) wird `che` aufgerufen, ein in Python geschriebenes Build-Skript (inkrementell), welches dann aus den JSON-Daten und den festgelegten HTML-Templates statische Webseiten mit intelligenter Verlinkung erzeugt.

Jede Seite erhält dabei eine eindeutige ID, welche in den Unterseiten referenziert werden kann (Verlinkungen). Bei einer Änderung des Seitentitels etc. wird aber die Referenz nicht aufgelöst, aber die referenzierenden Seiten müssen durch den intelligenten Builder neu gebaut werden (Klartext-URLs in Links etc).

## Templating
Für jede Webseite können beliebig viele Templates angelegt werden. Jeder Unterseite kann dann ein Template zugewiesen werden.
Die Templates basieren auf `Jinja2`.


## Wichtige Features

 - Markdown als Formatierungssprache im Frontend (-> Converter!)
 - Automatische Keyword- und Meta-Generierung durch NLTK aus dem Fließtext der Unterseiten (SEO!)
 - i18n
 - Automatische Auflösung von Seitenreferenzen und Assets (Bilder, etc.)
 - automatische robots.txt
 - automatische sitemap
 - automatische 404
 - Erzeugen von Navigation, Menus etc. aus Seiten
 - Footer, Header
 - Zusammenführen von Template-Flicken (partials)

## Metadaten

### Webseite allgemein
Für die Webseite werden folgende Daten gespeichert:

 - URL
 - Default-Sprache
 - Mehrsprachigkeit (i18n)
 - Datumsformat, Zeitzone etc.
 - Spezielle Build-Parameter etc.
 
_User und Passwörter etc. werden nicht beim Site Generator gespeichert - dieser nimmt nur die erzeugten
Daten an und erstellt daraus die Webseite (plain HTML + JS).
Für die Verwaltung der User und der Unterseiten wird ein (Vue.js)-Frontend verwendet._

### Unterseiten (pages)
Pages speichern folgende Metadaten:

 - Title (page title)
 - Slug  (URL, autogeneriert aus title mit automatischen Regeln, bzw. freie Einggabe)
 - ID (page identifier, eindeutig, ändert sich nach Erstellen nie mehr!)
 - Created (timestamp)
 - Modified (timestamp)
 - Version (für inkrementellen Builder)
 - template (Verweis auf Template-ID oder File)
 - hidden, private
 - Published, Draft
 - use_nlp (use natural language processing, z.B. autom. Keyword- und Satzextrahierung)

Die Metadaten werden pro Seite als `.json`-Datei gespeichert, während die eigentlichen Markdown-Daten als `<seite_id>.md` gespeichert sind.

## Build-Prozess

Dem Build-Prozess sollte eigene Middleware (plugins) zwischengeschaltet werden können. So könnte ein eigenes Template-Tag `galerie` eingeführt werden, welches dann durch eine Middleware in ein fertiges HTMl-Galerie-Konstrukt überführt werden kann.

### Ablauf

 1. Einlesen der Seiten (`<meta>.json` und `<seite>.md`) sowie der Einstellungen (`.json`)
 2. Der inkrementelle (intelligente) Builder baut nur Seiten, die sich verändert haben, oder bei denen sich Referenzen geändert haben. Dazu muss er über alle Dateien ein kleines Logbuch führen (json-basiert).


    {
	   'ueber_uns_3b4f8cc': {
	      'version': '02',
	      'last_modified': '207482221'
	   }
    }

 3. Laden der verwendeten Templates
 4. Laden der Metadaten pro Seite
 5. Einfügen der Metadaten in die Jinja-Env
 6. Middleware ausführen
 7. Automatische Keyword- und Metainformationen in Jinja-Env (SEO)
 8. Markdown-Converter -> Output in Jinja-Env
 9. Referenzen (Links, Bilder) auflösen (aus IDs werden Klartexturls z.B. /ueber-uns)
 10. Logbuch aktualisieren
 11. Nachdem alle Einzelseiten generiert wurden:
 12. Sitemap generieren
 13. Navigation und Menü generieren
 14. robots.txt generieren

