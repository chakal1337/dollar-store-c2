$WshShell = New-Object -comObject WScript.Shell
$wd = $pwd.Path
$wd = $wd + "\linkdir\Link.lnk"
$Shortcut = $WshShell.CreateShortcut($wd)
$Shortcut.TargetPath = 'C:\Windows\system32\cmd.exe'
$Shortcut.IconLocation = $pwd.Path + "\icon.ico"
$Shortcut.Arguments = '/c {COMMAND}'
$Shortcut.Save()