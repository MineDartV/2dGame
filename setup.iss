    [Setup]
AppName=Hero Vs Goblin 
AppVersion=1.0
DefaultDirName={pf}\Hero Vs Goblin
DefaultGroupName=Hero Vs Goblin
OutputBaseFilename=hero_vs_goblin_installer
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\game.ico

[Files]
Source: "dist\game\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Hero Vs Goblin Game"; Filename: "{app}\game.exe"; IconFilename: "{app}\_internal\assets\game.ico"
Name: "{group}\Uninstall Hero Vs Goblin Game"; Filename: "{uninstallexe}"; IconFilename: "{app}\_internal\assets\game.ico"


[Run]
Filename: "{app}\game.exe"; Description: "Launch Hero Vs Goblin Game"; Flags: nowait postinstall skipifsilent