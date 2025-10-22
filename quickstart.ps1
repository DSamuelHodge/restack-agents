# Quick Start Script for BaseModel Agent (Windows PowerShell)
# This script helps you get started quickly

Write-Host "="*60 -ForegroundColor Cyan
Write-Host "BaseModel Agent - Quick Start" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    $dockerPs = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Docker is running" -ForegroundColor Green
        $dockerRunning = $true
    }
} catch {
    Write-Host "  Docker is not running or not installed" -ForegroundColor Red
    Write-Host "  Please install Docker Desktop and start it" -ForegroundColor Yellow
}

if ($dockerRunning) {
    # Check for Restack container
    Write-Host ""
    Write-Host "Checking Restack container..." -ForegroundColor Yellow
    $restackRunning = docker ps --filter "name=restack" --format "{{.Names}}" | Select-String "restack"
    
    if ($restackRunning) {
        Write-Host "  Restack container is running" -ForegroundColor Green
    } else {
        Write-Host "  Restack container not found" -ForegroundColor Yellow
        Write-Host "  Starting Restack container..." -ForegroundColor Yellow
        docker run -d --pull always --name restack -p 5233:5233 -p 6233:6233 ghcr.io/restackio/restack:main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Restack container started!" -ForegroundColor Green
            Start-Sleep -Seconds 3
        } else {
            Write-Host "  Failed to start Restack container" -ForegroundColor Red
        }
    }
}

# Check for .env file
Write-Host ""
Write-Host "Checking environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  .env file exists" -ForegroundColor Green
} else {
    Write-Host "  .env file not found, creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  .env file created!" -ForegroundColor Green
}

# Check for virtual environment
Write-Host ""
Write-Host "Checking Python environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "  Virtual environment created!" -ForegroundColor Green
}

Write-Host ""
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Activate virtual environment:" -ForegroundColor White
Write-Host "       .venv\Scripts\activate" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Install dependencies:" -ForegroundColor White
Write-Host "       pip install -e ." -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Open TWO terminal windows:" -ForegroundColor White
Write-Host ""
Write-Host "     Terminal 1 (Service):" -ForegroundColor White
Write-Host "       python src/service.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "     Terminal 2 (Schedule Agent):" -ForegroundColor White
Write-Host "       python src/schedule.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. View UI in browser:" -ForegroundColor White
Write-Host "       http://localhost:5233" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tip: Run 'python dev_check.py' to verify everything is set up correctly" -ForegroundColor Yellow
Write-Host ""
