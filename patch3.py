app_py = "/workspace/whisper-diarization/app.py"
with open(app_py, "r") as f:
    content = f.read()

css_append = """
/* White Checkmarks */
.checkbox-group input[type="checkbox"]:checked,
label input[type="checkbox"]:checked {
    accent-color: #ffffff !important;
}
.checkbox-group input[type="checkbox"]:checked + *,
label input[type="checkbox"]:checked + * {
    color: #ffffff !important;
}
.checkbox-group svg, label input[type="checkbox"]:checked ~ svg {
    stroke: #ffffff !important;
    color: #ffffff !important;
    fill: #ffffff !important;
}
.checkbox-group label.selected,
label.selected {
    border-color: #ffffff !important;
}
"""

if "/* White Checkmarks */" not in content:
    content = content.replace("CUSTOM_CSS = \"\"\"", f'CUSTOM_CSS = """\n{css_append}')

with open(app_py, "w") as f:
    f.write(content)
