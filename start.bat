@echo off
title NexaAgent - Starting Services
echo.
echo ========================================
echo    NexaAgent - Starting All Services
echo ========================================
echo.

:: Step 1: Check Docker
echo [1/6] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found. Please install Docker Desktop.
    pause
    exit /b 1
)
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker daemon not running. Please start Docker Desktop.
    pause
    exit /b 1
)
echo OK: Docker is running
echo.

:: Step 2: Check Ollama
echo [2/6] Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama not found. Please install from https://ollama.com
    pause
    exit /b 1
)
echo OK: Ollama is installed
echo.

:: Step 3: Start Weaviate
echo [3/6] Starting Weaviate...
docker rm -f weaviate >nul 2>&1
docker run -d -p 8080:8080 -p 50051:50051 --name weaviate semitechnologies/weaviate:latest >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to start Weaviate
    pause
    exit /b 1
)
echo OK: Weaviate started on ports 8080 and 50051
echo.

:: Step 4: Wait for Weaviate to be ready
echo [4/6] Waiting for Weaviate to be ready...
timeout /t 10 /nobreak >nul
curl -s http://localhost:8080/v1/.well-known/ready >nul 2>&1
if errorlevel 1 (
    echo WARNING: Weaviate may still be starting. Continuing anyway...
)
echo OK: Weaviate ready check complete
echo.

:: Step 5: Verify Ollama models
echo [5/6] Checking Ollama models...
ollama list | findstr "qwen2.5" >nul 2>&1
if errorlevel 1 (
    echo Downloading qwen2.5:3b model...
    ollama pull qwen2.5:3b
)
ollama list | findstr "nomic" >nul 2>&1
if errorlevel 1 (
    echo Downloading nomic-embed-text model...
    ollama pull nomic-embed-text
)
echo OK: Models ready
echo.

:: Step 6: Start Streamlit
echo [6/6] Starting Streamlit frontend...
echo.
echo ========================================
echo    NexaAgent is starting!
echo    Open: http://localhost:8501
echo ========================================
echo.
cd /d "%~dp0app"
streamlit run main.py
