"""Generate HTML preview of README.md with GitHub Dark theme."""
from pathlib import Path

import markdown

readme_text = Path("README.md").read_text(encoding="utf-8")
html_body = markdown.markdown(readme_text, extensions=["tables", "fenced_code"])

css = """
body {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    margin: 0 auto;
    max-width: 860px;
    padding: 32px 16px;
}
a { color: #58a6ff; text-decoration: none; }
a:hover { text-decoration: underline; }
h1, h2, h3, h4 { color: #f0f6fc; border-bottom: 1px solid #21262d; padding-bottom: 6px; }
h3, h4 { border-bottom: none; }
hr { border: 0; border-top: 1px solid #30363d; margin: 24px 0; }
code {
    background-color: rgba(110, 118, 129, 0.4);
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, monospace;
    font-size: 85%;
    padding: 0.2em 0.4em;
    color: #e6edf3;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
    border: 1px solid #30363d;
    border-radius: 6px;
    background-color: #161b22;
}
th, td {
    border: 1px solid #30363d;
    padding: 12px 14px;
}
th { background-color: #21262d; color: #f0f6fc; }
ul { padding-left: 20px; }
li { margin: 4px 0; }
img { max-width: 100%; border-radius: 6px; }
blockquote {
    border-left: 4px solid #388bfd;
    color: #8b949e;
    padding: 0 16px;
    margin: 0;
}
"""

template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
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
