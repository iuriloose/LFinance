#define MyAppName "LFinance"
#define MyAppVersion "2.1.11"
#define MyAppPublisher "Iuri Loose"
#define MyAppExeName "LFinance.exe"

#ifndef MyAppSourceDir
  #define MyAppSourceDir "dist\LFinance"
#endif

#ifndef MyOutputDir
  #define MyOutputDir "instalador"
#endif

[Setup]
AppId={{B2C8F9A7-5E6B-4F2F-9C6D-2B4B7F8A1D23}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#MyOutputDir}
OutputBaseFilename=LFinance_Setup_v2.1.11
SetupIconFile=assets\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Sistema de gerenciamento financeiro pessoal
VersionInfoProductName=LFinance
VersionInfoCopyright=© 2026 Iuri Loose. Todos os direitos reservados.
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "VERSION.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_EXE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\LFinance"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar LFinance"; Filename: "{uninstallexe}"
Name: "{autodesktop}\LFinance"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir o LFinance"; Flags: nowait postinstall skipifsilent runasoriginaluser
