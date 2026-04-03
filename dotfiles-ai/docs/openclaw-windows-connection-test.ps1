# OpenClaw Windows Connection Test
# Run this on cbwwin (Windows) to diagnose connection issues

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenClaw Windows Connection Test" -ForegroundColor Cyan
Write-Host "Server: cbwdellr720 (192.168.4.101)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Tailscale
Write-Host "[1/5] Checking Tailscale..." -ForegroundColor Yellow
try {
    $tsStatus = tailscale status 2>&1
    if ($tsStatus -match "cbwdellr720") {
        Write-Host "  ✓ Tailscale running, cbwdellr720 visible" -ForegroundColor Green
        $tsStatus | Select-String "cbwdellr720" | Write-Host
    } else {
        Write-Host "  ✗ cbwdellr720 not found in tailnet" -ForegroundColor Red
        Write-Host "  Run: tailscale up" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Tailscale not installed or not running" -ForegroundColor Red
    Write-Host "  Download: https://tailscale.com/download" -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Check LAN connectivity
Write-Host "[2/5] Checking LAN connectivity..." -ForegroundColor Yellow
try {
    $lanTest = Test-NetConnection -ComputerName 192.168.4.101 -Port 18789 -WarningAction SilentlyContinue
    if ($lanTest.TcpTestSucceeded) {
        Write-Host "  ✓ LAN connection successful (192.168.4.101:18789)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ LAN connection failed" -ForegroundColor Red
        Write-Host "  - Check if Windows is on same network as Ubuntu" -ForegroundColor Yellow
        Write-Host "  - Check Ubuntu firewall: sudo ufw status" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Cannot test LAN connection" -ForegroundColor Red
}
Write-Host ""

# Step 3: Check Tailscale connectivity
Write-Host "[3/5] Checking Tailscale connectivity..." -ForegroundColor Yellow
try {
    $tsPing = tailscale ping cbwdellr720 2>&1
    if ($tsPing -match "ms") {
        Write-Host "  ✓ Tailscale ping successful" -ForegroundColor Green
        $tsPing | Select-Object -First 3 | Write-Host
    } else {
        Write-Host "  ✗ Tailscale ping failed" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ Cannot test Tailscale ping" -ForegroundColor Red
}
Write-Host ""

# Step 4: Check OpenClaw installation
Write-Host "[4/5] Checking OpenClaw installation..." -ForegroundColor Yellow
try {
    $ocVersion = openclaw --version 2>&1
    Write-Host "  ✓ OpenClaw installed: $ocVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ OpenClaw not installed" -ForegroundColor Red
    Write-Host "  Run: npm install -g @openclaw/cli" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Check config file
Write-Host "[5/5] Checking OpenClaw config..." -ForegroundColor Yellow
$configPath = "$env:USERPROFILE\.openclaw\openclaw.json"
if (Test-Path $configPath) {
    Write-Host "  ✓ Config exists at: $configPath" -ForegroundColor Green
    Write-Host "  Config contents:" -ForegroundColor Gray
    Get-Content $configPath | Write-Host
} else {
    Write-Host "  ✗ Config not found at: $configPath" -ForegroundColor Red
    Write-Host "  Creating config..." -ForegroundColor Yellow
    
    $config = @{
        gateway = @{
            mode = "remote"
            url = "ws://192.168.4.101:18789"
            auth = @{
                mode = "token"
                token = "33a6ddc5340e88ce6ce3accea74eadcc4d01430423989bbf"
            }
        }
    } | ConvertTo-Json -Depth 10
    
    New-Item -ItemType Directory -Force -Path (Split-Path $configPath -Parent) | Out-Null
    $config | Out-File -FilePath $configPath -Encoding utf8
    Write-Host "  ✓ Config created" -ForegroundColor Green
}
Write-Host ""

# Final test
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Gateway Connection..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
try {
    $gwStatus = openclaw gateway status 2>&1
    $gwStatus | Write-Host
    
    if ($gwStatus -match "RPC probe: ok") {
        Write-Host ""
        Write-Host "✓ SUCCESS: Gateway connection working!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ Gateway connection issue detected" -ForegroundColor Red
        Write-Host "Check the error messages above." -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Failed to connect to gateway" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
