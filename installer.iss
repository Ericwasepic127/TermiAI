#define AppId "io.github.ericwasepic127.terminal-assistant-interface"
#define AppExe "termiai-windows.exe"
#define BuildDir "build\windows"

#define AppExePath AddBackslash(SourcePath) + BuildDir + "\" + AppExe
#define ArtifactName Copy(AppExe, 1, Len(AppExe) - 4)
#if !FileExists(AppExePath)
  #error AppExe is not in BuildDir: run "flet pack" first, or fix the values above.
#endif
#define AppName GetStringFileInfo(AppExePath, "ProductName")
#define AppPublisher GetStringFileInfo(AppExePath, "CompanyName")
#define FullVersion GetStringFileInfo(AppExePath, "ProductVersion")
#define AppVersion Copy(FullVersion, 1, Pos("+", FullVersion + "+") - 1)

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoVersion={#GetVersionNumbersString(AppExePath)}
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExe}
DefaultDirName={autopf}\{code:SafeAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern dynamic
SetupIconFile=build\flutter\windows\runner\resources\app_icon.ico
OutputDir=build\installer
OutputBaseFilename={#StringChange(ArtifactName, " ", "-")}-{#AppVersion}-setup
SolidCompression=yes

[Tasks]
Name: desktopicon; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
Type: filesandordirs; Name: "{app}\app"; Check: IsUpgrade
Type: filesandordirs; Name: "{app}\data"; Check: IsUpgrade
Type: filesandordirs; Name: "{app}\DLLs"; Check: IsUpgrade
Type: filesandordirs; Name: "{app}\Lib"; Check: IsUpgrade
Type: filesandordirs; Name: "{app}\site-packages"; Check: IsUpgrade
Type: files; Name: "{app}\*.dll"; Check: IsUpgrade

[Files]
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{code:SafeAppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{code:SafeAppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function SafeAppName(Param: String): String;
var
  I: Integer;
begin
  Result := '{#StringChange(AppName, "'", "''")}';
  for I := Length(Result) downto 1 do
    if Pos(Result[I], '\/:*?"<>|') > 0 then
      Delete(Result, I, 1);
end;

function IsUpgrade: Boolean;
begin
  Result := CompareText(RemoveBackslash(WizardForm.PrevAppDir), RemoveBackslash(WizardDirValue)) = 0;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Rec: TFindRec;
begin
  Result := True;
  if (CurPageID = wpSelectDir) and not IsUpgrade and FindFirst(AddBackslash(WizardDirValue) + '*', Rec) then
  try
    repeat
      if (Rec.Name <> '.') and (Rec.Name <> '..') then
      begin
        SuppressibleMsgBox(WizardDirValue + ' already contains files. Choose an empty or new folder.', mbError, MB_OK, IDOK);
        Result := False;
        Break;
      end;
    until not FindNext(Rec);
  finally
    FindClose(Rec);
  end;
end;
