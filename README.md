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
9. [Tests](#tests)
10. [Fehlerbehebung](#fehlerbehebung)

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
python file_scanner.py test_files

# 4. Nachrichten prüfen
python read_messages.py --count 3

# 5. Aufräumen
rm -rf test_files
```

**Erwartete Ausgabe:**
```
2024-12-02 10:00:00 - INFO - Connecting to RabbitMQ at localhost:5672
2024-12-02 10:00:00 - INFO - Successfully connected to RabbitMQ
2024-12-02 10:00:00 - INFO - Starting scan of directory: test_files
2024-12-02 10:00:01 - INFO - Scan completed. Processed: 3, Failed: 0, Skipped: 0
```

---

## 🎯 Verwendung

### file_scanner.py - Hauptprogramm

#### Syntax

```bash
python file_scanner.py <DIRECTORY> [OPTIONS]
```

#### Argumente

| Argument | Typ | Standard | Pflicht | Beschreibung |
|----------|-----|----------|---------|--------------|
| `directory` | String | - | ✅ Ja | Pfad zum zu scannenden Verzeichnis |

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
| `--log-level` | Choice | `INFO` | Logging Level: DEBUG, INFO, WARNING, ERROR |

#### Beispiele

**Basis-Scan:**
```bash
python file_scanner.py ~/Documents
```

**Mit allen Optionen:**
```bash
python file_scanner.py /data/archive \
  --rabbitmq-host localhost \
  --rabbitmq-port 5672 \
  --rabbitmq-user guest \
  --rabbitmq-password guest \
  --queue-name my_files \
  --calculate-hash \
  --extensions .pdf .docx .xlsx \
  --log-level DEBUG
```

**Nur bestimmte Dateitypen:**
```bash
# Nur PDF und Word-Dokumente
python file_scanner.py ~/Documents --extensions .pdf .docx

# Nur Bilder
python file_scanner.py ~/Pictures --extensions .jpg .png .gif .jpeg

# Nur Text-Dateien
python file_scanner.py ~/Code --extensions .py .java .cpp .h
```

**Mit Hash-Berechnung:**
```bash
python file_scanner.py ~/important_files --calculate-hash
```

**Debug-Modus:**
```bash
python file_scanner.py ~/test --log-level DEBUG
```

**Entfernter RabbitMQ Server:**
```bash
python file_scanner.py /data \
  --rabbitmq-host 192.168.1.100 \
  --rabbitmq-user admin \
  --rabbitmq-password secret123
```

#### Ausgabe

**Console Output:**
```
2024-12-02 10:00:00 - INFO - Connecting to RabbitMQ at localhost:5672
2024-12-02 10:00:00 - INFO - Successfully connected to RabbitMQ
2024-12-02 10:00:00 - INFO - Starting scan of directory: /home/user/documents
2024-12-02 10:00:15 - INFO - Progress: 100 processed, 0 failed, 5 skipped
2024-12-02 10:00:30 - INFO - Progress: 200 processed, 0 failed, 8 skipped
2024-12-02 10:01:00 - INFO - Scan completed. Processed: 347, Failed: 0, Skipped: 12
2024-12-02 10:01:00 - INFO - RabbitMQ connection closed
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

**Alle Nachrichten konsumieren:**
```bash
python read_messages.py --count 1000 --acknowledge
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

### Alternative: Live Consumer (Echtzeit)

```bash
# Zeigt Nachrichten in Echtzeit an
python live_consumer.py

# Mit Options
python live_consumer.py --queue file_scan_queue --acknowledge
```

---

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

### Logging Konfiguration

Im Code anpassen (`logger_config.py`):

```python
# Log-Level für Console
console_handler.setLevel(logging.INFO)  # Ändern zu DEBUG, WARNING, etc.

# Log-Level für Datei
file_handler.setLevel(logging.DEBUG)  # Immer alles loggen

# Log-Datei Name
file_handler = logging.FileHandler('custom_name.log')
```

---

## 🧪 Tests

### Manueller Test

```bash
# Test-Dateien erstellen
mkdir -p test_files
for i in {1..100}; do
  echo "Test content $i" > test_files/file_$i.txt
done

# Scanner ausführen
python file_scanner.py test_files

# Ergebnisse prüfen
python read_messages.py --count 100

# Aufräumen
rm -rf test_files
```

### Stress-Test (Große Verzeichnisse)

```bash
# Erstellt ~10,000 Dateien und scannt sie
python stress_test.py
```

**Was der Stress-Test macht:**
1. Erstellt automatisch große Verzeichnisstruktur (10k+ Dateien)
2. Führt Scanner aus
3. Misst Performance (Dateien/Sekunde)
4. Prüft Stabilität
5. Räumt automatisch auf

**Erwartetes Ergebnis:**
```
Created 10000 files in 15.23 seconds
Scan completed in 25.67 seconds
Throughput: 389.54 files/second
✅ STRESS TEST PASSED
```

### Unit-Tests

```bash
# Einzelne Module testen
python test_file_info_extractor.py
```

### Integration Test

```bash
# Vollständiger Workflow-Test
docker-compose up -d
python file_scanner.py test_files --log-level DEBUG
python read_messages.py --count 10
docker-compose down
```

---

## 🐛 Fehlerbehebung

### Problem: "Connection refused" / "Could not connect to RabbitMQ"

**Ursache:** RabbitMQ läuft nicht

**Lösung:**
```bash
# Status prüfen
docker-compose ps

# Wenn nicht running:
docker-compose up -d

# Logs prüfen
docker-compose logs rabbitmq

# Warten bis bereit (dauert ~10 Sekunden)
docker-compose logs -f rabbitmq | grep "Server startup complete"
```

### Problem: "Permission denied" beim Scannen

**Ursache:** Keine Leserechte für Dateien/Verzeichnisse

**Lösung:**
```bash
# Option 1: Mit sudo ausführen (Vorsicht!)
sudo python file_scanner.py /root

# Option 2: Nur zugängliche Verzeichnisse scannen
python file_scanner.py ~/Documents  # Statt /root
```

### Problem: "ModuleNotFoundError: No module named 'pika'"

**Ursache:** Dependencies nicht installiert

**Lösung:**
```bash
# Virtual Environment aktivieren (falls verwendet)
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Dependencies neu installieren
pip install -r requirements.txt

# Verifizieren
pip list | grep pika
```

### Problem: Scanner hängt / keine Ausgabe

**Ursache:** Sehr große Dateien oder langsames Dateisystem

**Lösung:**
```bash
# Debug-Modus aktivieren für mehr Details
python file_scanner.py /path --log-level DEBUG

# Hash-Berechnung deaktivieren (falls aktiv)
python file_scanner.py /path  # Ohne --calculate-hash

# Kleineres Verzeichnis testen
python file_scanner.py ~/Documents/subset
```

### Problem: RabbitMQ Management UI nicht erreichbar

**Ursache:** Port nicht exposed oder Container nicht running

**Lösung:**
```bash
# Container Status prüfen
docker-compose ps

# Ports prüfen
docker port file_scanner_rabbitmq

# Container neu starten
docker-compose restart rabbitmq

# Browser Cache leeren und neu versuchen
# Chrome: Ctrl+Shift+R
# Firefox: Ctrl+F5
```

### Problem: Zu viele Nachrichten in Queue

**Ursache:** Messages werden nicht konsumiert

**Lösung:**
```bash
# Option 1: Alle Nachrichten lesen und löschen
python read_messages.py --count 10000 --acknowledge

# Option 2: Queue über Web UI purgen
# http://localhost:15672 → Queues → file_scan_queue → Purge Messages

# Option 3: Queue löschen und neu erstellen
docker exec file_scanner_rabbitmq rabbitmqctl delete_queue file_scan_queue
docker exec file_scanner_rabbitmq rabbitmqctl add_queue file_scan_queue
```

### Problem: Zu wenig Speicherplatz

**Ursache:** RabbitMQ speichert Messages auf Disk

**Lösung:**
```bash
# Docker Volumes prüfen
docker system df

# RabbitMQ Daten löschen (VORSICHT: Alle Messages gehen verloren!)
docker-compose down -v

# Neu starten
docker-compose up -d
```

### Logs für Debugging

**Scanner Logs:**
```bash
# Console Output ansehen
python file_scanner.py /path --log-level DEBUG

# Log-Datei ansehen
cat file_scanner.log
tail -f file_scanner.log  # Live-Monitoring
```

**RabbitMQ Logs:**
```bash
# Live logs
docker-compose logs -f rabbitmq

# Letzte 100 Zeilen
docker-compose logs --tail=100 rabbitmq
```

---

## 📊 Nachrichtenformat

Jede gesendete Nachricht enthält folgende Felder:

```json
{
  "file_path": "/absolute/path/to/file.txt",
  "file_name": "file.txt",
  "file_extension": ".txt",
  "file_size_bytes": 1024,
  "file_size_human": "1.00 KB",
  "created_time": "2024-11-29T10:30:00.123456",
  "modified_time": "2024-11-29T12:45:00.654321",
  "accessed_time": "2024-11-29T14:20:00.987654",
  "is_symlink": false,
  "scan_timestamp": "2024-12-02T15:00:00.111222",
  "sha256_hash": "a3b2c1d4..."  // Nur wenn --calculate-hash verwendet
}
```

---

## 🚦 Performance

### Erwartete Leistung

| Szenario | Dateien/Sekunde | Notizen |
|----------|-----------------|---------|
| Kleine Dateien (<1MB) | 500-1000 | SSD, kein Hash |
| Mittlere Dateien (1-10MB) | 100-500 | SSD, kein Hash |
| Mit Hash-Berechnung | 50-200 | Abhängig von Dateigröße |
| Netzwerk-Filesystem | 10-100 | Stark abhängig von Latenz |

### Optimierung für große Scans

```bash
# Ohne Hash für maximale Geschwindigkeit
python file_scanner.py /large/dir

# Nur bestimmte Extensions für weniger Dateien
python file_scanner.py /large/dir --extensions .pdf .docx

# Debug-Logs deaktivieren
python file_scanner.py /large/dir --log-level WARNING
```

---

## 📚 Weitere Ressourcen

- **STABILITY.md** - Detaillierte Erklärung der Stabilitäts-Features
- **QUICKSTART.md** - Schnellreferenz-Guide
- **Code-Kommentare** - Inline-Dokumentation im Source Code

---

## 🤝 Support

Bei Fragen oder Problemen:

1. **Logs prüfen**: `file_scanner.log` und `docker-compose logs`
2. **README durchlesen**: Fehlerbehebung-Sektion
3. **GitHub Issues**: (falls öffentliches Repository)
4. **Email**: eneida.nordbakk@norcom.de (für NorCom-Bewerbung)

---

## 📄 Lizenz

Dieses Projekt wurde als Coding-Challenge für **NorCom Information Technology GmbH** erstellt.

**Entwickler:** [Ihr Name]  
**Datum:** Dezember 2024  
**Kontakt:** [Ihre Email]

---

## ✅ Checkliste vor Einreichung

- [ ] Alle Dateien vorhanden (11 Python-Dateien + Config)
- [ ] `requirements.txt` installiert
- [ ] Docker & Docker Compose installiert
- [ ] RabbitMQ startet erfolgreich
- [ ] Scanner läuft ohne Fehler
- [ ] Nachrichten können gelesen werden
- [ ] Tests durchgeführt
- [ ] README vollständig gelesen
- [ ] Git Repository erstellt (falls gewünscht)

---

**Viel Erfolg mit der Bewerbung bei NorCom! 🚀**