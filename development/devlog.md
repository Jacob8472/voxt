Thinking through **architecture**, **bootstrapping**, **workflow order**, and **dev practices**.
Here’s a detailed guide on how to **approach and scaffold the full Whisp App** implementation.

---

## ✅ Phase 1: **Project Bootstrapping**

### 📁 1. Create the Project Structure (match the planned layout)

Use the structure from the requirements:

```bash
mkdir -p whisp/{core,gui,cli,whisp_mode,utils}
touch whisp/{__main__.py,setup.sh,setup.py,test.py,requirements.txt,config.yaml}
```

Then inside each folder:

```bash
touch whisp/core/{config.py,logger.py,recorder.py,transcriber.py,clipboard.py,typer.py}
touch whisp/gui/main.py
touch whisp/cli/cli_main.py
touch whisp/whisp_mode/tray.py
touch whisp/utils/{setup_utils.py,benchmark_utils.py}
```

### 🔧 2. Initialize Git

```bash
git init
```

---

## ✅ Phase 2: **Core Utilities and Configuration**

> 🔁 These should be done first as all other parts depend on them.

### 📌 1. `config.py`
- Read & validate config file
- Default fallback creation if not present
- Supports YAML or JSON

### 📌 2. `setup.sh`
- `setup.sh`:
  - Check/install system deps
  - Clone/build whisper.cpp
  - Set up Python & venv

---

## ✅ Phase 3: **Core Modules**

Once config is loadable and deps are in place:

### 🎤 1. `recorder.py`
- Uses `sounddevice`
- Outputs `.wav` for whisper.cpp

### 📄 2. `transcriber.py`
- Runs whisper.cpp binary
- Parses timestamped output (`orig_tscript`)
- Trims timestamps to produce `tscript`

### 🖱️ 3. `clipboard.py`
- Uses `pyperclip`, `xclip`, or `wl-clipboard`

### ⌨️ 4. `typer.py`
- Handles X11/Wayland typing via `ydotool`
- Optional: implement delay & speed settings

### 📓 5. `logger.py`
- Handles session logging string
- Writes to file on exit
- Appends `[ai output]` if present

---

## ✅ Phase 4: **Application Modes**

After core logic is working:

### 🖥️ 1. `cli_main.py` (CLI Mode)
- Run loop with commands (`r`, `rh`, `l`, `cfg`, `x`, etc.)
- Calls core process
- Handles logging, performance mode, config edit

### 🎛️ 2. `tray.py` (WHISP Mode)
- System tray icon with status updates
- Handles hotkey triggers
- Menu options (start/stop recording, log, config, test, quit)

### 🪄 3. `main.py` (GUI Mode)
- Use `PyQt6` for minimal GUI
- Pill-shaped central button
- Show latest `tscript`, options menu

---

## ✅ Phase 5: **Extra Features**

### 🧠 1. AIPP (AI Post Processing)
- `core/aipp.py`
- Sends `tscript` to local Ollama or remote API
- Reads config: model, prompt, API key
- Returns `ai_output`

### 📊 2. Performance Metrics
- Collects timestamps, durations, memory & CPU data
- Writes to `performance_data.csv`
- Optional: use `psutil` for hardware stats

### 🧪 3. `test.py`
- CLI for:
  - Single test
  - Benchmarks (same audio, multiple models)
  - Analyze CSV
  - Diagnostics
  - Dry run (dummy inputs)

---

## ✅ Phase 6: **Final Touches**

### 📦 Packaging
- Add `pyproject.toml` or `setup.cfg` for packaging
- Use `AppImage` tools (like `linuxdeploy`) to bundle everything
- Optional: PyInstaller spec file for `.bin` builds

### 🧪 Testing
- Unit tests: core modules
- Integration tests: CLI/GUI behavior

### 📚 Documentation
- `README.md`: features, install, usage

### Project Structure
```
whisp/
├── __main__.py
├── core/
│   ├── config.py
│   ├── logger.py
│   ├── recorder.py
│   ├── transcriber.py
│   ├── clipboard.py
│   ├── aipp.py
│   ├── whisp_core.py
│   └── typer.py
├── gui/
│   └── main.py
├── cli/
│   └── cli_main.py
├── whisp_mode/
│   └── tray.py
├── utils/
│   ├── setup_utils.py
│   ├── benchmark_utils.py
|   ├── ipc_client.py
│   ├── ipc_server.py
│   ├── test.py
│   └── core_runner.py   ← orchestrates full core process
├── setup.sh
├── test.py
├── requirements.txt
├── README.md
├── LICENSE
├── config.yaml
├── .gitignore
|   --- dependencies (virtual env, whisper.cpp) and git ---
├── .venv/
├── .git/
└── whisper.cpp/
```

