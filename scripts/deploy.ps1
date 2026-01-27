# Deploy Script for Unified GenAI Platform

Write-Host "Starting Deployment..." -ForegroundColor Green

# Check Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH."
    exit 1
}

# Navigate to docker compose location
$ComposeFile = "infrastructure/docker/docker-compose.yml"
if (-not (Test-Path $ComposeFile)) {
    Write-Error "Docker Compose file not found at $ComposeFile"
    exit 1
}

# Build and Up
Write-Host "Building and starting containers..." -ForegroundColor Cyan
docker compose -f $ComposeFile up -d --build

# Check status
if ($?) {
    Write-Host "Deployment started successfully!" -ForegroundColor Green
    Write-Host "API: http://localhost:8000"
    Write-Host "Frontend: http://localhost:3000"
    Write-Host "Checking service health in 5 seconds..."
    Start-Sleep -Seconds 5
    docker compose -f $ComposeFile ps
} else {
    Write-Error "Deployment failed."
    exit 1
}
