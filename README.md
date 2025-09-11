# Wattwallet - Home Assistant Integration

[![GitHub release](https://img.shields.io/github/release/biclighter81/wattwallet-ha.svg)](https://github.com/biclighter81/wattwallet-ha/releases)
[![GitHub issues](https://img.shields.io/github/issues/biclighter81/wattwallet-ha.svg)](https://github.com/biclighter81/wattwallet-ha/issues)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-blue.svg)](https://www.home-assistant.io/)

Eine Home Assistant Integration für Wattwallet, die es ermöglicht, Energieverbrauchsdaten von verschiedenen Stromzählern automatisch an den Wattwallet-Service zu übertragen.

## 📋 Überblick

Diese Integration sammelt Energieverbrauchsdaten von konfigurierten Sensoren in Home Assistant und sendet diese in regelmäßigen Abständen an eine konfigurierte Wattwallet API. Die Integration wurde speziell für die Überwachung von Energieverbrauch in Mehrfamilienhäusern entwickelt.

## ✨ Features

- **Automatische Datenübertragung**: Regelmäßiger Upload von Energiedaten an Wattwallet
- **Flexibel konfigurierbar**: Unterstützung für mehrere Stromzähler-Sensoren
- **Benutzerfreundliche Konfiguration**: Grafische Konfiguration über die Home Assistant UI
- **Anpassbare Intervalle**: Konfigurierbare Upload-Intervalle (Standard: 5 Minuten)
- **Status-Monitoring**: HTTP-Status-Sensor zur Überwachung der Übertragungsqualität
- **Sichere Authentifizierung**: Bearer Token-basierte API-Authentifizierung
- **Fehlerbehandlung**: Robuste Fehlerbehandlung mit detailliertem Logging

## 🛠 Voraussetzungen

- Home Assistant 2023.1.0 oder höher
- Python 3.10 oder höher
- Gültiger Wattwallet API-Token
- Konfigurierte Energiesensoren mit folgenden Anforderungen:
  - `state_class`: `total` oder `total_increasing`
  - `unit_of_measurement`: `Wh` oder `kWh`
  - `device_class`: `energy`

## 📦 Installation

### Installation über HACS (Empfohlen)

1. Stellen Sie sicher, dass [HACS](https://hacs.xyz) in Ihrem Home Assistant installiert ist
2. Klicken Sie auf den folgenden Button, um das Repository zu HACS hinzuzufügen:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=wattwallet-ha&owner=biclighter81&category=Integration)

3. Alternativ können Sie das Repository manuell hinzufügen:
   - Öffnen Sie HACS in Home Assistant
   - Gehen Sie zu "Integrationen"
   - Klicken Sie auf die drei Punkte (⋮) oben rechts
   - Wählen Sie "Benutzerdefinierte Repositories"
   - Fügen Sie `https://github.com/biclighter81/wattwallet-ha` als Repository-URL hinzu
   - Wählen Sie "Integration" als Kategorie
   - Klicken Sie auf "Hinzufügen"

4. Suchen Sie nach "wattwallet" und installieren Sie die Integration
5. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie die neueste Version von der [Releases-Seite](https://github.com/biclighter81/wattwallet-ha/releases) herunter
2. Extrahieren Sie das Archiv
3. Kopieren Sie den Ordner `custom_components/wattwallet` in Ihr `custom_components` Verzeichnis
4. Starten Sie Home Assistant neu

## ⚙️ Konfiguration

### Initial Setup

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **Integration hinzufügen**
3. Suchen Sie nach "Wattwallet" und wählen Sie die Integration aus
4. Füllen Sie das Konfigurationsformular aus:

#### Konfigurationsparameter

| Parameter | Typ | Beschreibung | Erforderlich | Standard |
|-----------|-----|--------------|-------------|----------|
| **Name** | Text | Name für diese Integration | ✅ | wattwallet |
| **Stromzähler** | Entitäten | Liste der Energiesensor-Entitäten | ✅ | - |
| **Intervall** | Zahl | Upload-Intervall in Sekunden | ✅ | 300 |
| **API Token** | Text | Wattwallet API-Authentifizierungstoken | ✅ | - |
| **Target URL** | Text | Wattwallet API-Endpunkt-URL | ✅ | - |

### Sensor-Anforderungen

Die ausgewählten Energiesensoren müssen folgende Eigenschaften haben:

```yaml
sensor:
  - platform: integration
    name: "Mein Energiezähler"
    source: sensor.power_meter
    unit_time: h
    round: 2
    method: trapezoidal
```

**Wichtige Attribute:**

- `state_class`: `total` oder `total_increasing`
- `unit_of_measurement`: `Wh` oder `kWh`  
- `device_class`: `energy`

### Beispielkonfiguration

```yaml
# Beispiel für Template-Sensoren mit Integration
sensor:
  # Power-Sensoren (kW)
  - platform: template
    sensors:
      building_a_consumption:
        friendly_name: "Building A Consumption"
        unit_of_measurement: "kW"
        value_template: "{{ 2.5 }}"

  # Integration zu Energiesensoren (kWh)
  - platform: integration
    name: "Building A Energy"
    source: sensor.building_a_consumption
    unit_time: h
    round: 2
    method: trapezoidal

# Homeassistant Customization für device_class
homeassistant:
  customize:
    sensor.building_a_energy:
      device_class: energy
```

## 📊 Datenformat

Die Integration sendet Daten im folgenden JSON-Format an die Wattwallet API:

```json
{
  "data": [
    {
      "entity_id": "sensor.building_a_energy",
      "state": "1234.56",
      "attributes": {
        "unit_of_measurement": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "friendly_name": "Building A Energy"
      }
    }
  ]
}
```

## 🔍 Monitoring & Debugging

### HTTP Status Sensor

Die Integration erstellt automatisch einen Status-Sensor:

- **Entity ID**: `sensor.wattwallet_http_status`
- **State**: HTTP-Statuscode der letzten Anfrage (200, 401, 500, etc.)
- **Attribut**: `message` mit Erfolgs- oder Fehlermeldung

### Logging

Aktivieren Sie Debug-Logging für detaillierte Informationen:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.wattwallet: debug
```

### Häufige Probleme

| Problem | Ursache | Lösung |
|---------|---------|--------|
| HTTP 401 | Ungültiger API-Token | Überprüfen Sie den API-Token |
| HTTP 404 | Falsche Target URL | Überprüfen Sie die Endpunkt-URL |
| Sensor-Validierungsfehler | Falsche Sensor-Attribute | Stellen Sie sicher, dass `state_class` und `unit_of_measurement` korrekt sind |
| Keine Daten gesendet | Sensoren liefern keine Werte | Überprüfen Sie, ob die Sensoren aktiv sind |

## 🔄 Updates & Optionen

### Konfiguration ändern

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Finden Sie die Wattwallet-Integration
3. Klicken Sie auf **Konfigurieren**
4. Ändern Sie die gewünschten Parameter
5. Die Änderungen werden automatisch übernommen

### Automatische Updates

Bei der Installation über HACS werden Updates automatisch erkannt und können mit einem Klick installiert werden.

## 🏗 Entwicklung

### Projektstruktur

```
custom_components/wattwallet/
├── __init__.py          # Integration Setup
├── config_flow.py       # Konfigurationsflow
├── sensor.py           # Sensor-Implementierung
└── manifest.json       # Manifest-Datei
```

### Entwicklungsumgebung

```bash
# Repository klonen
git clone https://github.com/biclighter81/wattwallet-ha.git

# Development-Links erstellen
ln -s $(pwd)/custom_components/wattwallet /path/to/homeassistant/custom_components/
```

### Testing

Die Integration wurde getestet mit:

- Home Assistant 2023.1+
- Python 3.10+
- Verschiedene Sensor-Konfigurationen
- Unterschiedliche API-Endpunkte

## 🤝 Beitragen

Beiträge sind herzlich willkommen! Bitte befolgen Sie diese Schritte:

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committen Sie Ihre Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Pushen Sie den Branch (`git push origin feature/AmazingFeature`)
5. Öffnen Sie einen Pull Request

### Code-Standards

- Befolgen Sie PEP 8
- Verwenden Sie Type Hints
- Schreiben Sie aussagekräftige Commit-Messages
- Testen Sie Ihre Änderungen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 🐛 Bug Reports & Feature Requests

- **Bug Reports**: [GitHub Issues](https://github.com/biclighter81/wattwallet-ha/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/biclighter81/wattwallet-ha/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/biclighter81/wattwallet-ha/discussions)

## 📚 Weitere Ressourcen

- [Wattwallet Website](https://wattwallet.de/)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/docs/basic/getting_started)

## 💡 Beispiel-Anwendungsfall

Diese Integration ist besonders nützlich für:

- **Mehrfamilienhäuser**: Überwachung des Energieverbrauchs einzelner Wohnungen

---

**Entwickelt mit ❤️ für die Home Assistant Community**
