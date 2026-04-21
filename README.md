# Parakh Prototype

This is the prototype for "Parakh", an AI vs Human text classification engine.

## Directory Structure
- `backend/`: FastAPI Python server, ML training, file parser, PDF report generator.
- `frontend/`: React + Tailwind CSS client, allowing file upload, sentence-by-sentence analysis, and report download.
- `start.sh`: Helper script to install requirements and run everything together.

## How to run
1. Open Bash / WSL / Git Bash.
2. Run `sh start.sh`.
3. Wait for packages to install. The frontend will start at http://localhost:5173 and backend at http://localhost:8000.

## API Endpoints
- `POST /analyze`: Evaluates sentences with ML model.
- `POST /upload`: Handles file uploads (.pdf, .docx, .txt), parses, calls `/analyze`.
- `POST /generate-report`: Generates a downloadable PDF based on analysis results.

## Requirements
- Python 3.9+
- Node.js 18+
