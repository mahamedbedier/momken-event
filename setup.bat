@echo off
REM ═══════════════════════════════════════════════════════════════
REM  Momken For Her — One-Click Setup Script
REM  Run this from the project root: d:\Momken Event\
REM ═══════════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║   Momken For Her — Platform Setup               ║
echo ╚══════════════════════════════════════════════════╝
echo.

REM ── Step 1: Archive old HTML files ─────────────────────────────
echo [1/6] Archiving old HTML files...
if not exist "old" mkdir old
if exist "index.html" move /Y index.html old\index.html >nul 2>&1
if exist "auth.html" move /Y auth.html old\auth.html >nul 2>&1
if exist "checkout.html" move /Y checkout.html old\checkout.html >nul 2>&1
if exist "speakers.html" move /Y speakers.html old\speakers.html >nul 2>&1
if exist "agenda.html" move /Y agenda.html old\agenda.html >nul 2>&1
echo       Done.

REM ── Step 1b: Copy images to static folder ──────────────────────
echo [1b/6] Copying images to static folder...
if not exist "static\images" mkdir "static\images"
if exist "images\hero-bg.jpg" copy /Y "images\hero-bg.jpg" "static\images\hero-bg.jpg" >nul 2>&1
if exist "images\logo2.png" copy /Y "images\logo2.png" "static\images\logo2.png" >nul 2>&1
echo       Done.

REM ── Step 2: Install Python dependencies ────────────────────────
echo [2/6] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo       ERROR: pip install failed. Make sure Python is installed.
    pause
    exit /b 1
)
echo       Done.

REM ── Step 3: Install NPM dependencies (Tailwind CSS) ───────────
echo [3/6] Installing Tailwind CSS...
npm install
if errorlevel 1 (
    echo       ERROR: npm install failed. Make sure Node.js is installed.
    pause
    exit /b 1
)
echo       Done.

REM ── Step 4: Build Tailwind CSS ─────────────────────────────────
echo [4/6] Building Tailwind CSS...
npm run build:css
if errorlevel 1 (
    echo       ERROR: Tailwind build failed.
    pause
    exit /b 1
)
echo       Done.

REM ── Step 5: Create instance directory ──────────────────────────
echo [5/6] Setting up database...
if not exist "instance" mkdir instance

REM ── Step 6: Seed the database ──────────────────────────────────
python seed.py
if errorlevel 1 (
    echo       ERROR: Database seeding failed.
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║   Setup Complete!                               ║
echo ║                                                 ║
echo ║   Start the server:  python app.py              ║
echo ║   Then open:  http://localhost:5000              ║
echo ║                                                 ║
echo ║   Admin login:  admin@momken.com / admin123     ║
echo ╚══════════════════════════════════════════════════╝
echo.
pause
