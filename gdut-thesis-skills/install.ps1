$ErrorActionPreference = "Stop"
$SourceDir = Join-Path $PSScriptRoot "plugins/gdut-thesis-workflow/skills"
if ($env:CLAUDE_SKILLS_DIR) {
    $DestDir = $env:CLAUDE_SKILLS_DIR
} else {
    $DestDir = Join-Path $HOME ".claude/skills"
}
New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
Copy-Item -Path (Join-Path $SourceDir "*") -Destination $DestDir -Recurse -Force
Write-Host "Installed GDUT thesis workflow skills to: $DestDir"
