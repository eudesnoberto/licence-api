# Script PowerShell para agendar sincronização automática
# Execute como Administrador

$scriptPath = Join-Path $PSScriptRoot "sincronizar_automatico.py"
$pythonPath = (Get-Command python).Source

# Criar tarefa agendada para executar a cada hora
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "SincronizarBancosAPI" -Action $action -Trigger $trigger -Settings $settings -Description "Sincroniza banco de dados entre servidores principal e backup" -RunLevel Highest

Write-Host "✅ Tarefa agendada criada: SincronizarBancosAPI"
Write-Host "   Executa a cada 1 hora"
Write-Host ""
Write-Host "Para verificar:"
Write-Host "   Get-ScheduledTask -TaskName SincronizarBancosAPI"
Write-Host ""
Write-Host "Para remover:"
Write-Host "   Unregister-ScheduledTask -TaskName SincronizarBancosAPI -Confirm:`$false"



