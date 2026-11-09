# Instala o bot em um computador novo e agenda a execução às 07:00 (seg a sex).
# Uso (PowerShell, dentro da pasta do bot):  powershell -ExecutionPolicy Bypass -File .\instalar_agendamento.ps1
$ErrorActionPreference = "Stop"
$dir = $PSScriptRoot
Set-Location $dir

$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py -or $py -like "*WindowsApps*") {
    Write-Host "Python real nao encontrado. Instale em python.org (marque 'Add Python to PATH') e rode de novo." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "$dir\.env")) {
    Write-Host "Falta o arquivo .env (copie do computador antigo ou de .env.example e preencha)." -ForegroundColor Red
    exit 1
}

& $py -m pip install -q -r "$dir\requirements.txt"

@"
@echo off
cd /d "$dir"
if not exist logs mkdir logs
"$py" main.py --auto >> logs\execucao.log 2>&1
echo [%date% %time%] exit=%errorlevel% >> logs\execucao.log
"@ | Set-Content "$dir\run_diario.bat" -Encoding ascii

$acao = New-ScheduledTaskAction -Execute "$dir\run_diario.bat" -WorkingDirectory $dir
$gatilho = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 07:00
$cfg = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "botmarina-resumo-INSS" -Action $acao -Trigger $gatilho -Settings $cfg -Description "Resumo diario INSS 07h (seg a sex)" -Force | Out-Null

Write-Host "Pronto. Proxima execucao:" (Get-ScheduledTaskInfo -TaskName "botmarina-resumo-INSS").NextRunTime -ForegroundColor Green
Write-Host "IMPORTANTE: desative a tarefa 'botmarina-resumo-INSS' no computador antigo para nao enviar e-mail em duplicidade."
