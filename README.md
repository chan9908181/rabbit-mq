# File System Scanner mit RabbitMQ Integration

Ein Python-Programm, das ein lokales Dateisystem rekursiv durchsucht und für jede gefundene Datei eine Nachricht mit Metadaten an eine RabbitMQ-Queue sendet.

Entwickelt als Lösung für die Coding-Challenge von **NorCom Information Technology GmbH**.

---

## Inhaltsverzeichnis

1. [Funktionen](#funktionen)
2. [Installation](#installation)
3. [Schnellstart](#schnellstart)
4. [Verwendung](#verwendung)
5. [Nachrichten überprüfen](#nachrichten-überprüfen)
6. [Konfiguration](#konfiguration)

---

## Funktionen

- Rekursive Verzeichnisdurchsuchung mit `os.walk()` (Python Standard Library)
- Memory-efficient: Konstanter Speicherverbrauch auch bei Millionen von Dateien
- Stabil bei großen Strukturen: Generator-basierte Iteration verhindert Speicherüberlauf
- Robuste Fehlerbehandlung: Berechtigungsfehler, fehlende Dateien, Netzwerkprobleme
- RabbitMQ-Verbindung mit Auto-Reconnect: Automatische Wiederverbindung bei Ausfall
- Connection Health Monitoring: Verhindert Timeouts bei mehrstündigen Scans
- Publisher Confirms: Garantierte Nachrichtenzustellung ohne Verlust
- Detaillierte Datei-Metadaten: Größe, Zeitstempel, optional SHA256-Hash
- Filterung nach Dateitypen: Nur bestimmte Extensions scannen
- Umfassendes Logging: Console + File Logging mit verschiedenen Levels
- Vollständig konfigurierbar: Alle Parameter über CLI steuerbar

---
## Installation

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

Was wird installiert:
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

RabbitMQ Zugang:
- AMQP Port: `localhost:5672` (für Programm)
- Management UI: `http://localhost:15672` (für Web-Interface)
- Username: `guest`
- Password: `guest`

---

## Schnellstart


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
cd ../utils
python read_messages.py --count 3

# 5. Aufräumen
rm -rf test_files
```

Erwartete Ausgabe:

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

## Verwendung

### file_scanner.py - Hauptprogramm

#### Syntax

```bash
python file_scanner.py --input-dirs directory_name [OPTIONS]
```

#### Argumente

| Argument        | Typ    | Standard | Pflicht | Beschreibung |
|-----------------|--------|----------|---------|--------------|
| `--input-dirs`  | String | -        | Ja      | Ein oder mehrere Verzeichnispfade, die gescannt werden sollen. Unterstützt mehrere Repositories (`repo1 repo2 repo3`). |

#### Beispiele

Mit allen Optionen:

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

Log-Datei: `file_scanner.log`
- Enthält detaillierte Logs für Debugging
- Wird automatisch erstellt
- Rotiert nicht automatisch (manuell löschen bei Bedarf)

---

## Nachrichten überprüfen

### read_messages.py - Nachrichten lesen

#### Syntax

```bash
python read_messages.py [OPTIONS]
```

#### Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `--queue` | String | `file_scan_queue` | Queue Name |
| `--count` | Integer | `10` | Anzahl zu lesender Nachrichten |
| `--acknowledge` | Flag | `False` | Nachrichten nach Lesen aus Queue entfernen |

#### Beispiele

Standard - 10 Nachrichten lesen (bleiben in Queue):

```bash
python read_messages.py
```

5 Nachrichten lesen:

```bash
python read_messages.py --count 5
```

Nachrichten lesen UND entfernen:

```bash
python read_messages.py --count 10 --acknowledge
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
# Login: guest / guest
# Navigation: Queues → file_scan_queue → Get messages
```

---

## Konfiguration

### RabbitMQ Konfiguration

docker-compose.yml anpassen:

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