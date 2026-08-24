# TrustPed

TrustPed is a machine learning-powered web application that analyzes an e-commerce store and estimates its fraud risk.

The application provides:

* Overall fraud risk score
* Risk status: `SAFE`, `WARNING`, or `HIGH`
* Price anomaly analysis
* Review anomaly analysis
* Store information anomaly analysis
* Explainable AI insights using SHAP
* Natural-language risk explanation using Google Gemini

The project is fully containerized with Docker, so judges do **not** need to install Python, Node.js, FastAPI, or other project dependencies manually.

---

## Tech Stack

* **Frontend:** React + Vite
* **Backend:** FastAPI
**AI / NLP:** XGBoost, scikit-learn, SHAP, Google Gemini API, TF-IDF
* **Containerization:** Docker & Docker Compose

---

## Prerequisites

Before getting started, make sure you have the following installed:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Git
* VS Code (recommended)
* WSL2 (required for Windows users running Docker with the WSL2 backend)

All project dependencies are installed inside Docker containers.

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd acikiwir
```

---

## 2. Configure the Gemini API Key

The application uses Google Gemini to generate the natural-language explanation shown in the analysis result.

Create a `.env` file in the **backend** (see the .env.example)
```env
GEMINI_API_KEY=your_gemini_api_key
```

Example project structure:

```text
acikiwir/
├── backend/
├── frontend/
├── docker-compose.yml
├── .env
└── README.md
```

> **Important:** Do not commit the `.env` file or expose your Gemini API key publicly.

If the API key is unavailable or the Gemini request fails, the backend automatically uses a built-in fallback explanation so that the application can still return an analysis result.

---

## 3. Build and Start the Application

From the project root, run:

```bash
docker compose up --build
```

Docker will:

1. Build the frontend container
2. Build the backend container
3. Install all required dependencies
4. Start both services
5. Connect the frontend and backend through Docker Compose

The first build may take several minutes.

Once the containers are running, open:

| Service               | URL                        |
| --------------------- | -------------------------- |
| Frontend              | http://localhost:5173      |
| Backend API           | http://localhost:8000      |
| FastAPI Documentation | http://localhost:8000/docs |

---

# 4. Using the Application

Open the frontend:

```text
http://localhost:5173
```

The application accepts a **store ID**.

For example:

```text
2017
```

The backend retrieves the corresponding store data from the project's dataset, runs the trained fraud detection model, calculates the risk score, and returns the analysis.

The result contains:

* Overall risk score
* Risk status
* Risk thresholds
* Price anomaly
* Review anomaly
* Store information anomaly
* Top contributing factors
* Overall explanation

---

# 5. Testing the Backend Directly

The FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

You can use Swagger UI to test the API without the frontend.

For example, a prediction request can be sent with:

```json
{
  "id": 2017
}
```

The API returns a response similar to:

```json
{
  "id": 2017,
  "store_name": "PT Lestari Tbk",
  "risk_score": 97.55,
  "status": "HIGH",
  "thresholds": {
    "warning": 79.46,
    "high": 90.88
  },
  "price_anomaly": {
    "score": 29.81,
    "explanation": "...",
    "top_features": [
      "price_deviation",
      "price_ratio",
      "res_rating_price_interaction"
    ]
  },
  "review_anomaly": {
    "score": 29.57,
    "explanation": "...",
    "top_features": [
      "five_star_reviews_last_24h"
    ]
  },
  "information_anomaly": {
    "score": 40.62,
    "explanation": "...",
    "top_features": [
      "five_star_ratio",
      "average_rating"
    ]
  },
  "overall_explanation": "..."
}
```

---

# 6. Running the Project After the First Build

After the initial build, you normally do not need to rebuild the images.

Start the application with:

```bash
docker compose up
```

Stop the application with:

```bash
docker compose down
```

---

# 7. Useful Docker Commands

### Rebuild the application

Use this after changing dependencies or Docker configuration:

```bash
docker compose up --build
```

### View logs

```bash
docker compose logs
```

### View backend logs

```bash
docker compose logs backend
```

### View frontend logs

```bash
docker compose logs frontend
```

### Follow backend logs in real time

```bash
docker compose logs -f backend
```

This is useful when checking API requests, model loading, or Gemini API errors.

### Open a shell inside the backend container

```bash
docker compose exec backend sh
```

### Open a shell inside the frontend container

```bash
docker compose exec frontend sh
```

### Stop the application

```bash
docker compose down
```

### Stop the application and remove volumes

```bash
docker compose down -v
```

> Removing volumes may delete Docker-managed dependency caches and other persisted container data.

---

# 8. Installing Additional Dependencies

Dependencies should be installed **inside the appropriate Docker container**, not directly on the host machine.

### Frontend

```bash
docker compose exec frontend npm install <package-name>
```

Example:

```bash
docker compose exec frontend npm install axios
```

If the dependency is added to `package.json`, rebuild the frontend container when necessary:

```bash
docker compose up --build
```

### Backend

```bash
docker compose exec backend pip install <package-name>
```

After adding a Python dependency, update:

```text
backend/requirements.txt
```

For example:

```bash
docker compose exec backend pip freeze > backend/requirements.txt
```

Then rebuild:

```bash
docker compose up --build
```

---

# 9. Project Structure

The repository is organized as follows:

```text
acikiwir/
│
├── backend/
│   ├── app/
│   │   ├── model/
│   │   │   └── model_bundle.joblib
│   │   ├── services/
│   │   └── schemas/
│   ├── data/
│   │   └── synthetic_data.csv
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env
└── README.md
```

The exact internal structure may vary slightly depending on the latest project version.

---

# 10. Development Workflow

A typical workflow for evaluating or developing the project is:

### First time

```bash
git clone <repository-url>
cd acikiwir
```

Create the `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Then build and start:

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

### Subsequent runs

After the initial build:

```bash
docker compose up
```

When finished:

```bash
docker compose down
```

---

# 11. Troubleshooting

### Frontend cannot connect to backend

Check that both containers are running:

```bash
docker compose ps
```

Then check the backend logs:

```bash
docker compose logs backend
```

The backend should be available at:

```text
http://localhost:8000
```

### Gemini explanation is not generated

Check that the `.env` file exists in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Then restart the containers:

```bash
docker compose down
docker compose up
```

To inspect Gemini-related errors:

```bash
docker compose logs backend
```

The application contains a fallback explanation mechanism, so a Gemini API failure does not prevent the fraud analysis itself from being returned.

### Docker changes are not reflected

Rebuild the containers:

```bash
docker compose down
docker compose up --build
```

---

# 12. Important Notes for Evaluation

The project is designed to be evaluated through the Dockerized application.

No local Python or Node.js environment is required.

The recommended evaluation flow is:

```text
Clone repository
      ↓
Create .env with GEMINI_API_KEY
      ↓
docker compose up --build
      ↓
Open http://localhost:5173
      ↓
Enter a store ID
      ↓
View fraud risk analysis
```

The backend can also be evaluated independently through:

```text
http://localhost:8000/docs
```

The trained model and required project data are included in the repository so the application can run directly without requiring the evaluator to retrain the model.

---
