[Setup]
; Basic Setup Info
AppName=BATMAN V3
AppVersion=3.0
AppPublisher=Mạnh Mế (Shinii Team)
DefaultDirName={autopf}\BATMAN V3
DefaultGroupName=BATMAN V3
OutputDir=dist
OutputBaseFilename=Setup_BATMAN_v3
SetupIconFile=..\..\assets\icon.ico
Compression=lzma2/ultra
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\BATMAN V3.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\BATMAN V3.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\BATMAN V3"; Filename: "{app}\BATMAN V3.exe"
Name: "{group}\{cm:UninstallProgram,BATMAN V3}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\BATMAN V3"; Filename: "{app}\BATMAN V3.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\BATMAN V3.exe"; Description: "{cm:LaunchProgram,BATMAN V3}"; Flags: nowait postinstall skipifsilent
