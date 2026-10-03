<p align="center"><img src="assets/banner.svg" alt="SalsaNOW Session Guide und Remote AI Starter für Windows, macOS und Linux" width="1200"></p>

# SalsaNOW Session Guide & Remote AI Starter

[![Automatische Prüfungen](https://github.com/Henner4746/salsanow-session-guide/actions/workflows/checks.yml/badge.svg)](https://github.com/Henner4746/salsanow-session-guide/actions/workflows/checks.yml)
[![MIT-Lizenz](https://img.shields.io/badge/Lizenz-MIT-a4e7cb)](LICENSE)

Eine praktische Community-Anleitung für SalsaNOW / GeForce NOW und ein Starter, mit dem du deinen eigenen LM-Studio-Server auf **Windows, macOS oder Linux** nutzen kannst.

**[English](README.md)** · [Sitzungsprobleme und Lösungen](docs/session-guide.md) · [API-Anleitung](docs/remote-api.md)

## Schnellstart

1. Repository über **Code → Download ZIP** herunterladen und entpacken.
2. Falls nötig, **Python ab Version 3.10** von [python.org](https://www.python.org/downloads/) installieren.
3. Passenden Starter öffnen:

| Betriebssystem | Start |
|---|---|
| Windows | `start-windows.cmd` doppelklicken |
| macOS | Im Terminal: `sh ./start-macos.command` |
| Linux | Im Terminal: `sh ./start-linux.sh` |

Du brauchst nur **deinen Endpoint und deinen LM-Studio-API-Key**. Ein Endpoint wie `https://api.example.com` wird automatisch um `/v1` ergänzt. Der Schlüssel wird verdeckt eingegeben und nicht auf der Festplatte gespeichert.

Das Programm prüft den Anmeldeschutz und den Zugriff, liest die Modellliste und öffnet ein neues Terminal mit den passenden Umgebungsvariablen. Es wählt das erste Modell aus, dessen Name es nicht als Embedding-Modell ausweist. Das ist eine Hilfe, keine Garantie für die Fähigkeiten jedes Modells. Mit `--model MODELL_ID` kannst du ein anderes angeben.

Weitere Möglichkeiten:

```console
python remote_ai.py --check
python remote_ai.py --chat
python remote_ai.py --chat --max-tokens 2048
```

`--check` prüft den Zugang ohne Textgenerierung. `--chat` bietet einen kleinen Chat zum Testen. Standardmäßig öffnet das Programm ein vorkonfiguriertes Terminal. Darin gestartete Programme können die Zugangsdaten aus der Umgebung lesen. Beim Schließen dieser Sitzung enden auch deren Umgebungsvariablen; dein ursprüngliches Terminal und deine Profile werden nicht verändert.

Es werden keine fremden Programme installiert und keine Einstellungen aller Chat-Apps geändert. Programme, die diese Umgebungsvariablen nicht unterstützen, brauchen ihre eigene Konfiguration.

## Voraussetzungen auf dem Server

Der Host muss bereits laufen: Modell geladen, LM-Studio-Server gestartet, Authentifizierung eingeschaltet und HTTPS-Tunnel verbunden. Der **Cloudflare-Verbindungstoken ist nicht der LM-Studio-API-Key**.

In einer Cloud-Sitzung ohne Administratorrechte läuft der Tunnel als normaler Prozess. Die hier enthaltene Dokumentation korrigiert deshalb die früher verwendete Windows-Service-Anweisung.

## Stand und Mitarbeit

Eine [Beispielsitzung](docs/walkthrough.md) zeigt die Eingabe und den Start eines Clients. Die Anzeige ist ein gekennzeichnetes Beispiel, kein Screenshot eines echten Benutzerkontos.

Die Ausgangsdokumente berichten erfolgreiche API-Tests. Das neuere Handoff hat bei Widersprüchen Vorrang. Die Persistenz nach einem vollständigen Sitzungswechsel und die Langzeitstabilität sind weiterhin getrennt zu prüfen. Details: [Teststatus](docs/verification.md).

Fehler und Verbesserungen gerne als Issue melden. Bitte keine Schlüssel, persönlichen Domains, vollständigen Logs oder Einstellungen mit Geheimnissen posten. Siehe [CONTRIBUTING.md](CONTRIBUTING.md).

Unabhängiges Community-Projekt; keine offizielle Unterstützung oder öffentliche API. [MIT-Lizenz](LICENSE).
