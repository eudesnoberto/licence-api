#SingleInstance,Force

; ============================================================================
; PROTEÇÃO DE LICENÇA - Verifica antes de continuar
; ============================================================================
#Include license_check.ahk

; Se chegou aqui, a licença é válida - continua execução normal

; ============================================================================
; SEU CÓDIGO ORIGINAL (sem modificações)
; ============================================================================

#Include performace.ahk

#NoTrayIcon

	Loop, 7{

	WinGetTitle, Title, A

	;MsgBox, The active window is "%Title%".

	myTitle := Title

	myTube := SubStr(Title, 1,13)

	youtubeTv := "YouTube na TV"

	if(myTube = youtubeTv){

		Process, Exist, javaw.exe

		NewPID = %errorlevel%

			if (%errorlevel% <> 0){

		CoordMode, Mouse, Screen

		Loop, 2{

			x := A_ScreenWidth // 2

			y := A_ScreenHeight // 2

			MouseMove, %x%, %y%

			Click

			Sleep, 300

		}

		Sleep, 1000

	; ===== CONFIGURAÇÕES =====

		Send, {Left}

		Sleep, 300

		Loop, 2{

			Send, {Down}

			Sleep, 300

		}

		Send, {Right}

		Sleep, 300

		Loop, 6{

			Send, {Down}

			Sleep, 300

		}

		Sleep, 500

		Run, %A_WorkingDir%\Comandos.exe

			Sleep, 500

		Run, %A_WorkingDir%\blocked.exe

			Sleep, 500

		Run, %A_WorkingDir%\clicks.exe

		Sleep, 500

		ExitApp

			}else{

			Run, %A_WorkingDir%\notification.exe

		}

		Process, Exist, timetemporary.exe

		NewPID = %errorlevel%

			if (%errorlevel% <> 0){

				Send, {Volume_Mute}

			ExitApp

			}

	Run, %A_WorkingDir%\timetemporary.exe

	Process, close, images.exe

	Progress, off

	}else{

	Run, %A_WorkingDir%\images.exe

	Sleep, 3000

	process, close, psrockola4.exe

	;Run, chrome.exe --chrome-frame -kiosk /incognito https://www.youtube.com/tv

	Run, brave.exe --kiosk --start-fullscreen --kiosk --incognito --disable-infobars --disable-session-crashed-bubble --disable-restore-session-state --no-first-run --no-default-browser-check --disable-plugins-discovery --disable-popup-blocking --disable-blink-features=AutomationControlled --disable-features=TranslateUI --disable-ipc-flooding-protection --incognito --profile-directory="Default" "https://www.youtube.com/tv#/browse?c=FElibrary"

	;~Run, msedge.exe --kiosk "https://www.youtube.com/tv#/browse?c=FEmy_youtube" --inprivate --edge-kiosk-type=full

	;~ Run, msedge.exe --kiosk "https://www.youtube.com/tv#/browse?c=FEmy_youtube" --inprivate --edge-kiosk-type=fullscreen

	wdth := (A_ScreenWidth/2)-(Width/2), hght := 455

	Progress,  b fs30 fm12 zh0 CTRED CWFFFFFF X%wdth% Y%hght%  w1330, AGUARDE UM MOMENTO..., ,Youtube

	WinSet, TransColor, 000000 200, Youtube,

	Sleep, 850

	}

	Sleep, 5000

	}

	Send, {F5}

	Reload

	return

Shift::

ExitApp





