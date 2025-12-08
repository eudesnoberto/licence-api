#SingleInstance,Force

; ============================================================================
; PROTEÇÃO DE LICENÇA - Verificação obrigatória no início
; ============================================================================

; Inclui o módulo de verificação
#Include license_verify.ahk

; Verifica licença antes de continuar
licenseResult := License_Verify()

If (!licenseResult.allow) {
    ; Bloqueia execução se não houver licença válida
    License_ShowError(licenseResult.msg . "`n`nDevice ID: " . licenseResult.deviceId)
    ExitApp
}

; Se chegou aqui, a licença é válida - continua execução normal
; (Opcional: salvar token de licença para cache offline)

; ============================================================================
; CÓDIGO ORIGINAL DO USUÁRIO (começa aqui)
; ============================================================================

#Include performace.ahk

IniRead, leter, %A_WorkingDir%\config.ini, Teclas, youtube
IniRead, abc, %A_WorkingDir%\config.ini, Teclas, abc
HotKey, %leter%, IniciarYoutube

return

IniciarYoutube:
	IniRead, conection, %A_WorkingDir%\config.ini, IPS, IP
	url= %conection%
	RunWait, ping.exe %url% -n 1,, Hide UseErrorlevel
	If (Errorlevel){
		SoundSet, 10
		Progress, CTRED b fs15 fm12 zh0 w1360, FALHA NA CONEXAO COM A INTERNET `n POR FAVOR TENTE NOVAMENTE MAIS TARDE.,,Countdowner
		WinSet, TransColor, 000000 240, Countdowner
		Sleep 7000
		Progress, Off
		 SoundSet, 10
		 SendInput, {break}
		 Reload
	 }else{
Send, % abc
Sleep, 500
Run, %A_WorkingDir%\Comandos.exe
Run, %A_WorkingDir%\blocked_Inicio.exe
SetTimer, AfterBox, -50
	FileRead Files, %A_WorkingDir%\Psrockola\Credits.txt
	IniRead, Minute, %A_WorkingDir%\config.ini, times, noteiro_A_time
	File := Trim(Files, "`r`n `t")
	Total := Floor(Minute / 60 * Files)
if(File<=0){
Msgbox, 65, % Title := "EA YOUTUBE SYSTEM", PARA INICIAR O YOUTUBE PRECIONE OK.
}else{
Msgbox, 65, % Title := "EA YOUTUBE SYSTEM", PARA INICIAR E CONVERTER %File% CREDITOS EM %Total% MINUTOS PARA O YOUTUBE PRECIONE OK.
}
AfterBox:
While ( WinExist(Title) )
{
	WinGet, MinMax, MinMax, %Title%
	If (MinMax == -1)
		WinRestore, %Title%
	If ( !WinActive(Title) )
		WinActivate, %Title%
	Sleep, 100
}
	IfMsgBox OK
	Send, @
	IfMsgBox Cancel
	Process, close, Comandos.exe
	Process, close, blocked_Inicio.exe
return

@::
process, close, psrockola4.exe
Sleep, 500
if(File <= 0 ){
Send, !{z}
}else{
	FileRead Files, %A_WorkingDir%\Psrockola\Credits.txt
	IniRead, Minute, %A_WorkingDir%\config.ini, times, noteiro_A_time
	File := Trim(Files, "`r`n `t")
	Total := Floor(Minute / 60 * File * 60)
	fConversao = %A_WorkingDir%\timeBar.txt
	IniRead, currentCount, %fConversao%, Tempo, keepCount
	currentCount += %Total%
	IniWrite, %currentCount%, %fConversao%, Tempo, keepCount
		file := FileOpen("Psrockola\Credits.txt", "w")
		file.write("0")
		file.close()
Sleep, 500
	FileRead Creditos, %A_WorkingDir%\Psrockola\Credits.txt
	IniRead, Minutos, %A_WorkingDir%\timeBar.txt, Tempo, keepCount
	Minutos := Floor(Minutos/60)
			Progress, CTgreen b fs14 fm12 zh0 w1360,   CONVERTIDO COM SUCESSO VOCE TEM %Minutos% MINUTOS PARA O YOUTUBE!,,Notificatios_new
			WinSet, TransColor, 000000 255, Notificatios_new
			Sleep, 5000
			Progress, Off
			Progress, CTgreen b fs40 fm12 zh0 w1360,   INICIANDO O YOUTUBE,,Notificatios_new
			WinSet, TransColor, 000000 180, Notificatios_ne5w
			Sleep, 3000
			Progress, Off
			Send, !{z}
			return
	}
}
	return

SoundSet, 9
	Process, Exist, brave.exe
	NewPID = %errorlevel%
	if (%errorlevel% <> 0){
		Loop{
		Process, close, brave.exe
	}
	}else{
!z:: ;test key3737777
	Suspend On
	testkey := A_ThisHotkey
	wait4time = 2000
	start := A_TickCount
	end := (start + wait4time)
	loop
	{	if (!Getkeystate(testkey,"p"))
			break
	}
	if (A_Tickcount < end)
	{	gosub part1
	}
	else
	{	gosub part2
	}
	Suspend Off
	return

part1:
	dur := (A_Tickcount - start)
	Sleep,500
	process, close, brave.exe
	process, close, psrockola4.exe
	Sleep, 500
	Process, close, blocked_Inicio.exe
	Process, close, Comandos.exe
	Process, close, ouvinteCreditos.exe
	Process, Exist, creditos.exe
	NewPID = %errorlevel%
	if (%errorlevel% <> 0){
		SendInput, {break}
		Reload
	}
	Run, %A_WorkingDir%\creditos.exe
	Sleep, 500
	Run, %A_WorkingDir%\youtube.exe
	Sleep, 7000
	MouseMove, 1367, 0
	BlockInput, MouseMove
	Run, %A_WorkingDir%\notificationbar.exe
	Sleep, 500
	process, close, psrockola4.exe
	Sleep, 5000
	Run, %A_WorkingDir%\tmeOut.exe
	Sleep, 500
	SoundSet, 5
	Sleep, 15000
	Run, %A_WorkingDir%\botaoB.exe
	Run, %A_WorkingDir%\closeSystemYoutube.exe
	Sleep, 500
	ExitApp
	return

part2:
	dur := (A_Tickcount - start)
	process, close, brave.exe
	Sleep,500
	Run, "%A_WorkingDir%\Psrockola\psrockola4.exe"
	return

Shift::
suspend permit
exitapp
return





