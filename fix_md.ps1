$content = Get-Content -Raw "D:\Scraping_Anichin_Reborn\redesign.md"

# Step 1: Normalize line endings and trim trailing spaces
$lines = $content -split "`r?`n" | ForEach-Object { $_.TrimEnd() }

$result = [System.Text.StringBuilder]::new()

$prevBlank = $false

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    $isBlank = ($line -match '^\s*$')
    
    # Collapse multiple blank lines into one
    if ($isBlank) {
        if (-not $prevBlank) {
            [void]$result.AppendLine("")
            $prevBlank = $true
        }
        continue
    }
    $prevBlank = $false
    
    # Detect setext H1 heading (=== underline)
    if ($line -match '^[=\-]{3,}\s*$') {
        # Look ahead for the heading text (it's above this line)
        # In setext style, the text comes BEFORE the === line
        # But we need to find the preceding non-blank line(s)
        # Actually in the file, setext headings have the text on the line BEFORE ===
        # Let's handle this differently - process when we see the === line
        # and look back for the heading text
        $headingText = ""
        for ($j = $i - 1; $j -ge 0; $j--) {
            if ($lines[$j] -match '^\s*$') {
                break
            }
            $headingText = $lines[$j]
        }
        if ($headingText -and $headingText.Trim()) {
            $headingText = $headingText.Trim()
            # Check if next non-blank line after === is also ===
            # This is a setext H1
            if ($headingText -ne "==========================================" -or $i -gt 0) {
                # Insert blank line before heading
                if ($result.Length -gt 0) { [void]$result.AppendLine("") }
                # Insert ATX H1
                [void]$result.AppendLine("# $headingText")
                # Skip the === line
                # Don't set prevBlank - the heading line is not blank
                $prevBlank = $false
                continue
            }
        }
    }
    
    # Fix ATX headings missing space after #
    if ($line -match '^#{1,6}[^\s#]') {
        $line = $line -replace '^(#{1,6})([^\s#])', '$1 $2'
    }
    
    # Convert + to - for unordered lists (at start of line)
    if ($line -match '^(\s*)\+\s') {
        $line = $line -replace '^(\s*)\+\s', '$1- '
    }
    
    # Wrap bare URLs in angle brackets
    if ($line -match '(?<![\w])(https?://\S+)(?![\w])' -and $line -notmatch '<https?://') {
        $matchesFound = [regex]::Matches($line, '(?<![\w])(https?://\S+)')
        foreach ($m in $matchesFound) {
            $url = $m.Value
            # Don't wrap if already in quotes or brackets
            $idx = $line.IndexOf($url)
            if ($idx -gt 0 -and $line[$idx-1] -in '"', "'", '<', ')') { continue }
            $line = $line.Replace($url, "<$url>", 1)
        }
    }
    
    [void]$result.AppendLine($line)
}

# Ensure single trailing newline
$output = $result.ToString().TrimEnd() + "`n"

Set-Content -Path "D:\Scraping_Anichin_Reborn\redesign.md" -Value $output -Encoding UTF8
Write-Output "Done. Lines: $($output -split '`n').Count"
