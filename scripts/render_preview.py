"""Generate HTML preview of README.md with GitHub Dark theme."""
from pathlib import Path

import markdown

readme_text = Path("README.md").read_text(encoding="utf-8")
html_body = markdown.markdown(readme_text, extensions=["tables", "fenced_code", "md_in_html", "extra"])

css = """
body {
    background-color: #080F1F;
    color: #A5B4CF;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    margin: 0 auto;
    max-width: 900px;
    padding: 32px 16px;
}
a { color: #38BDF8; text-decoration: none; }
a:hover { text-decoration: underline; }
h1, h2, h3, h4 { color: #F4F7FF; border-bottom: 1px solid #293B59; padding-bottom: 6px; }
h3, h4 { border-bottom: none; }
hr { border: 0; border-top: 1px solid #293B59; margin: 24px 0; }
code {
    background-color: #17243C;
    border: 1px solid #293B59;
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, monospace;
    font-size: 85%;
    padding: 0.2em 0.4em;
    color: #38BDF8;
}
table {
    border-collapse: separate;
    border-spacing: 0;
    width: 100%;
    margin-bottom: 16px;
    border: 1px solid #293B59;
    border-radius: 12px;
    background-color: #111C31;
    overflow: hidden;
}
th, td {
    border: 1px solid #293B59;
    padding: 14px 16px;
}
th { background-color: #17243C; color: #F4F7FF; }
ul { padding-left: 20px; }
li { margin: 4px 0; }
img { max-width: 100%; border-radius: 8px; }
blockquote {
    border-left: 4px solid #8B5CF6;
    background-color: #17243C;
    border-radius: 4px;
    color: #A5B4CF;
    padding: 8px 16px;
    margin: 12px 0;
}
"""

template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Profile README — Rendered Preview</title>
    <style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>
"""

Path("preview.html").write_text(template, encoding="utf-8")
print("Rendered preview.html successfully!")
