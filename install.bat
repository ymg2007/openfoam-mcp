@echo off
REM OpenFOAM MCP Server Installation Script for Windows
REM This script creates a virtual environment and installs dependencies

echo ========================================
echo OpenFOAM MCP Server Installation
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment
if exist venv (
    echo Virtual environment already exists. Removing...
    rmdir /s /q venv
)

echo Creating virtual environment...
python -m venv venv

if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully.
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To use the MCP server:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Configure your AI assistant (Claude Desktop, Claude Code, etc.)
echo    Add this server to your MCP config:
echo.
echo    {
echo      "mcpServers": {
echo        "openfoam": {
echo          "command": "%CD%\\venv\\Scripts\\python.exe",
echo          "args": ["%CD%\\src\\server.py"]
echo        }
echo      }
echo    }
echo.
echo Replace %CD% with the actual path to this directory.
echo.
pause
