## Installation and Setup

Follow these steps to set up and run the application. You can choose between running the **Production Build** (recommended for standard use) or the **Development Server** (recommended for modifying frontend code).

### 1. Clone the Repository
Clone the project to your local machine and navigate into the root directory:
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup (Python)
Create and activate a virtual environment, then install the required dependencies:

**On Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Option A: Production Build (No Dev Server Needed)
Use this option to compile the frontend assets directly into the application so it runs standalone.

**1. Build the Frontend:**
```bash
cd frontend
npm install
npm run build
```

**2. Run the Application:**
Navigate back to the root folder and execute the main script directly (do not set `FRONTEND_DEV_URL`):
```bash
cd ..
python main.py
```
*(Use `python3 main.py` on macOS/Linux)*

---

### Option B: Development Server Flow
Use this option if you plan to edit the frontend code and want hot-reloading active inside the `pywebview` window.

**1. Start the Frontend Dev Server:**
```bash
cd frontend
npm install
npm run dev
```

**2. Run the Application:**
Open a **new terminal window**, activate your Python virtual environment, navigate to the project root folder, set the dev environment variable, and start the script:

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
$env:FRONTEND_DEV_URL="http://localhost:5173/"
python main.py
```

**On macOS/Linux (Bash/Zsh):**
```bash
source venv/bin/activate
export FRONTEND_DEV_URL="http://localhost:5173/"
python3 main.py
```
