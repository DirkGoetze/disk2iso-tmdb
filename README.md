# disk2iso TMDB Provider Module

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/github/v/release/DirkGoetze/disk2iso-tmdb)](https://github.com/DirkGoetze/disk2iso-tmdb/releases)

TMDB (The Movie Database) Metadata Provider für [disk2iso](https://github.com/DirkGoetze/disk2iso) - liefert Film-/TV-Metadaten für DVD und Blu-ray Discs.

## 🚀 Features

- **Film-Metadaten** - Titel, Beschreibung, Release-Jahr, Genre
- **TV-Serien Support** - Episoden-Informationen, Staffeln
- **Cover-Art** - Poster-Thumbnails für Web-UI
- **TMDB API v3** - Offizielle API-Integration
- **Cache-System** - Automatisches Caching für 30 Tage
- **Multi-Language** - Unterstützt 4 Sprachen (DE, EN, ES, FR)
- **Web-UI Integration** - Modal-Dialog für Metadata-Auswahl
- **Provider-Framework** - Registriert sich beim disk2iso Metadata-Framework

## 📋 Voraussetzungen

- **disk2iso** >= v1.2.0 mit libmetadata.sh ([Installation](https://github.com/DirkGoetze/disk2iso))
- **curl** - Für API-Requests
- **jq** - Für JSON-Parsing
- **TMDB API Key** - Kostenlos bei [themoviedb.org](https://www.themoviedb.org/settings/api)

## 📦 Installation

### Automatisch (empfohlen)

```bash
# Download neueste Version
curl -L https://github.com/DirkGoetze/disk2iso-tmdb/releases/latest/download/tmdb-module.zip -o /tmp/tmdb.zip

# Entpacken nach disk2iso
cd /opt/disk2iso
sudo unzip /tmp/tmdb.zip

# Service neu starten
sudo systemctl restart disk2iso
sudo systemctl restart disk2iso-web
```

### Manuell

1. Download [neueste Release](https://github.com/DirkGoetze/disk2iso-tmdb/releases/latest)
2. Entpacke nach `/opt/disk2iso/`
3. Setze Berechtigungen: `sudo chown -R root:root /opt/disk2iso/`
4. Restart Services: `sudo systemctl restart disk2iso disk2iso-web`

### Via Web-UI (ab v1.3.0)

1. Öffne disk2iso Web-UI
2. Gehe zu **Einstellungen → Module → Metadata Provider**
3. Klicke auf **TMDB → Installieren**

## ⚙️ Konfiguration

### 1. TMDB API Key erstellen

1. Registriere dich bei [themoviedb.org](https://www.themoviedb.org/signup)
2. Gehe zu [API Settings](https://www.themoviedb.org/settings/api)
3. Beantrage einen API Key (Type: Developer)
4. Kopiere deinen API Key (v3 Auth)

### 2. API Key in disk2iso eintragen

```bash
# Bearbeite die Konfiguration
sudo nano /opt/disk2iso/conf/libtmdb.ini

# Trage deinen API Key ein:
[settings]
api_key = dein_api_key_hier
```

Oder via Web-UI:
1. Öffne http://your-server:5000
2. **Einstellungen → Metadata Provider → TMDB**
3. Trage API Key ein → **Speichern**

### 3. Provider aktivieren

```ini
[settings]
active = true
```

### Manifest-Datei

`conf/libtmdb.ini`:

```ini
[module]
name=tmdb
version=1.2.0
description=TMDB Metadata Provider für DVDs und Blu-rays

[api]
base_url=https://api.themoviedb.org/3
image_base_url=https://image.tmdb.org/t/p/w500
language=de-DE
timeout=10

[settings]
active=true
cache_enabled=true
cache_duration_days=30
api_key=
```

## 🔧 Verwendung

### Automatisch

Der Provider wird automatisch vom Metadata-Framework verwendet, wenn:
- Eine DVD oder Blu-ray eingelegt wird
- libmetadata.sh aktiviert ist
- TMDB als Video-Provider konfiguriert ist

```bash
# Status prüfen
sudo systemctl status disk2iso

# Provider-Registrierung prüfen
sudo journalctl -u disk2iso -f | grep TMDB
```

### Via Web-UI

1. Öffne http://your-server:5000
2. Lege DVD/Blu-ray ein
3. **Metadata-Dialog** öffnet sich automatisch
4. Wähle Film/Serie aus TMDB-Suchergebnissen
5. Metadaten werden automatisch gespeichert

### Manuell (API)

```bash
# Suche nach Film
curl "http://localhost:5000/api/metadata/query?provider=tmdb&title=Inception&year=2010"

# Response:
{
  "success": true,
  "provider": "tmdb",
  "results": [
    {
      "id": "27205",
      "title": "Inception",
      "release_date": "2010-07-16",
      "overview": "...",
      "poster_path": "/..."
    }
  ]
}
```

## 📊 Ausgabe-Struktur

```
/media/iso/metadata/tmdb/
├── cache/
│   ├── inception_2010.nfo          # Cached Query-Results
│   └── avatar_2009.nfo
├── covers/
│   ├── inception_2010.jpg          # Poster-Thumbnails
│   └── avatar_2009.jpg
└── metadata.json                   # Provider-Statistiken
```

## 🔌 Provider-API

### Registrierung

TMDB registriert sich automatisch beim Metadata-Framework:

```bash
metadata_register_provider "tmdb" "dvd-video,bd-video"
```

### Implementierte Funktionen

- `tmdb_query(title, year)` - Suche nach Film/Serie
- `tmdb_parse(json)` - Parse API-Response
- `tmdb_apply(metadata, target)` - Speichere Metadaten
- `tmdb_get_cover(poster_path)` - Download Cover-Art

## 🌐 Unterstützte Disc-Typen

- **dvd-video** - Video-DVDs
- **bd-video** - Blu-ray Discs

## 🔑 API-Endpunkte

### TMDB API v3

- **Search Movie**: `GET /search/movie?query={title}&year={year}`
- **Search TV**: `GET /search/tv?query={title}&year={year}`
- **Movie Details**: `GET /movie/{id}`
- **TV Details**: `GET /tv/{id}`
- **Images**: `GET https://image.tmdb.org/t/p/w500/{poster_path}`

**Dokumentation**: [TMDB API Docs](https://developers.themoviedb.org/3)

## 🧪 Entwicklung

### Struktur

```
disk2iso-tmdb/
├── conf/
│   └── libtmdb.ini             # Provider-Manifest
├── doc/
│   ├── TMDB-API-Key.md         # API-Key Anleitung
│   └── TMDB-Integration.md     # Integration-Doku
├── lang/
│   ├── libtmdb.de              # Deutsche Übersetzung
│   ├── libtmdb.en              # Englische Übersetzung
│   ├── libtmdb.es              # Spanische Übersetzung
│   └── libtmdb.fr              # Französische Übersetzung
└── lib/
    └── libtmdb.sh              # Haupt-Bibliothek
```

### Lokale Tests

```bash
# In disk2iso-Umgebung testen
cd /opt/disk2iso
source lib/libmetadata.sh
source lib/libtmdb.sh

# Abhängigkeiten prüfen
tmdb_check_dependencies

# Test-Query
tmdb_query "Inception" "2010"
```

## 📝 Changelog

Siehe [CHANGELOG.md](CHANGELOG.md) für alle Änderungen.

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit deine Änderungen (`git commit -m 'Add amazing feature'`)
4. Push zum Branch (`git push origin feature/amazing-feature`)
5. Öffne einen Pull Request

## 📜 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

## 🔗 Links

- [disk2iso Core](https://github.com/DirkGoetze/disk2iso)
- [TMDB API](https://www.themoviedb.org/documentation/api)
- [libmetadata Framework](https://github.com/DirkGoetze/disk2iso/blob/main/lib/libmetadata.sh)
- [DVD Module](https://github.com/DirkGoetze/disk2iso-dvd) (empfohlen)
- [Blu-ray Module](https://github.com/DirkGoetze/disk2iso-bluray) (empfohlen)

## ⚠️ Wichtige Hinweise

- **API Key erforderlich**: Ohne TMDB API Key funktioniert der Provider nicht
- **Rate Limits**: TMDB API hat Rate Limits (40 Requests/10 Sekunden)
- **Cache nutzen**: Cache-System reduziert API-Requests erheblich
- **Kostenlos**: TMDB API ist für nicht-kommerzielle Nutzung kostenlos

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/DirkGoetze/disk2iso-tmdb/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/DirkGoetze/disk2iso-tmdb/discussions)
- **TMDB API Support**: [TMDB Forums](https://www.themoviedb.org/talk)
- **Core Projekt**: [disk2iso](https://github.com/DirkGoetze/disk2iso)
