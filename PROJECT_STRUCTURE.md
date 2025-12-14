# DPS-OS Project Structure

## Essential Files Only

```
dps-os/
├── dps_app.py              # Main unified application
├── run_dps.sh              # Launcher script  
├── requirements_app.txt    # Python dependencies
├── schema/
│   └── ruleSchema.json     # Security rules configuration
├── README.md               # Project overview
├── SIMPLE_SETUP.md         # Setup instructions
└── LICENSE                 # MIT License
```

## What Each File Does

### `dps_app.py` (Main Application)
- Unified monitoring application with web dashboard
- Monitors USB devices, processes, network connections
- Executes security actions (VPN, clipboard, filesystem)
- Provides web interface at http://localhost:8080
- Runs with full privileges for system-wide monitoring

### `run_dps.sh` (Launcher)
- Installs dependencies automatically
- Ensures root privileges
- Starts the main application
- One-command setup and launch

### `requirements_app.txt` (Dependencies)
- Flask (web dashboard)
- pyudev (USB monitoring)
- psutil (system monitoring)
- Essential Python packages only

### `schema/ruleSchema.json` (Configuration)
- Defines security zones (Normal, Sensitive, Ultra)
- Rules for zone transitions
- Actions to execute on events
- Easily customizable

## Usage

1. **Setup**: `chmod +x run_dps.sh`
2. **Run**: `sudo ./run_dps.sh`
3. **Monitor**: Open http://localhost:8080
4. **Test**: Use dashboard buttons or real hardware

## Clean & Minimal
- No complex multi-component architecture
- No separate daemons or services
- No browser extensions required
- Single application with everything built-in
- Easy to deploy, test, and demonstrate