$f = "config\settings.py"
$c = Get-Content $f -Raw

$old = @'
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "apps" / "layout" / "templates",
        ],
'@

$new = @'
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "apps" / "layout" / "templates",
            BASE_DIR / "apps" / "authentication" / "presentation" / "templates",
            BASE_DIR / "apps" / "user" / "presentation" / "templates",
            BASE_DIR / "apps" / "key" / "presentation" / "templates",
            BASE_DIR / "apps" / "knowledge" / "presentation" / "templates",
            BASE_DIR / "apps" / "notification" / "presentation" / "templates",
        ],
'@

if ($c.Contains($old)) {
    $c = $c.Replace($old, $new)
    Set-Content $f $c -NoNewline -Encoding UTF8
    Write-Host "[OK] settings.py updated" -ForegroundColor Green
} else {
    Write-Host "[!!] pattern not found — แก้มือ" -ForegroundColor Yellow
}