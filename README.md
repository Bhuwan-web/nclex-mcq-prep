# NCLEX-RN Practice Hub 🩺

A comprehensive web-based practice platform for NCLEX-RN (National Council Licensure Examination for Registered Nurses) multiple choice questions. This application helps nursing students prepare for their licensing exam with interactive practice sessions, detailed explanations, and progress tracking.

## 🌟 Features

### Practice Modes

-   **Instant Feedback Mode**: Get immediate answers and explanations after each question
-   **Exam Mode**: Submit all answers at once, simulating the real NCLEX experience

### Question Management

-   **Flexible Question Sets**: Choose from 5 to 50 questions per session
-   **Custom Starting Points**: Start from any question number in the database
-   **Mistake Review**: Focus on previously answered incorrectly questions

### Progress Tracking

-   **Session History**: Track all your practice sessions with scores and timestamps
-   **Mistake Analytics**: Identify patterns in incorrect answers
-   **Performance Statistics**: Monitor your overall progress and accuracy

### User Experience

-   **Modern Web Interface**: Clean, responsive design optimized for studying
-   **Real-time Progress**: Visual progress bars and completion tracking
-   **Detailed Explanations**: Comprehensive rationales for each answer
-   **Mobile Friendly**: Works seamlessly on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# From the project directory, build and start the app
docker compose up -d --build
```

Open `http://localhost:8000`. On first start, Docker copies the bundled
`data_loader/nclex_simple.db` into the `nclex_data` volume. The volume keeps
practice progress across container restarts. Do not use `docker compose down -v`
unless you want to delete saved progress.

### Option 2: Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

#### Prerequisites

-   Python 3.8 or higher
-   pip (Python package installer)

#### Installation Steps

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd nclex-practice-hub
    ```

2. **Create a virtual environment**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install dependencies**

    ```bash
    # Install API dependencies
    pip install -r mcq_api/requirements.txt

    # Install data loader dependencies (if you need to process PDF files)
    pip install -r data_loader/requirements.txt
    ```

4. **Set up the database**

    If you have an NCLEX PDF file:

    ```bash
    # Place your NCLEX PDF file in the data_loader directory as 'nclex.pdf'
    cd data_loader
    python simple_extract.py
    cd ..
    ```

    Or use the existing database file if available:

    ```bash
    # Make sure nclex_simple.db exists in the project root
    ```

5. **Run the application**
    ```bash
    cd mcq_api
    python run.py
    ```

</details>

## 📖 Usage

### Starting a Practice Session

1. **Open your browser** and navigate to `http://localhost:8000`
2. **Choose your practice mode**:
    - **Instant Feedback**: See answers immediately after each question
    - **Exam Mode**: Answer all questions before seeing results
3. **Configure your session**:
    - Select number of questions (5-50)
    - Choose starting question number
4. **Click "Start Practice"** to begin

### Practice Features

-   **Answer Selection**: Click on any option (A, B, C, D) to select your answer
-   **Instant Feedback** (if enabled): See correct answer and explanation immediately
-   **Progress Tracking**: Monitor your completion percentage in real-time
-   **Detailed Explanations**: Learn from comprehensive rationales for each question

### Reviewing Performance

-   **View Report**: See overall statistics including accuracy percentage
-   **Session History**: Review all previous practice sessions
-   **Practice Mistakes**: Focus on questions you've answered incorrectly

## 🏗️ Architecture

### Backend (FastAPI)

-   **REST API**: Clean, documented API endpoints
-   **SQLite Database**: Lightweight database for questions and user data
-   **SQLAlchemy ORM**: Database abstraction and management
-   **Pydantic Models**: Data validation and serialization

### Frontend (Vanilla JavaScript)

-   **Responsive Design**: Mobile-first approach with Tailwind CSS
-   **Interactive UI**: Dynamic question loading and progress tracking
-   **Modern UX**: Smooth animations and intuitive navigation

### Data Processing

-   **PDF Extraction**: Automated extraction from NCLEX question PDFs
-   **Database Population**: Structured storage of questions and answers
-   **Data Validation**: Ensures question integrity and completeness

## 🛠️ API Endpoints

### Questions

-   `GET /questions/` - Retrieve paginated questions
-   `GET /questions/count` - Get total question count
-   `GET /questions-with-answers/` - Get questions with their answers
-   `GET /question/{id}/answer` - Get detailed answer for specific question

### Practice Sessions

-   `POST /submit/` - Submit practice answers and get feedback
-   `GET /sessions/` - Retrieve practice session history
-   `GET /practice-mistakes/` - Get frequently missed questions

### Analytics

-   `GET /report/` - Get overall performance report
-   `GET /mistakes/` - Get mistake analysis
-   `GET /stats/` - Get database statistics
-   `GET /health` - Health check endpoint

