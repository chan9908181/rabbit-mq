# File System Scanner mit RabbitMQ Integration

Ein robustes Python-Programm, das ein lokales Dateisystem rekursiv durchsucht und für jede gefundene Datei eine Nachricht mit Metadaten an eine RabbitMQ-Queue sendet.

Entwickelt als Lösung für die Coding-Challenge von **NorCom Information Technology GmbH**.

---

## 📋 Inhaltsverzeichnis

1. [Funktionen](#funktionen)
2. [Architektur](#architektur)
3. [Voraussetzungen](#voraussetzungen)
4. [Installation](#installation)
5. [Schnellstart](#schnellstart)
6. [Verwendung](#verwendung)
7. [Nachrichten überprüfen](#nachrichten-überprüfen)
8. [Konfiguration](#konfiguration)

---

## ✨ Funktionen

- ✅ **Rekursive Verzeichnisdurchsuchung** mit `os.walk()` (Python Standard Library)
- ✅ **Memory-efficient**: Konstanter Speicherverbrauch auch bei Millionen von Dateien
- ✅ **Stabil bei großen Strukturen**: Generator-basierte Iteration verhindert Speicherüberlauf
- ✅ **Robuste Fehlerbehandlung**: Berechtigungsfehler, fehlende Dateien, Netzwerkprobleme
- ✅ **RabbitMQ-Verbindung mit Auto-Reconnect**: Automatische Wiederverbindung bei Ausfall
- ✅ **Connection Health Monitoring**: Verhindert Timeouts bei mehrstündigen Scans
- ✅ **Publisher Confirms**: Garantierte Nachrichtenzustellung ohne Verlust
- ✅ **Detaillierte Datei-Metadaten**: Größe, Zeitstempel, optional SHA256-Hash
- ✅ **Filterung nach Dateitypen**: Nur bestimmte Extensions scannen
- ✅ **Umfassendes Logging**: Console + File Logging mit verschiedenen Levels
- ✅ **Vollständig konfigurierbar**: Alle Parameter über CLI steuerbar

---

## 🏗️ Architektur

### Modulare Struktur nach SOLID-Prinzipien

Das Programm folgt dem **Single Responsibility Principle** - jede Komponente hat genau eine Aufgabe:

```
┌─────────────────────────────────────────────────────────────┐
│                    file_scanner.py                          │
│              (Main Orchestrator / Entry Point)              │
│  - Koordiniert den Gesamtablauf                             │
│  - Dependency Injection                                     │
│  - CLI Argument Parsing                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
┌────────────┐ ┌────────────┐ ┌──────────────────┐
│ rabbitmq_  │ │  file_info │ │  directory_      │
│ client.py  │ │ _extractor │ │  scanner.py      │
│            │ │    .py     │ │                  │
│ - Connect  │ │ - Extract  │ │ - os.walk()      │
│ - Publish  │ │   metadata │ │ - Iterate files  │
│ - Reconnect│ │ - Hash     │ │ - Statistics     │
│ - Health   │ │ - Format   │ │ - Error handling │
└────────────┘ └────────────┘ └──────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │ logger_     │
              │ config.py   │
              │             │
              │ - Setup     │
              │ - Formatters│
              └─────────────┘
```

### Projektstruktur

```
file-scanner/
├── 📄 Core Application
│   ├── file_scanner.py              # Hauptprogramm (Orchestrator)
│   ├── rabbitmq_client.py           # RabbitMQ-Verbindung
│   ├── file_info_extractor.py       # Datei-Metadaten-Extraktion
│   ├── directory_scanner.py         # Verzeichnis-Traversierung
│   └── logger_config.py             # Logging-Konfiguration
│
├── 🔧 Utility Tools
│   ├── read_messages.py             # Nachrichten lesen (Batch)
│   ├── stress_test.py               # Performance-Test
│
├── ⚙️ Configuration
│   ├── requirements.txt             # Python Dependencies
│   ├── docker-compose.yml           # RabbitMQ Setup
│   └── .gitignore                   # Git Ignore Rules
│
└── 📚 Documentation
    ├── README.md                    # Diese Datei
    ├── STABILITY.md                 # Stabilitäts-Details
    └── QUICKSTART.md                # Schnellreferenz
```
---

## 📦 Voraussetzungen

### Software-Anforderungen

| Software | Version | Zweck |
|----------|---------|-------|
| **Python** | 3.7+ | Programmiersprache |
| **pip** | Latest | Package Manager |
| **Docker** | 20.10+ | Container Runtime |
| **Docker Compose** | 1.29+ | Multi-Container Orchestration |

### Installation prüfen

```bash
# Python Version prüfen
python --version
# Sollte zeigen: Python 3.7.x oder höher

# pip prüfen
pip --version

# Docker prüfen
docker --version
docker-compose --version
```

## 🚀 Installation

### Schritt 1: Projekt herunterladen

```bash
git clone https://github.com/YOUR_USERNAME/file-scanner-rabbitmq.git
cd file-scanner-rabbitmq
```

### Schritt 2: Python Dependencies installieren

```bash
# Virtual Environment erstellen (empfohlen)
python -m venv venv

# Virtual Environment aktivieren
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

**Was wird installiert:**
- `pika==1.3.2` - RabbitMQ Client Library

### Schritt 3: RabbitMQ starten

```bash
# RabbitMQ Container starten (im Hintergrund)
docker-compose up -d

# Status prüfen
docker-compose ps

# Sollte zeigen:
# NAME                    STATUS    PORTS
# file_scanner_rabbitmq   Up        0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
```

**RabbitMQ Zugang:**
- **AMQP Port**: `localhost:5672` (für Programm)
- **Management UI**: `http://localhost:15672` (für Web-Interface)
- **Username**: `guest`
- **Password**: `guest`

### Schritt 4: Installation verifizieren

```bash
# Testen ob alles funktioniert
cd src
python file_scanner.py --help

# Sollte die Hilfe anzeigen ohne Fehler
```

---

## ⚡ Schnellstart

### 5-Minuten-Test

```bash
# 1. RabbitMQ starten
docker-compose up -d

# 2. Test-Verzeichnis erstellen
mkdir -p test_files
echo "Test content 1" > test_files/test1.txt
echo "Test content 2" > test_files/test2.pdf
echo "Test content 3" > test_files/test3.jpg

# 3. Scanner ausführen
cd src
python file_scanner.py --input-dirs test_files

# 4. Nachrichten prüfen
cd ..
cd utils
python read_messages.py --count 3

# 5. Aufräumen
rm -rf test_files
```

**Erwartete Ausgabe:**
```
2025-12-02 13:50:56 - INFO - Starting scan of: /Users/ichan-yeong/IdeaProjects/rabbit-mq/test_files
2025-12-02 13:50:56 - INFO - Connecting to RabbitMQ at localhost:5672 (attempt 0/3)
2025-12-02 13:50:56 - INFO - Successfully connected to RabbitMQ
2025-12-02 13:50:56 - INFO - Starting scan of directory: /Users/ichan-yeong/IdeaProjects/rabbit-mq/test_files
2025-12-02 13:50:56 - DEBUG - Published: test1.txt
2025-12-02 13:50:56 - DEBUG - Published: test2.pdf
2025-12-02 13:50:56 - DEBUG - Published: test3.jpg
2025-12-02 13:50:56 - INFO - Scan completed. Processed: 3, Failed: 0, Skipped: 0
2025-12-02 13:50:56 - INFO - RabbitMQ connection closed
```

---

## 🎯 Verwendung

### file_scanner.py - Hauptprogramm

#### Syntax

```bash
python file_scanner.py --input-dirs directory_name [OPTIONS]
```

#### Argumente

| Argument        | Typ    | Standard | Pflicht | Beschreibung |
|-----------------|--------|----------|---------|--------------|
| `--input-dirs`  | String | -        | ✅ Ja   | Ein oder mehrere Verzeichnispfade, die gescannt werden sollen. Unterstützt mehrere Repositories, z. B.  (`repo1 repo2 repo3`). |


#### Optionale Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `--rabbitmq-host` | String | `localhost` | RabbitMQ Hostname oder IP |
| `--rabbitmq-port` | Integer | `5672` | RabbitMQ AMQP Port |
| `--rabbitmq-user` | String | `guest` | RabbitMQ Benutzername |
| `--rabbitmq-password` | String | `guest` | RabbitMQ Passwort |
| `--queue-name` | String | `file_scan_queue` | Name der RabbitMQ Queue |
| `--calculate-hash` | Flag | `False` | SHA256-Hash für Dateien <100MB berechnen |
| `--extensions` | List | Alle | Nur bestimmte Dateierweiterungen scannen |
| `--log-level` | Choice | `DEBUG` | Logging Level: DEBUG, INFO, WARNING, ERROR |

#### Beispiele

**Mit allen Optionen:**
```bash
python file_scanner.py --input-dirs test_files \
  --rabbitmq-host localhost \
  --rabbitmq-port 5672 \
  --rabbitmq-user guest \
  --rabbitmq-password guest \
  --queue-name my_files \
  --calculate-hash \
  --extensions .pdf .docx .xlsx \
  --log-level DEBUG
```


**Entfernter RabbitMQ Server:**
```bash
python file_scanner.py --input-dirs test_files \
  --rabbitmq-host 192.168.1.100 \
  --rabbitmq-user admin \
  --rabbitmq-password secret123
```


**Log-Datei:** `file_scanner.log`
- Enthält detaillierte Logs für Debugging
- Wird automatisch erstellt
- Rotiert nicht automatisch (manuell löschen bei Bedarf)

---

## 📨 Nachrichten überprüfen

### read_messages.py - Nachrichten lesen

#### Syntax

```bash
python read_messages.py [OPTIONS]
```

#### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `--host` | String | `localhost` | RabbitMQ Hostname |
| `--port` | Integer | `5672` | RabbitMQ Port |
| `--user` | String | `guest` | RabbitMQ Benutzername |
| `--password` | String | `guest` | RabbitMQ Passwort |
| `--queue` | String | `file_scan_queue` | Queue Name |
| `--count` | Integer | `10` | Anzahl zu lesender Nachrichten |
| `--acknowledge` | Flag | `False` | Nachrichten nach Lesen aus Queue entfernen |

#### Beispiele

**Standard - 10 Nachrichten lesen (bleiben in Queue):**
```bash
python read_messages.py
```

**5 Nachrichten lesen:**
```bash
python read_messages.py --count 5
```

**Nachrichten lesen UND entfernen:**
```bash
python read_messages.py --count 10 --acknowledge
```


**Von anderer Queue lesen:**
```bash
python read_messages.py --queue my_custom_queue --count 20
```

**Von entferntem Server:**
```bash
python read_messages.py \
  --host 192.168.1.100 \
  --user admin \
  --password secret123 \
  --count 5
```

#### Ausgabe

```
Connected to RabbitMQ at localhost:5672
Reading up to 10 messages from queue: file_scan_queue
================================================================================

Message 1:
--------------------------------------------------------------------------------
{
  "file_path": "/home/user/documents/report.pdf",
  "file_name": "report.pdf",
  "file_extension": ".pdf",
  "file_size_bytes": 524288,
  "file_size_human": "512.00 KB",
  "created_time": "2024-11-29T10:30:00.123456",
  "modified_time": "2024-11-29T12:45:00.654321",
  "accessed_time": "2024-11-29T14:20:00.987654",
  "is_symlink": false,
  "scan_timestamp": "2024-12-02T15:00:00.111222",
  "sha256_hash": "a3b2c1d4e5f6..."
}

Message 2:
--------------------------------------------------------------------------------
...

================================================================================
Total messages read: 10

Note: Messages were not removed from queue (use --acknowledge flag to remove)
```

### Alternative: Management Web UI

```bash
# Browser öffnen
open http://localhost:15672  # macOS
xdg-open http://localhost:15672  # Linux
start http://localhost:15672  # Windows

# Login: guest / guest
# Navigation: Queues → file_scan_queue → Get messages
```

## 🔧 Konfiguration

### RabbitMQ Konfiguration

**docker-compose.yml** anpassen:

```yaml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3.12-management
    container_name: file_scanner_rabbitmq
    ports:
      - "5672:5672"   # AMQP Port
      - "15672:15672" # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: myuser      # Hier ändern
      RABBITMQ_DEFAULT_PASS: mypassword  # Hier ändern
      # Optional: Memory Limits für große Scans
      RABBITMQ_VM_MEMORY_HIGH_WATERMARK: 0.8
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
```

Dann Programm mit neuen Credentials starten:
```bash
python file_scanner.py /path \
  --rabbitmq-user myuser \
  --rabbitmq-password mypassword
```
---

## 🤝 Support

Bei Fragen oder Problemen:

1. **Logs prüfen**: `file_scanner.log` und `docker-compose logs`
2. **GitHub Issues**: (falls öffentliches Repository)
3. **Email**: chan9908181@gmail.com (für NorCom-Bewerbung)

---

## 📄 Lizenz

Dieses Projekt wurde als Coding-Challenge für **NorCom Information Technology GmbH** erstellt.

**Entwickler:** Chan-Young Lee  
**Datum:** Dezember 2025
**Kontakt:** chan9908181@gmail.com

---
