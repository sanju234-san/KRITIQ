# Setup & Execution Plan

This document outlines the startup plan for running the skeleton version of Kritiq.

## Prerequisites

* Python 3.9+
* Node.js 16+
* MongoDB Atlas connection string (or local MongoDB for testing)
* Gemini API Key

## Backend Setup (Skeleton Mode)

1. Navigate to backend:
   ```bash
   cd kritiq-backend
   ```
2. Create virtual environment and activate:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup environment file:
   * Copy `.env.example` to `.env` and fill variables.
5. Run server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup (Skeleton Mode)

1. Navigate to frontend:
   ```bash
   cd kritiq-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Setup environment file:
   * Copy `.env.example` to `.env`
4. Run dev server:
   ```bash
   npm run dev
   ```