## 🔧 Configuration

### Environment Variables

-   `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
-   `HOST`: Server host (default: 0.0.0.0)
-   `PORT`: Server port (default: 8000)
-   `JWT_SECRET_KEY`: Required secret used to sign access tokens. Use a long random value and keep it private.
-   `JWT_EXPIRE_MINUTES`: Token lifetime in minutes (default: 60).

### Accounts and saved progress

Create an account in the app with an email and password of at least eight
characters. The API hashes passwords with Argon2 and uses signed JWT bearer
tokens. Practice submissions, session history, reports, and mistakes are scoped
to the signed-in account. `/auth/register`, `/auth/token`, and `/auth/me` manage
accounts and tokens; progress endpoints require `Authorization: Bearer <token>`.

Set `JWT_SECRET_KEY` before starting the app, for example with
`python -c "import secrets; print(secrets.token_urlsafe(48))"`. For production,
also set `DATABASE_URL` to a persistent PostgreSQL database. Local SQLite works
for development, but Vercel's writable `/tmp` filesystem is temporary, so data
written there can disappear when an instance is replaced or restarted.
When running against PostgreSQL, app startup copies the bundled SQLite tables
into PostgreSQL once using conflict-safe inserts. To enable Actions deployments,
add a Vercel access token as
the repository secret `VERCEL_TOKEN`, then set the repository variable
`VERCEL_ACTIONS_ENABLED` to `true`. Deployments remain paused until CI has valid
Vercel credentials.

### Database Configuration

The application uses SQLite by default with the following tables:

-   `questions`: MCQ questions with options
-   `detailed_answers`: Answer explanations and rationales
-   `practice_sessions`: User practice session records
-   `practice_answers`: Individual question responses
-   `mistakes`: Tracking of incorrect answers

## 📊 Database Schema

```sql
-- Questions table
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    page_number INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    quick_answer_page INTEGER,
    detailed_answer_page INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detailed answers table
CREATE TABLE detailed_answers (
    id INTEGER PRIMARY KEY,
    page_number INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    answer CHAR(1) NOT NULL,
    rationale TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Development

### Running Tests

```bash
cd mcq_api
python -m pytest test_api.py -v
```

### Development Server

```bash
cd mcq_api
python run.py
```

The development server includes:

-   Auto-reload on code changes
-   Detailed logging
-   Interactive API documentation at `/docs`

### Adding New Questions

1. Place your NCLEX PDF in `data_loader/nclex.pdf`
2. Run the extraction script:
    ```bash
    cd data_loader
    python simple_extract.py
    ```
3. The database will be updated automatically

## 🐳 Docker Deployment

### Building the Image

```bash
docker build -t nclex-practice .
```

### Running the Container

```bash
# Basic run
docker run -p 8000:8000 nclex-practice

# With volume for persistent data
docker run -p 8000:8000 -v $(pwd)/data:/app/data nclex-practice

# With environment variables
docker run -p 8000:8000 -e PORT=3000 nclex-practice
```

### Docker Compose (Optional)

```yaml
version: "3.8"
services:
    nclex-practice:
        build: .
        ports:
            - "8000:8000"
        volumes:
            - ./data:/app/data
        environment:
            - PORT=8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

<details>
<summary>Database not found error</summary>

**Problem**: `Database file not found` error when starting the application.

**Solution**:

1. Ensure you have run the data extraction script
2. Check that `nclex_simple.db` exists in the project root
3. If using Docker, make sure the database is included in the build context

</details>

<details>
<summary>Port already in use</summary>

**Problem**: `Port 8000 is already in use` error.

**Solution**:

1. Stop any other services running on port 8000
2. Use a different port: `python run.py --port 8001`
3. For Docker: `docker run -p 8001:8000 nclex-practice`

</details>

<details>
<summary>Questions not loading</summary>

**Problem**: Questions don't appear in the web interface.

**Solution**:

1. Check the browser console for JavaScript errors
2. Verify the API is running at `http://localhost:8000/health`
3. Check that the database contains questions: `http://localhost:8000/stats`

</details>

### Getting Help

-   **Documentation**: Check the `/docs` endpoint for API documentation
-   **Issues**: Report bugs and request features on GitHub
-   **Discussions**: Join community discussions for usage questions

## 🎯 Roadmap

-   [ ] User authentication and profiles
-   [ ] Advanced analytics and reporting
-   [ ] Question categories and filtering
-   [ ] Timed practice sessions
-   [ ] Mobile app development
-   [ ] Multi-language support
-   [ ] Integration with learning management systems

---

**Made with ❤️ for nursing students preparing for NCLEX-RN**
