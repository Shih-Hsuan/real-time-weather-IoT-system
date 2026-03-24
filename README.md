<h1 align="center">🌤️ Real-Time Weather & Time Query IoT System</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Language-C%20%7C%20MicroPython-00599C?style=for-the-badge" alt="Language">
  <img src="https://img.shields.io/badge/MCU-STM32%20%7C%20ESP32-red?style=for-the-badge" alt="MCU">
  <img src="https://img.shields.io/badge/Interface-Delta%20HMI%20%7C%20UART-success?style=for-the-badge" alt="Interface">
  <img src="https://img.shields.io/badge/Cloud-OpenWeatherMap%20API%20%7C%20JSON-yellow?style=for-the-badge" alt="Cloud">
</p>

## Project Overview
This repository contains the source code for a **Location-based Weather Retrieval System**. The project demonstrates a robust Hardware-Software Co-design approach by integrating a **Delta DOPSoft HMI Simulator (PC-based)**, an **ALIENTEK STM32F407 Development Board**, and an **ESP32 IoT Gateway**. It enables users to select a city via the simulated touchscreen interface, bridging PC software with local physical hardware to instantly retrieve live weather conditions and local time from the cloud.

## Hardware Connection Diagram

<img width="681" height="426" alt="STM32_PROJECT drawio" src="https://github.com/user-attachments/assets/e891b931-e9ed-4ae4-a482-e5d0de787f5d" />

*Figure 1: Comprehensive System Architecture. The Delta DOPSoft HMI Simulator interfaces with the ALIENTEK STM32F407 board directly via its onboard serial connection (UART1 @ 115200 bps, 8-N-1). The STM32 routes data via UART2 (@ 9600 bps) to the ESP32, which fetches real-time JSON payloads from the OpenWeatherMap API via Wi-Fi.*


## System Architecture & Data Routing

The system utilizes a 3-tier architecture, heavily relying on **UART communication** for seamless data routing:

### 1. Delta HMI (User Interface)
- Provides a graphical dropdown menu for city selection (e.g., Keelung, Tainan, Osaka, London).
- Uses internal macros (`GETCHARS`, `PUTCHARS`) to send selection commands and display incoming formatted strings.
- **Hardware Interface:** Configured COM1 for RS232 UART communication at 115200 bps, utilizing a standard **8-N-1** data frame (8 data bits, No parity, 1 stop bit) with no flow control.

### 2. STM32 (Local Data Router)
Acts as the central communication bridge handling dual UART interfaces:
- **UART1 (115200 bps):** Communicates with the Delta HMI.
- **UART2 (9600 bps):** Communicates with the ESP32.
- **Routing Logic:** Translates raw integer commands from the HMI into specific character flags (e.g., `0` $\rightarrow$ `'K'` for Keelung) and routes them to the ESP32. It also buffers the incoming JSON-parsed string from the ESP32 and routes it back to the HMI display.

### 3. ESP32 (IoT Gateway)
- **Wi-Fi & NTP:** Establishes internet connectivity and fetches accurate UTC time via NTP.
- **RESTful API & JSON:** Queries the **OpenWeatherMap API** using `urequests`, parses the incoming JSON payloads to extract temperature and weather descriptions.
- **Data Formatting:** Computes timezone offsets dynamically (e.g., UTC+8 for Taiwan, UTC+9 for Japan) and formats the data into a fixed-length string before transmitting it back to the STM32.

## Repository Structure
- `STM32_Code/` : Bare-metal C source code for the STM32 UART router.
- `ESP32_Code/` : MicroPython scripts for Wi-Fi connection, API fetching, and JSON parsing.
- `HMI_Macros/` : Reference text for Delta HMI background and button macros.
