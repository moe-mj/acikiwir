## Tech Stack

* **Frontend:** React + Vite
* **Backend:** FastAPI
* **Containerization:** Docker & Docker Compose

---

## Prerequisites

Before getting started, make sure you have the following installed:

* Docker Desktop
* Git
* VS Code (recommended)
* WSL2 (Windows users)

> **Note:** You do **not** need to install Node.js, Python, FastAPI, or any project dependencies on your local machine. Everything runs inside Docker containers.

---

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd acikiwir
```

### 2. Build and start the project

```bash
docker compose up --build
```

The first build may take a few minutes since Docker needs to download the required images and install all dependencies.

Once the containers are running:

| Service               | URL                        |
| --------------------- | -------------------------- |
| Frontend              | http://localhost:5173      |
| Backend API           | http://localhost:8000      |
| FastAPI Documentation | http://localhost:8000/docs |

---

## Running the Project

After the initial build, you can start the application with:

```bash
docker compose up
```

To stop the containers:

```bash
docker compose down
```

---

## Installing Frontend Dependencies

Install new npm packages inside the frontend container:

```bash
docker compose exec frontend npm install <package-name>
```

Example:

```bash
docker compose exec frontend npm install axios
```

---

## Installing Backend Dependencies

Install Python packages inside the backend container:

```bash
docker compose exec backend pip install <package-name>
```

After installing new packages, update `requirements.txt`:

```bash
docker compose exec backend pip freeze > requirements.txt
```

---

## Project Structure

```text
acikiwir/
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   └── public/
│
├── docker-compose.yml
└── README.md
```

---

## Useful Docker Commands

### Rebuild the project

```bash
docker compose up --build
```

### View logs

```bash
docker compose logs
```

### View logs for a specific service

```bash
docker compose logs frontend
docker compose logs backend
```

### Open a shell inside the frontend container

```bash
docker compose exec frontend sh
```

### Open a shell inside the backend container

```bash
docker compose exec backend sh
```

### Stop all containers

```bash
docker compose down
```

### Stop and remove containers, networks, and volumes

```bash
docker compose down -v
```

---

## Development Workflow

1. Pull the latest changes from the repository.

2. Start the application with:

   ```bash
   docker compose up
   ```

3. Develop your features.

4. Commit your changes.

5. Push your branch to the remote repository.

Since all dependencies are managed inside Docker, there is no need to install project-specific packages on your local machine.
