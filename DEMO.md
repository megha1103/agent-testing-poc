# How to create and run the demo

## Option 1: Run from the IDE (Cursor / VS Code)

1. **Open the POC folder**
   - File → Open Folder → choose `agent-testing-poc`  
   - Or open the repo and set the working directory to `agent-testing-poc` when running.

2. **Install dependencies once**
   - Open a terminal in the IDE (Terminal → New Terminal).
   - Make sure the terminal is in `agent-testing-poc`:
     ```bash
     cd agent-testing-poc
     ```
   - Run:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run the demo**
   - **Using Run/Debug:** Press **F5** or use Run → Start Debugging.  
     The first time, choose **Python** and then **Python File** (run current file).  
     Set the current file to `main.py` and run.
   - **Using the terminal:** In the same terminal, run:
     ```bash
     python main.py
     ```
   - **Using the play button:** Right‑click `main.py` in the explorer → **Run Python File in Terminal**.

4. **Check the result**
   - In the terminal you’ll see: scenarios run, overall PASS/FAIL, and paths to the report files.
   - Open `reports/report_<timestamp>_<id>.md` in the IDE to see the human‑readable report.

## Option 2: Run from command line

```bash
cd agent-testing-poc
pip install -r requirements.txt
python main.py
```

To demo the **senior customer** persona:

```bash
python main.py senior_customer
```

## Option 3: One-click demo script (Windows)

Double‑click `run_demo.bat` (or run it from a terminal). It will:

- Try to use your default Python.
- Install dependencies if needed.
- Run the full test suite and open the latest report folder.

## What you’ll see in the demo

- **Console:** Which scenarios run, then overall PASS/FAIL and a short summary per scenario.
- **reports/report_*.json:** Machine‑readable results (for CI or tooling).
- **reports/report_*.md:** Short report with pass/fail, score, reason, and suggestion per scenario.

No API key is required; the demo uses mock avatar and mock evaluator so it runs offline.
