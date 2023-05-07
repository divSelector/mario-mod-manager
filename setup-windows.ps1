#!/usr/bin/env pwsh

function downloadZipFromGit {
    $homeDir = [Environment]::GetFolderPath('UserProfile')

    New-Item -ItemType Directory -Path "$homeDir\smwcentral-scraper"

    Set-Location -Path "$homeDir\smwcentral-scraper"

    Invoke-WebRequest -Uri 'https://github.com/divSelector/smwcentral-scraper/archive/refs/heads/main.zip' -OutFile 'smwcentral-scraper.zip'
	
	Expand-Archive -Path "smwcentral-scraper.zip" -DestinationPath "$HOME\smwcentral-scraper"
	
	Get-ChildItem -Directory | Select-Object -First 1 | Set-Location
	
	Remove-Item ..\smwcentral-scraper.zip

	Get-ChildItem -Recurse | Move-Item -Destination ..

	Set-Location ..
	
	Get-ChildItem -Directory | Where-Object { (Get-ChildItem $_.FullName -Recurse -Force).Count -eq 0 } | Remove-Item -Recurse -Force
}


function setupVirtualEnv {
	
	py -m pip install virtualenv
	
	py -m virtualenv venv
	
	.\venv\Scripts\activate
	
	py -m pip install --upgrade pip
	
	py -m pip install -r .\requirements.txt
}


#downloadZipFromGit
setupVirtualEnv
