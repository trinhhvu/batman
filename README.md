# batman v1

Advanced Dailymotion Visual Intelligence Tool.

## Platform Support
- **Windows**: x64 / x86
- **macOS**: Apple Silicon (M1, M2, M3, M4) / Intel Core

## Requirements
- Python 3.10+
- Requirements listed in `requirements.txt`

## Getting Started

### Windows
1. Open PowerShell or Command Prompt.
2. Execute `run_windows.bat`.

### macOS
1. Open Terminal.
2. Grant execution permissions:
   ```bash
   chmod +x *.sh
   ```
3. Run the application:
   ```bash
   ./run_mac.sh
   ```

## Production Build (macOS)
To generate a standalone `.app` bundle:
1. Run `./build_mac.sh`.
2. Locate the output in the `dist/` directory.

## Features
- Real-time video metadata extraction (Title, Channel, Owners).
- High-precision view analytics (Total, 24h, 1h).
- Regional geoblocking status detection.
- Batch processing for large-scale data sets.
- Excel (XLSX) export integration.
