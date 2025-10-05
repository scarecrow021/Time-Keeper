# 🕒 Time-Keeper

**Time-Keeper** is a personal time-tracking and logging application built with **Python + PyQt6**, designed to help you maintain authentic daily work logs.  
It automatically records your activities, calculates total work duration, and exports a secured, tamper-evident PDF report.

---

## 🚀 Features

- Real-time work tracking with live clocks (`HH:MM:SS`)
- Displays:
  - Current time  
  - Time spent  
  - Time remaining  
  - Countdown to leave time  
- Editable **leave time** with seconds precision  
- Automatic location detection (via IP)
- Displays full system information (Make / Model / Hostname)
- Generates professional **secured PDF reports**
  - Includes full session metadata  
  - Appends a legal-style authenticity disclaimer  
  - Automatically locks the PDF against edits  
- Password-protected app closure (prevents accidental exits)
- Clean, minimal interface using PyQt6

---

## 📘 Example PDF Output

Each generated daily log includes:
- User info (name, system, PC)
- Login/Logout times  
- Hours worked (in HH:MM:SS)
- Location info:
  ```
  IP, City, Region, Country, Coordinates, Postal, Timezone
  ```
- Verbatim log messages
- Authenticity disclaimer at the end of the file

---

## 🧩 Requirements

- Python 3.9+
- Modules:
  ```bash
  pip install PyQt6 reportlab PyPDF2 requests
  ```

---

## ⚙️ Usage

1. Clone the repository:
   ```bash
   git git@github.com:scarecrow021/Time-Keeper.git
   cd time-keeper
   ```

2. Run the app:
   ```bash
   python main.py
   ```

3. The app starts logging automatically.  
   - Enter messages and click **Submit** to add to your log.  
   - Closing the app requires the password (`BYEBYE`).  
   - Upon closure, your **daily log PDF** will be generated in the `daily_log/` directory.

---

## 🔒 Security & Authenticity

- Each PDF is generated **verbatim from your logs** and locked from edits.
- Timestamps are precise to the second.
- If a file appears tampered with, it should not be accepted as valid.
- The design encourages keeping the app open throughout the workday for real-time tracking.

---

## 🧠 Technical Notes

- Uses `ipinfo.io` API for geolocation.  
- Detects system manufacturer and model via platform-specific commands.
- Fully cross-platform (Windows, macOS, Linux).

---

## 🧾 License & Attribution

**Time-Keeper** © Soumik Sarkar  
Licensed under the [MIT License](LICENSE).

> *"Designed for accountability, built for authenticity.🤣"*
