param (
    [string]$source
)

# If no path is provided, exit with an error message
if (-not $source) {
    Write-Host "Error: File '$source' not found."
    exit 1
}

# Ensure the provided path exists
if (-not (Test-Path $source -PathType Leaf)) {
    Write-Host "Error: File '$source' not found."
    exit 1
}

# Create shortcut in the user's Startup folder
$shell = New-Object -ComObject WScript.Shell
$startupFolder = $shell.SpecialFolders.Item("Startup")
$shortcut = "$startupFolder\Dextop.lnk"

$s = $shell.CreateShortcut($shortcut)
$s.TargetPath = (Get-Item $source).FullName
$s.WorkingDirectory = (Get-Item $source).DirectoryName
$s.Save()
