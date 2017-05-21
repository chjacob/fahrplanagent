# Fahrplan-Agent
Fahrplan-Agent: Benachrichtigungen für DB Fahrplanänderungen

Mein Fahrplan-Agent ist ein Skript, das ich geschrieben habe weil mich die 
[DB Streckenagent-App](https://www.bahn.de/p/view/service/buchung/mobil/streckenagent-app.shtml)
nur über Verspätungen und nicht über Änderungen des Fahrplans informiert.

Der Fahrplan-Agent verwendet die [DB-Opendata](http://data.deutschebahn.com/)
[Fahrplan-API](http://data.deutschebahn.com/dataset/api-fahrplan) um den Fahrplan
für einen Tag abzufragen und mit den "normalen" Daten für gegebene verbindungen zu
vergleichen. Änderungen gegenüber dem Normal-Fahrplan werden so erkannt und können
als E-Mail-Benachrichtigung verschickt werden.

Ich habe den Fahrplan-Agent als Cronjob angelegt, der für mich jeden Abend die
Fahrplan-Ânderungen am nächsten Tag abfragt und mich benachrichtigt.

Abgefragt werden:
- Änderung der Abfahrtszeit
- Änderung der Ankunftszeit
- Änderung des Abfahrtsgleises
- Ausfall des Halts am Zielbahnhof
- Ausfall des gesamten Zugs

## Verwendung

In `fahrplanagent-mailer.py`
- in `trains` die gewünschten Verbindungen anlegen
- ggf. in `mailto` eine E-Mail-Adresse angeben (ohne E-Mail-Adresse wird
  das Ergebnis direkt ausgegeben)

Standardmäßig wird die Fahrplan-Free-API verwendet, bei welcher die Anzahl der
Abfragen begrenzt ist. Um die unbegrenzte API zu verwenden, ist eine Registrierung
erforderlich. Das Access-Token kann in einer Datei `fahrplanapi-accesstoken.txt`
hinterlegt werden im Verzeichnis des Skripts hinterlegt werden und wird dann
verwendet.

E-Mail-Versand erfolgt über Aufruf von `mail` und wird nur unter Linux u.ä. mit
konfiguriertem Mail-System funktionieren.
