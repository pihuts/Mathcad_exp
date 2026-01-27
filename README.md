# Mathcad Automator

**Mathcad Automator** is a local web application designed to automate PTC Mathcad Prime calculations. It enables engineers to perform complex parameter studies (batch processing) and chain multiple Mathcad files together in logic-driven workflows without writing VBA or complex scripts.

Now featuring **Bisaya Mode**: Enjoy playful, cycling status messages in the Cebuano dialect while your engineering calculations run in the background!

![UI Screenshot](docs/screenshot.png) *(Place holder for screenshot)*

## Features

- **Batch Processing:**
  - Define input ranges (Start, End, Step) or lists.
  - Upload CSV files for bulk parameter updates.
  - Export results to `.pdf` and `.mcdx` automatically.
- **Workflow Orchestration:**
  - Chain multiple Mathcad files (File A Output -> File B Input).
  - Visual drag-and-drop workflow builder.
- **Native Experience:**
  - Uses native Windows file dialogs for file selection.
  - Live results list to quickly access generated files.
  - Playful status messages to keep you entertained.

## Prerequisites

Before running the application, ensure you have the following installed:

1.  **PTC Mathcad Prime** (Licensed and Active). Use the desktop application to verify it opens correctly.
2.  **Python 3.10+**.
3.  **Node.js 18+** (Only required if you plan to modify the frontend code).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/mathcad-automator.git
    cd mathcad-automator
    ```

2.  **Set up the Backend (Python):**
    ```bash
    # Create a virtual environment
    python -m venv .venv

    # Activate the environment
    # Windows (CMD):
    .venv\Scripts\activate.bat
    # Windows (PowerShell):
    .venv\Scripts\Activate.ps1

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Set up the Frontend (React):**
    ```bash
    cd frontend
    npm install
    # Return to root
    cd ..
    ```

## Running the Application

### Option 1: The Easy Way (One-Click)

1.  Double-click **`start_dev.bat`** in the project root.
2.  This will open two terminal windows (one for Backend, one for Frontend) and launch the app in your default browser.

### Option 2: Manual Start

You need to run the backend and frontend in separate terminals.

**Terminal 1 (Backend):**
```bash
.venv\Scripts\activate
python -m src.server.main
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Troubleshooting

- **"Mathcad Application not found" / COM Errors:**
  - Mathcad's COM API can sometimes fail if the application is in a "sleeping" state.
  - **Fix:** Open Mathcad Prime manually *before* starting the Automator. Once open, retry the batch job.
- **Backend doesn't start:**
  - Ensure you have activated the virtual environment (`.venv`).
  - Check if port `8000` is already in use.

## License

MIT License.
