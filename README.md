# Smart Bridge for Rising Water Monitoring

## Overview

The **Smart Bridge for Rising Water Monitoring** project is an IoT-based intelligent monitoring system designed to detect rising water levels beneath bridges and provide early warnings to prevent accidents during floods and heavy rainfall.

The system continuously measures the water level using sensors, processes the data through a microcontroller, uploads it to a cloud platform, and displays real-time information on a web dashboard. When the water level exceeds predefined safety thresholds, the system automatically triggers alarms and sends alerts to authorities and users.

---

# Features

* Real-time water level monitoring
* Continuous sensor data collection
* Live web dashboard
* Safe, Warning, and Danger level detection
* Automatic buzzer and LED alerts
* Cloud data storage
* Historical data visualization
* IoT-based remote monitoring
* Low-cost and energy-efficient design

---

# Problem Statement

Floods and heavy rainfall often cause river water levels to rise rapidly. Many bridges lack automated monitoring systems, making it difficult for authorities and travelers to know whether it is safe to cross.

This project addresses that problem by providing a smart, automated solution that continuously monitors water levels and issues early warnings before conditions become dangerous.

---

# Objectives

* Monitor bridge water levels in real time.
* Detect abnormal rises in water level.
* Display live readings on a dashboard.
* Send alerts during dangerous conditions.
* Improve public safety.
* Reduce flood-related accidents.

---

# System Architecture

```
Water Source
      │
      ▼
Ultrasonic Sensor
      │
      ▼
ESP32 Microcontroller
      │
      ├────────► LCD Display
      │
      ├────────► LED Indicators
      │
      ├────────► Buzzer
      │
      ▼
Wi-Fi
      │
      ▼
Cloud Database
      │
      ▼
Flask Web Dashboard
      │
      ▼
Users / Authorities
```

---

# Hardware Requirements

* ESP32 Development Board
* Ultrasonic Sensor (HC-SR04 or Waterproof Sensor)
* Rain Sensor (Optional)
* LCD Display (16×2 with I2C)
* Red, Yellow, Green LEDs
* Buzzer
* Breadboard
* Jumper Wires
* Power Supply
* USB Cable

---

# Software Requirements

* Arduino IDE
* Python 3.x
* Flask
* HTML
* CSS
* JavaScript
* Bootstrap
* Firebase / MySQL (optional)
* Git & GitHub

---

# Technologies Used

* Internet of Things (IoT)
* Embedded Systems
* Cloud Computing
* Python
* Flask
* REST API
* HTML5
* CSS3
* JavaScript

---

# Working Procedure

1. The ultrasonic sensor continuously measures the distance to the water surface.
2. The ESP32 calculates the current water level.
3. Sensor readings are transmitted over Wi-Fi.
4. The cloud server stores the received data.
5. The Flask application retrieves and displays the latest values.
6. If the water level exceeds predefined thresholds:

   * Green → Safe
   * Yellow → Warning
   * Red → Danger
7. The buzzer and LEDs activate during dangerous conditions.
8. Alerts are displayed on the dashboard and can be sent to users.

---

# Water Level Thresholds

| Water Level | Status  | Action                   |
| ----------- | ------- | ------------------------ |
| 0–40%       | Safe    | Green LED                |
| 41–70%      | Warning | Yellow LED               |
| Above 70%   | Danger  | Red LED + Buzzer + Alert |

---

# Project Folder Structure

```
SmartBridge-RisingWater/

│
├── README.md
├── LICENSE
├── requirements.txt
├── app.py
├── config.py
├── sensor/
│   ├── esp32_code.ino
│   └── sensor_data.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── alerts.html
├── database/
│   └── water_level.db
├── models/
├── documentation/
├── screenshots/
└── demo_video/
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/username/SmartBridge-RisingWater.git
```

Navigate to the project folder:

```bash
cd SmartBridge-RisingWater
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

Open your browser and visit:

```
http://localhost:5000
```

---

# Expected Output

* Live water level displayed on the dashboard.
* Real-time graphs showing water trends.
* Safe/Warning/Danger indicators.
* Automatic buzzer activation at danger level.
* Cloud storage of sensor readings.
* Instant warning notifications.

---

# Advantages

* Real-time monitoring
* Early flood detection
* Remote accessibility
* Low implementation cost
* Automatic alert system
* Improved bridge safety
* Easy maintenance
* Scalable for multiple bridges

---

# Future Enhancements

* AI-based flood prediction.
* Machine learning for water level forecasting.
* Mobile application for alerts.
* SMS and email notifications.
* Solar-powered deployment.
* CCTV integration for live monitoring.
* Government disaster management integration.
* Multi-bridge monitoring dashboard.

---

# Applications

* River bridges
* Flood-prone highways
* Rural road crossings
* Smart city infrastructure
* Disaster management systems
* Public safety monitoring

---

# Team

**Project Title:** Smart Bridge for Rising Water Monitoring

**Department:** Computer Science & Engineering (Artificial Intelligence & Machine Learning)

**Academic Year:** 2026–2027

---

# Conclusion

The **Smart Bridge for Rising Water Monitoring** system provides an intelligent, IoT-based solution for monitoring water levels beneath bridges in real time. By combining sensors, cloud connectivity, and a web dashboard, it enables early flood warnings, reduces the risk of accidents, and enhances public safety. The project is scalable, cost-effective, and suitable for deployment in flood-prone regions.
