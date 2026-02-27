# FastAPI Task Management System

A RESTful API built with FastAPI that manages tasks using a JSON Lines persistent storage system.

## Features
- **Persistence**: Tasks survive server restarts via `tasks.txt`[cite: 38].
- **Statistics**: Get real-time data on task completion percentages [cite: 98-99].
- **Filtering**: View tasks based on their completion status[cite: 81].

## How to Run
### 1. Setup Environment
Open your terminal and create a clean workspace:
```bash
# Navigate to the project root
cd fastapi-tasks

# Create a virtual environment
python -m venv venv

# Activate the environment
source venv/bin/activate  # Mac/Linux
.\venv\Scripts\activate   # Windows
```
### 2. Install Dependencies
```bash
pip install fastapi uvicorn pydantic
```
### 3. Initialize Data Storage
```bash
touch tasks.txt      # Mac/Linux
type nul > tasks.txt # Windows
```
### 4. Start the Server
```bash
uvicorn main:app --reload
```
### 5. Access Documentation
```bash
http://127.0.0.1:8000/docs : Interactive API Docs (Swagger)
http://127.0.0.1:8000/ : Health Check

### API Endpoints
GET / : Health check.
GET /tasks : Retrieve all tasks (optional completed filter).
GET /tasks/stats : View task summary statistics.
POST /tasks : Create a new task.
PUT /tasks/{id} : Update an existing task. 
DELETE /tasks/{id} : Delete a specific task.
```
