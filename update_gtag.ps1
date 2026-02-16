$files = Get-ChildItem -Path "f:\dev\Project3\elevate_aura_bot" -Filter "*.html" -Recurse

foreach ($file in $files) {
    if ($file.Name -eq "update_gtag.ps1") { continue }
    
    $content = Get-Content -Path $file.FullName -Raw
    
    if ($content -match "AW-765151521") {
        # Replace the tracking ID everywhere (config, src url, send_to prefix)
        $content = $content -replace "AW-765151521", "AW-17956207834"
        
        # Replace the old conversion label with the new one
        $content = $content -replace "WvxrCJvg2_kbEKGS7ewC", "ipDyCInL2fkbENr5l_JC"
        
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8
        Write-Host "Updated $($file.FullName)"
    }
}
