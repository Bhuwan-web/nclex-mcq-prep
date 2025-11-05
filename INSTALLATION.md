# Installation Guide

This guide provides detailed instructions for setting up the NCLEX-RN Practice Hub on your system.

## 🐳 Docker Installation (Recommended)

Docker provides the easiest and most consistent way to run the application across different systems.

### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/) installed on your system
-   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

### Quick Start with Docker

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd nclex-practice-hub
    ```

2. **Build and run with Docker**

    ```bash
    docker build -t nclex-practice .
    docker run -p 8000:8000 nclex-practice
    ```

3. **Access the application**
   Open your browser and go to `http://localhost:8000`

### Using Docker Compose

For a more robust setup with persistent data:

1. **Start the application**

    ```bash
    docker-compose up -d
    ```

2. **View logs**

    ```bash
    docker-compose logs -f
    ```

3. **Stop the application**
    ```bash
    docker-compose down
    ```

### Docker with Custom Database

If you have your own NCLEX database file:

```bash
# Place your database file in the project root
cp /path/to/your/nclex_simple.db ./

# Run with volume mount
docker run -p 8000:8000 -v $(pwd)/nclex_simple.db:/app/nclex_simple.db:ro nclex-practice
```

## 🐍 Manual Python Installation

### Prerequisites

-   **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
-   **pip** - Usually included with Python
-   **Git** - [Download Git](https://git-scm.com/downloads)

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd nclex-practice-hub
```

#### 2. Create Virtual Environment

**On macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
# Install API dependencies
pip install -r mcq_api/requirements.txt

# Install data processing dependencies (optional)
pip install -r data_loader/requirements.txt
```

#### 4. Database Setup

**Option A: Use existing database**
If you have an existing `nclex_simple.db` file, place it in the project root.

**Option B: Create database from PDF**
If you have an NCLEX PDF file:

```bash
# Place your PDF file in data_loader directory
cp /path/to/your/nclex.pdf data_loader/nclex.pdf

# Run extraction script
cd data_loader
python simple_extract.py
cd ..
```

**Option C: Create empty database**
The application will create an empty database automatically on first run.

#### 5. Run the Application

```bash
cd mcq_api
python run.py
```

The application will be available at `http://localhost:8000`

### Troubleshooting Manual Installation

<details>
<summary>Python version issues</summary>

**Problem**: `python: command not found` or version conflicts

**Solutions**:

-   On macOS: Use `python3` instead of `python`
-   On Windows: Ensure Python is added to PATH during installation
-   Use `python --version` to check your Python version
-   Consider using [pyenv](https://github.com/pyenv/pyenv) for version management

</details>

<details>
<summary>Permission errors</summary>

**Problem**: Permission denied when installing packages

**Solutions**:

-   Use virtual environment (recommended)
-   On macOS/Linux: Use `sudo` (not recommended)
-   On Windows: Run command prompt as administrator (not recommended)

</details>

<details>
<summary>Package installation failures</summary>

**Problem**: Packages fail to install

**Solutions**:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output to see errors
pip install -r mcq_api/requirements.txt -v

# Try installing packages individually
pip install fastapi uvicorn sqlalchemy pydantic
```

</details>

## 🖥️ Development Setup

For developers who want to contribute or modify the application:

### Additional Development Dependencies

```bash
# Install development dependencies
pip install pytest black flake8 mypy

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
cd mcq_api
python -m pytest test_api.py -v
```

### Code Formatting

```bash
# Format code with black
black mcq_api/ data_loader/

# Check code style
flake8 mcq_api/ data_loader/

# Type checking
mypy mcq_api/
```

### Development Server

```bash
cd mcq_api
python run.py
```

The development server includes:

-   Auto-reload on code changes
-   Detailed logging
-   Interactive API documentation at `http://localhost:8000/docs`

## 🌐 Production Deployment

### Environment Variables

Set these environment variables for production:

```bash
export PORT=8000
export HOST=0.0.0.0
export DATABASE_URL=sqlite:///./nclex_simple.db
```

### Using a Process Manager

**With systemd (Linux):**

Create `/etc/systemd/system/nclex-practice.service`:

```ini
[Unit]
Description=NCLEX Practice Hub
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/nclex-practice-hub
Environment=PATH=/path/to/nclex-practice-hub/.venv/bin
ExecStart=/path/to/nclex-practice-hub/.venv/bin/python -m uvicorn mcq_api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable nclex-practice
sudo systemctl start nclex-practice
```

**With PM2 (Node.js process manager):**

```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'nclex-practice',
    script: 'python',
    args: '-m uvicorn mcq_api.main:app --host 0.0.0.0 --port 8000',
    cwd: '/path/to/nclex-practice-hub',
    interpreter: '/path/to/nclex-practice-hub/.venv/bin/python',
    env: {
      PORT: 8000
    }
  }]
}
EOF

# Start application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Reverse Proxy Setup

**Nginx configuration:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/nclex-practice-hub/mcq_api/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📱 Platform-Specific Instructions

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Follow standard installation steps above
```

### Windows

1. **Install Python from Microsoft Store** (recommended) or [python.org](https://python.org)
2. **Install Git** from [git-scm.com](https://git-scm.com)
3. **Open Command Prompt or PowerShell**
4. Follow standard installation steps above

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv git

# Follow standard installation steps above
```

### Linux (CentOS/RHEL/Fedora)

```bash
# Install Python and pip
sudo dnf install python3 python3-pip git  # Fedora
# or
sudo yum install python3 python3-pip git  # CentOS/RHEL

# Follow standard installation steps above
```

## 🔧 Configuration Options

### Database Configuration

The application supports different database configurations:

```python
# SQLite (default)
DATABASE_URL = "sqlite:///./nclex_simple.db"

# PostgreSQL (for production)
DATABASE_URL = "postgresql://user:password@localhost/nclex_db"

# MySQL
DATABASE_URL = "mysql://user:password@localhost/nclex_db"
```

### Server Configuration

```bash
# Change port
export PORT=3000

# Change host (for external access)
export HOST=0.0.0.0

# Enable debug mode
export DEBUG=true
```

## 🆘 Getting Help

If you encounter issues during installation:

1. **Check the logs** for error messages
2. **Verify prerequisites** are installed correctly
3. **Try the Docker installation** if manual installation fails
4. **Search existing issues** on GitHub
5. **Create a new issue** with detailed error information

### Common Installation Issues

<details>
<summary>Port already in use</summary>

**Error**: `Address already in use`

**Solution**:

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
export PORT=8001
```

</details>

<details>
<summary>Database permission errors</summary>

**Error**: `Permission denied` when accessing database

**Solution**:

```bash
# Fix file permissions
chmod 644 nclex_simple.db
chown $USER:$USER nclex_simple.db
```

</details>

<details>
<summary>Module not found errors</summary>

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r mcq_api/requirements.txt
```

</details>

---

For more help, please check the main [README.md](README.md) or create an issue on GitHub.
