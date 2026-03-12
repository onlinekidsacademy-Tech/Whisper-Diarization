app_py = "/workspace/whisper-diarization/app.py"

with open(app_py, "r") as f:
    content = f.read()

# Fix the invalid syntax for the check color
content = content.replace('    checkbox_check_color="#000000",\n', '')

# Re-add custom CSS that targets ONLY the SVG checkmark inside the checked box without breaking other things
css_append = """
/* White SVG Checkmark override for Gradio */
.checkbox-group input[type="checkbox"]:checked {
    background-color: transparent !important;
}
.checkbox-group input[type="checkbox"]:checked::after {
    content: '' !important;
    position: absolute !important;
    left: 4px !important;
    top: 1px !important;
    width: 6px !important;
    height: 10px !important;
    border: solid #ffffff !important;
    border-width: 0 2px 2px 0 !important;
    transform: rotate(45deg) !important;
}
"""

if "/* White SVG Checkmark override for Gradio */" not in content:
    content = content.replace("CUSTOM_CSS = \"\"\"", f'CUSTOM_CSS = """\n{css_append}')


with open(app_py, "w") as f:
    f.write(content)