---

## 🧭 Suggested Implementation Order

| Priority | Module/File | Purpose |
|---------|--------------|--------|
| 🥇 1 | `config.py`, `setup.sh` | Foundational |
| 🥈 2 | `recorder.py`, `transcriber.py`, `clipboard.py` | Core pipeline |
| 🥉 3 | `cli_main.py` | First mode to validate everything |
| 4 | `logger.py`, `typer.py` | Session logging, simulated typing |
| 5 | `tray.py`, `main.py` | GUI and WHISP modes |
| 6 | `ai_processor.py`, `benchmark_utils.py`, `test.py` | AIPP, diagnostics, benchmarking |

---

🛠️ setup.sh — System Setup Script
Handles:
- Installing system packages
- Building whisper.cpp
- Creating virtualenv

🔧 Notes:
Assumes requirements.txt exists in root (we’ll create this next).

whisper.cpp uses default ggml-base.en.bin model.

Compatibility with X11 or Wayland.

---


**`requirements.txt`**, matching all required and optional components for Whisp App based on the suggested architecture.

config.py
does the following:
- Load and validate this config.
- Provide a global access object.
- Auto-fill defaults if keys are missing.

---

recorder.py.

This module will:

Use sounddevice (or optionally pyaudio) to record from the microphone.

Save the recording as a .wav file (e.g., recorded.wav).

Be reusable by CLI/GUI modes and test/benchmarking.

🧠 Notes:
Uses sounddevice, configured for 16 kHz mono.

Records into memory and saves as .wav upon stop.

Automatically generates timestamped file names if none given.

Rescales float32 input to 16-bit PCM (int16), as required by most STT engines.

---

📄 whisp/core/transcriber.py
This module:

Calls the whisper.cpp binary with proper arguments.

Extracts the full transcript with timestamps (orig_tscript) from the .txt output.

Strips timestamps to create the clean tscript.

🧪 Example usage:
```python
if __name__ == "__main__":
    transcriber = WhisperTranscriber(
        model_path="whisper.cpp/models/ggml-base.en.bin",
        binary_path="./whisper.cpp/main"
    )
    tscript, orig = transcriber.transcribe("recording_20240403_120400.wav")
    print("\n=== Cleaned Transcript ===\n", tscript)
```

🧠 Notes:
Outputs are saved in whisp_output/ and .txt files are reused if already generated.

---

📄 whisp/core/clipboard.py

🧪 Usage Example:
```python
from core.clipboard import ClipboardManager

cb = ClipboardManager(backend="auto")  # or explicitly: "xclip", "wl-copy", "pyperclip"
cb.copy("Hello from Whisp!")
```

🧠 Features & Notes
Uses pyperclip as a fallback if xclip/wl-copy are not found.

Allows override via config: clipboard_backend: "xclip" etc.

Designed for synchronous use — no clipboard polling.

---
📄 whisp/utils/core_runner.py

🧠 Features:
Modular: every component is pluggable and swappable.

Parameters:

preserve_audio: store file for reuse/benchmarking.

simulate_typing: should it type the result?

apply_aipp: (future) use AI post-processing.

✅ Example usage from cli_main.py:
python
Copy
Edit
from core.config import AppConfig
from utils.core_runner import run_core_process

cfg = AppConfig()
tscript = run_core_process(cfg, preserve_audio=False, simulate_typing=True)
print("\nFinal transcript:\n", tscript)
---
 whisp/core/typer.py

 ✅ Goals
Simulate typing each character of tscript with a configurable delay.

Use:

ydotool

Example
```python
if __name__ == "__main__":
    typer = SimulatedTyper(delay=0.02)
    typer.type("Hello from Whisp App!")
```

🧠 Notes
Works best when focus is already on a text field.
Delay is per character. Could be improved with buffered chunks if needed.
You may want to warn the user if no compatible backend is installed and offer a --simulate-install CLI flag.

---

📄 whisp/core/logger.py

logger.py module, responsible for:

Storing session logs (each tscript, optionally ai_output)
Writing them to a file at the end of the session (or on demand)
Appending with timestamps
Supporting default-named file if none specified

🧪 Example
```python
if __name__ == "__main__":
    logger = SessionLogger(True)
    logger.log_entry("Hello world.")
    logger.log_entry("[ai output] Summary of your message.")
    logger.show()
    logger.save()
```

