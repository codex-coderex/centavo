## Installation and Setup

Follow these steps to set up and run both the backend and frontend development servers.

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

### 3. Frontend Setup (Node.js)
Navigate to the frontend directory, install dependencies, and start the development server:
```bash
cd frontend
npm install
npm run dev
```

### 4. Run the Application
Open a **new terminal window**, navigate to the project folder, set the environment variable, and start the main script:

**On Windows (PowerShell):**
```powershell
cd centavo
\$env:FRONTEND_DEV_URL="http://localhost:5173/"
python main.py
```

**On macOS/Linux (Bash/Zsh):**
```bash
cd centavo
export FRONTEND_DEV_URL="http://localhost:5173/"
python3 main.py
```
