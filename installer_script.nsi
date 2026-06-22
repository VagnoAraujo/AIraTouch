; ══════════════════════════════════════════════════════════════════
;  AIra9Touch v3.0 ULTRA — Script NSIS (Nullsoft Installer)
;  Compilar com: makensis installer_script.nsi
;  Download NSIS: https://nsis.sourceforge.io/Download
; ══════════════════════════════════════════════════════════════════

!define APP_NAME     "AIra9Touch"
!define APP_VERSION  "3.0 ULTRA"
!define APP_EXE      "aira9touch_v3.exe"
!define INSTALL_DIR  "$PROGRAMFILES\AIra9Touch"
!define REG_KEY      "Software\Microsoft\Windows\CurrentVersion\Uninstall\AIra9Touch"

; ── Configurações Gerais ───────────────────────────────────────────
Name              "${APP_NAME} ${APP_VERSION}"
OutFile           "AIra9Touch_v3_Setup.exe"
InstallDir        "${INSTALL_DIR}"
InstallDirRegKey  HKLM "${REG_KEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor     lzma

; ── Interface visual ──────────────────────────────────────────────
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON          "icon.ico"
!define MUI_UNICON        "icon.ico"
!define MUI_HEADERIMAGE
!define MUI_BGCOLOR       "000000"
!define MUI_TEXTCOLOR     "C5A059"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE     "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "PortugueseBR"

; ══════════════════════════════════════════════════════════════════
;  SEÇÃO DE INSTALAÇÃO
; ══════════════════════════════════════════════════════════════════
Section "AIra9Touch v3.0 ULTRA (obrigatório)" SecMain

    SectionIn RO
    SetOutPath "$INSTDIR"

    ; ── Copia todos os arquivos necessários ──────────────────────
    File "${APP_EXE}"
    File /oname=aira9touch_v3.py "aira9touch_v3.py"
    File "requirements.txt"
    File /nonfatal "icon.ico"
    File /nonfatal "LICENSE.txt"
    File "desinstalar_aira9.bat"

    ; ── Atalho no Menu Iniciar ───────────────────────────────────
    CreateDirectory "$SMPROGRAMS\AIra9Touch"
    CreateShortcut  "$SMPROGRAMS\AIra9Touch\AIra9Touch.lnk" \
                    "$INSTDIR\${APP_EXE}" "" "$INSTDIR\icon.ico" 0
    CreateShortcut  "$SMPROGRAMS\AIra9Touch\Desinstalar.lnk" \
                    "$INSTDIR\Uninstall.exe"

    ; ── Atalho na Área de Trabalho ───────────────────────────────
    CreateShortcut  "$DESKTOP\AIra9Touch.lnk" \
                    "$INSTDIR\${APP_EXE}" "" "$INSTDIR\icon.ico" 0

    ; ── Registro do Windows (Add/Remove Programs) ─────────────────
    WriteRegStr   HKLM "${REG_KEY}" "DisplayName"     "${APP_NAME} ${APP_VERSION}"
    WriteRegStr   HKLM "${REG_KEY}" "DisplayVersion"  "${APP_VERSION}"
    WriteRegStr   HKLM "${REG_KEY}" "Publisher"       "AIra9"
    WriteRegStr   HKLM "${REG_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr   HKLM "${REG_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegDWORD HKLM "${REG_KEY}" "NoModify"        1
    WriteRegDWORD HKLM "${REG_KEY}" "NoRepair"        1

    ; ── Desinstalador ────────────────────────────────────────────
    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

; ══════════════════════════════════════════════════════════════════
;  SEÇÃO DE DESINSTALAÇÃO
; ══════════════════════════════════════════════════════════════════
Section "Uninstall"

    ; Para o processo antes de remover
    ExecWait 'taskkill /f /im "${APP_EXE}"'
    ExecWait 'taskkill /f /im pythonw.exe'

    ; Remove arquivos
    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\aira9touch_v3.py"
    Delete "$INSTDIR\requirements.txt"
    Delete "$INSTDIR\icon.ico"
    Delete "$INSTDIR\LICENSE.txt"
    Delete "$INSTDIR\config_v3.json"
    Delete "$INSTDIR\desinstalar_aira9.bat"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir  "$INSTDIR"

    ; Remove atalhos
    Delete "$DESKTOP\AIra9Touch.lnk"
    Delete "$SMPROGRAMS\AIra9Touch\AIra9Touch.lnk"
    Delete "$SMPROGRAMS\AIra9Touch\Desinstalar.lnk"
    RMDir  "$SMPROGRAMS\AIra9Touch"

    ; Remove do início automático (caso estivesse ativo)
    DeleteRegValue HKCU \
        "Software\Microsoft\Windows\CurrentVersion\Run" "AIra9Touch"

    ; Remove do Add/Remove Programs
    DeleteRegKey HKLM "${REG_KEY}"

    MessageBox MB_OK "AIra9Touch desinstalado com sucesso."

SectionEnd