🧠 Notes
log_entry() stores to memory (no immediate write).
save() appends to file (can be triggered once per session).
Integrates cleanly into core_runner.py after clipboard or AIPP.
---

📄 whisp/cli/cli_main.py

✅ Goals for CLI Mode
Loop: wait for commands (r, rh, l, cfg, x, h)

On r (or "rh" for hotkey trigger), run the full core process
On l, show and optionally save the current log
On cfg, open the config file in default editor
Clean exit on x

---

📄 whisp/gui/main.py

✅ Key Features in PyQt6 GUI:
Pill-style central button with status (Whisp, Recording, etc.)

Transcript preview
Clipboard notice
Options menu:
Show log
Open config
Run test (stubbed)
Quit

Non-blocking threading for core process
Integrated with AppConfig, core_runner, SessionLogger

✅ Summary of Integration
Uses AppConfig, SessionLogger, and run_core_process() from existing modules
Non-blocking via QThread to keep GUI responsive
All features match your spec, including clipboard integration and future AIPP/test stubs
Option buttons open real config and show/save logs

🧪 Example Usage

```bash
source .venv/bin/activate
python -m gui.main
```
---

📄 whisp_mode/tray.py

✅ Goals (as per the spec):
Start in background with system tray icon showing status:

Whisp, Recording, Transcribing, Typing
React to a global hotkey (e.g. ctrl+alt+r) to trigger the core process

Tray menu:
Start/Stop recording
Show/Save session log
Open settings (xdg-open config.yaml)
Run test (placeholder)
Quit

Use PyQt6 here too, since it supports system tray and integrates with the GUI stack.

✅ Notes:
Integrates with AppConfig, SessionLogger, and core_runner
Global hotkey runs the core process without UI focus
Requires an icon PNG file at whisp/assets/icon.png

🧪 To Run:
```bash
python -m whisp_mode.tray
```

✅ The entire architecture now has:

CLI with hotkey and flags
PyQt6 GUI mode
WHISP tray mode
Modular and reusable core logic

---

## 🔜 Next: `test.py` — Test / Benchmark / Diagnostics Utility

As per requirements, this utility will support:

### Modes:
- ✅ **Test** — run one core process and collect performance metrics
- ✅ **Benchmark** — run multiple models on same audio input
- ✅ **Analyze** — summarize `performance_data.csv`
- ✅ **Diagnostics** — check system dependencies, config, model files
- ✅ **Dry-run** — for CI/testing

---

## 📄 `test.py`
including all four modes: **test**, **benchmark**, **analyze**, and **diagnostics**, each with placeholder or basic functionality wired to your architecture.


## ✅ To Run:

```bash
# Single test run (with metrics)
python test.py test

# Benchmark mode (transcribe same audio with multiple models)
python test.py benchmark --audio recordings/sample.wav --models whisper.cpp/models/ggml-base.en.bin whisper.cpp/models/ggml-tiny.en.bin

# Analyze performance data
python test.py analyze

# Check system/config sanity
python test.py diagnostics

# Load modules without doing anything
python test.py dry
```

---

## 📄 `whisp/__main__.py`

---

✅ Purpose of __main__.py
This file acts as the main entry point when the module is run directly (like a script). It's especially useful when distributing your project as a package or making it more user-friendly.

---

✅ Loads the `app_mode` from `config.yaml` (as default)  
✅ Allows you to override the mode from the command line via `--mode`  
✅ Supports all four modes: `cli`, `gui`, `whisp`, `hear`  
✅ Falls back cleanly on unknown modes

---
## ✅ Example Usage (from outside the project folder):

```bash
# Use mode from config.yaml
python -m whisp

# Override to GUI
python -m whisp --mode gui

# One-off dictation (HEAR mode)
python -m whisp --mode hear
```

This ensures `whisp` behaves like a polished, production-ready entry point with both configuration and CLI flexibility.

---

✅ Plan to Implement AIPP
We’ll build a new module:

📄 core/aipp.py

With:

run_aipp(text: str, cfg: AppConfig) -> str

if provider == "local" → call Ollama via HTTP

if provider == "remote" → call OpenAI or other API

And plug that into core_runner.py.


✅ core/aipp.py is now implemented with:

run_aipp() dispatcher (based on cfg.aipp_provider)

run_ollama_aipp() — sends prompt to a local Ollama instance

run_openai_aipp() — sends prompt to OpenAI Chat Completions API

---

✅ core_runner.py is to be fully integrated with aipp.py:

