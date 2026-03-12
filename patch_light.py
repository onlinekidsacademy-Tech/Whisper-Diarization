import re

app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    content = f.read()

LIGHT_CSS = '''CUSTOM_CSS = """
/* Premium Light / White Theme */

/* Enforce Light Mode over Dark Mode variables */
body, .gradio-container, .dark, .dark body, .dark .gradio-container, .gr-blocks {
    background-color: #f8fafc !important;
    background-image: none !important;
    color: #0f172a !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* Cards & Panels */
.gr-box, .gr-panel, fieldset, .gr-block, .dark .gr-box, .dark .gr-panel, .dark fieldset, .dark .gr-block {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05) !important;
}

/* Text elements */
h1, h2, h3, h4, h5, h6, .gr-form-label, label, p, span, .dark h1, .dark h2, .dark h3, .dark label, .dark p, .dark span, .gr-text-input {
    color: #0f172a !important;
}
span.text-gray-500, .dark span.text-gray-500 {
    color: #475569 !important;
}

/* Input Fields */
input, textarea, select, .gr-input, .dark input, .dark textarea, .dark select, .dark .gr-input {
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 8px !important;
    box-shadow: inset 0 1px 2px rgb(0 0 0 / 0.05) !important;
}

input:focus, textarea:focus, select:focus, .gr-input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    outline: none !important;
}

/* Tabs */
.gr-tabs > div > button, .dark .gr-tabs > div > button {
    color: #64748b !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    margin-right: 8px !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.2s ease !important;
}
.gr-tabs > div > button.selected, .dark .gr-tabs > div > button.selected {
    color: #2563eb !important;
    border-bottom: 2px solid #2563eb !important;
    background: #eff6ff !important;
}
.gr-tabs > div > button:hover:not(.selected) {
    color: #0f172a !important;
    background: #f1f5f9 !important;
}

/* File Upload */
.gr-file-upload, .dark .gr-file-upload {
    background: #f8fafc !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}
.gr-file-upload:hover {
    border-color: #3b82f6 !important;
    background: #eff6ff !important;
}

/* Primary Button */
button.primary, .gr-button-primary, .dark .gr-button-primary {
    background: linear-gradient(to right, #3b82f6, #2563eb) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.4) !important;
    transition: all 0.2s ease !important;
}
button.primary:hover, .gr-button-primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 8px -1px rgba(59, 130, 246, 0.5) !important;
    background: linear-gradient(to right, #2563eb, #1d4ed8) !important;
}

/* Secondary Button */
button.secondary, .gr-button-secondary, .dark .gr-button-secondary {
    background: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
button.secondary:hover, .gr-button-secondary:hover {
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
}

/* Checkboxes */
input[type="checkbox"], .dark input[type="checkbox"] {
    accent-color: #3b82f6 !important;
}
.gr-checkbox-label, .dark .gr-checkbox-label {
    color: #0f172a !important;
}

/* Form Elements */
.gr-dropdown, .dark .gr-dropdown {
    background: #f1f5f9 !important;
}
.gr-dropdown-item:hover, .dark .gr-dropdown-item:hover {
    background: #e2e8f0 !important;
    color: #0f172a !important;
}

/* Scrollbars */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 4px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
"""'''

def replacer(match):
    return LIGHT_CSS

new_content = re.sub(r'CUSTOM_CSS\s*=\s*""".*?"""', replacer, content, flags=re.DOTALL)

with open(app_py, "w") as f:
    f.write(new_content)

print("CSS Patched for Light Theme.")
