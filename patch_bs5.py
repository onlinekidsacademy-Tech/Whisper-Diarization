import re

app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    content = f.read()

# Replace CUSTOM_CSS and DARK_THEME definition
BS5_CSS = '''CUSTOM_CSS = """
/* Bootstrap 5 Mimic Theme for Gradio */

:root {
  --bs-blue: #0d6efd;
  --bs-primary: #0d6efd;
  --bs-secondary: #6c757d;
  --bs-success: #198754;
  --bs-body-bg: #f8f9fa;
  --bs-body-color: #212529;
  --bs-border-color: #dee2e6;
  --bs-border-radius: 0.375rem;
  --bs-box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  --bs-font-sans-serif: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif;
}

body, .gradio-container, .gr-blocks {
    background-color: var(--bs-body-bg) !important;
    background-image: none !important;
    color: var(--bs-body-color) !important;
    font-family: var(--bs-font-sans-serif) !important;
}

/* Cards (gr-box/panel) */
.gr-box, .gr-panel, fieldset, .gr-block {
    background-color: #ffffff !important;
    border: 1px solid var(--bs-border-color) !important;
    border-radius: var(--bs-border-radius) !important;
    box-shadow: var(--bs-box-shadow) !important;
}

/* Typography elements */
h1, h2, h3, h4, h5, h6, .gr-form-label, label, p, span {
    color: var(--bs-body-color) !important;
}

/* Form Controls (Inputs, Textarea, Select) */
input, textarea, select, .gr-input, .gr-dropdown {
    display: block !important;
    width: 100% !important;
    padding: 0.375rem 0.75rem !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    color: var(--bs-body-color) !important;
    background-color: #fff !important;
    background-clip: padding-box !important;
    border: 1px solid #ced4da !important;
    appearance: none !important;
    border-radius: var(--bs-border-radius) !important;
    transition: border-color .15s ease-in-out,box-shadow .15s ease-in-out !important;
    box-shadow: none !important;
}

input:focus, textarea:focus, select:focus, .gr-input:focus {
    color: var(--bs-body-color) !important;
    background-color: #fff !important;
    border-color: #86b7fe !important;
    outline: 0 !important;
    box-shadow: 0 0 0 0.25rem rgba(13,110,253,.25) !important;
}

/* Primary Button (btn-primary) */
button.primary, .gr-button-primary {
    color: #fff !important;
    background-color: var(--bs-primary) !important;
    border-color: var(--bs-primary) !important;
    display: inline-block !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    text-align: center !important;
    text-decoration: none !important;
    vertical-align: middle !important;
    cursor: pointer !important;
    user-select: none !important;
    border: 1px solid transparent !important;
    padding: 0.375rem 0.75rem !important;
    font-size: 1rem !important;
    border-radius: var(--bs-border-radius) !important;
    transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out !important;
    box-shadow: none !important;
}
button.primary:hover, .gr-button-primary:hover {
    color: #fff !important;
    background-color: #0b5ed7 !important;
    border-color: #0a58ca !important;
}
button.primary:active, .gr-button-primary:active {
    background-color: #0a58ca !important;
    border-color: #0a53be !important;
    box-shadow: inset 0 3px 5px rgba(0, 0, 0, 0.125) !important;
}

/* Secondary Button (btn-secondary/btn-outline) */
button.secondary, .gr-button-secondary {
    color: var(--bs-secondary) !important;
    background-color: transparent !important;
    border: 1px solid var(--bs-secondary) !important;
    display: inline-block !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    text-align: center !important;
    text-decoration: none !important;
    padding: 0.375rem 0.75rem !important;
    font-size: 1rem !important;
    border-radius: var(--bs-border-radius) !important;
    transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out !important;
}
button.secondary:hover, .gr-button-secondary:hover {
    color: #fff !important;
    background-color: var(--bs-secondary) !important;
    border-color: var(--bs-secondary) !important;
}

/* Tabs (nav-tabs style) */
.gr-tabs > div > button {
    color: var(--bs-primary) !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-top-left-radius: var(--bs-border-radius) !important;
    border-top-right-radius: var(--bs-border-radius) !important;
    margin-bottom: -1px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 400 !important;
}
.gr-tabs > div > button.selected {
    color: #495057 !important;
    background-color: #fff !important;
    border-color: #dee2e6 #dee2e6 #fff !important;
}
.gr-tabs > div > button:hover:not(.selected) {
    border-color: #e9ecef #e9ecef #dee2e6 !important;
}
.gr-tabs {
    border-bottom: 1px solid #dee2e6 !important;
}

/* Checkbox (form-check-input) */
input[type="checkbox"] {
    width: 1em !important;
    height: 1em !important;
    margin-top: 0.25em !important;
    vertical-align: top !important;
    background-color: #fff !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: contain !important;
    border: 1px solid rgba(0,0,0,.25) !important;
    appearance: none !important;
    border-radius: 0.25em !important;
}
input[type="checkbox"]:checked {
    background-color: var(--bs-primary) !important;
    border-color: var(--bs-primary) !important;
}

/* File Upload Area */
.gr-file-upload {
    background-color: #f8f9fa !important;
    border: 2px dashed #dee2e6 !important;
    border-radius: var(--bs-border-radius) !important;
    transition: background-color 0.2s ease !important;
}
.gr-file-upload:hover {
    background-color: #e2e3e5 !important;
    border-color: #adb5bd !important;
}

/* Header */
.app-header h1 {
    font-weight: 500 !important;
    margin-bottom: 0.5rem !important;
    line-height: 1.2 !important;
    font-size: 2.5rem !important;
}
.app-header p {
    font-size: 1.25rem !important;
    font-weight: 300 !important;
    color: #6c757d !important;
}
"""
BS5_THEME = gr.themes.Base()
'''

content = re.sub(r'CUSTOM_CSS\s*=\s*""".*?"""', BS5_CSS.split("BS5_THEME")[0].strip() + "\n", content, flags=re.DOTALL)
content = re.sub(r'DARK_THEME\s*=\s*gr.*?shadow_drop="none",\s*\)', 'BS5_THEME = gr.themes.Base()', content, flags=re.DOTALL)
content = content.replace("theme=DARK_THEME", "theme=BS5_THEME")

with open(app_py, "w") as f:
    f.write(content)
print("Bootstrap 5 Patch Applied Successfully.")