Runs AIPP if apply_aipp and cfg.aipp_enabled are true

Logs [ai output] ... to the session log

Measures and logs AIPP duration, model, provider, and efficiency

---

## ✅ **How to get `ydotool` working on Wayland**

### 🧠 Context:
Wayland doesn’t allow traditional X11 tools like `xdotool` to simulate keyboard input, due to stricter security. `ydotool` is a low-level input simulation tool that *can* work on Wayland, but it needs special setup — including `uinput` device access and a background daemon.

---

### 🔧 What was done:

#### 1. **Cloned and built `ydotool` from source:**
We installed the necessary build dependencies and compiled `ydotool` from [ReimuNotMoe's GitHub repo](https://github.com/ReimuNotMoe/ydotool).

```bash
git clone https://github.com/ReimuNotMoe/ydotool.git
cd ydotool
cmake -B build
make -j$(nproc)
sudo make install
```

#### 2. **Granted access to `/dev/uinput`:**
This device is needed to simulate input events. We:
- Added a udev rule to allow users in the `input` group access:
  ```bash
  echo 'KERNEL=="uinput", MODE="0660", GROUP="input"' | sudo tee /etc/udev/rules.d/99-uinput.rules
  ```
- Reloaded udev rules:
  ```bash
  sudo udevadm control --reload-rules && sudo udevadm trigger
  ```

#### 3. **Added the current user to the `input` group:**
```bash
sudo usermod -aG input $USER
```
> ⚠️ **A full system reboot** (not just logout/login) was required for the new group membership to take effect.

#### 4. **Set up a persistent user daemon with `systemd`:**
We created a `~/.config/systemd/user/ydotoold.service` file to run the `ydotoold` daemon automatically at login, using a user-specific UNIX socket:
```ini
[Unit]
Description=ydotool user daemon
After=default.target

[Service]
ExecStart=/usr/local/bin/ydotoold --socket-path=%h/.ydotool_socket --socket-own=%U:%G
Restart=on-failure

[Install]
WantedBy=default.target
```

Then enabled and started the service:
```bash
systemctl --user daemon-reexec
systemctl --user enable --now ydotoold.service
```

#### 5. **Added the socket path to the environment:**
We exported this path and added it to the user's `.bashrc`:
```bash
export YDOTOOL_SOCKET="$HOME/.ydotool_socket"
```

---

### 🧪 Final Verification:

After reboot:
- Confirmed group membership: `groups` → should show `input`
- Verified daemon is running: `systemctl --user status ydotoold`
- Ran a typing test:
  ```bash
  ydotool type "🚀 We have liftoff!"
  ```

If text appeared as simulated input — success! 🎉

---

### ❗Key Gotchas:
- **Must reboot** after adding to `input` group — logout won’t cut it.
- **Systemd user session** must be active — won’t work in sessions started via `startx` unless systemd is enabled for the user session.
- No need to use `wtype` if `ydotool` is installed — they're redundant.

---

### IPC Hotkey Implementation

1. **IPC Server Setup** (in CLI mode):
```python
# In cli_main.py
hotkey_event = threading.Event()

def on_ipc_trigger():
    print("\n[IPC] Hotkey trigger received.")
    hotkey_event.set()

# Start IPC server for hotkey triggers
start_ipc_server(on_ipc_trigger)
```

2. **Hotkey Recording Mode** (`rh` command):
- Uses `threading.Event()` to synchronize between IPC trigger and recording
- First trigger starts recording
- Second trigger stops recording
- Continues in loop until Ctrl+C

### System Shortcut Setup

**Correct Command for GNOME/Wayland:**
```bash
bash -c 'PYTHONPATH=/home/jacobi/.project/ python3 -m whisp --trigger-record'
```

This works because:
- `bash -c` ensures command runs in a proper shell environment
- `PYTHONPATH` is set correctly to find the package
- Command runs regardless of working directory

### Setup Instructions

1. **Open Settings** → **Keyboard** → **Keyboard Shortcuts**
2. **Add Custom Shortcut:**
   - Name: `Whisp Record`
   - Command: `bash -c 'PYTHONPATH=/home/jacobi/.project/ python3 -m whisp --trigger-record'`
   - Shortcut: Your chosen key combination (e.g., `Ctrl+Alt+R`)

### Usage Flow

1. Run Whisp in CLI mode
2. Enter `rh` to start hotkey recording mode
3. Press system shortcut to start recording
4. Press system shortcut again to stop recording
5. Transcription happens automatically
6. Repeat or Ctrl+C to exit hotkey mode

---
