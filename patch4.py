app_py = "/workspace/whisper-diarization/app.py"
import re

with open(app_py, "r") as f:
    content = f.read()

# 1. Update the Dark Theme definition to explicitly color selected checkboxes white
theme_replace = """    checkbox_background_color_selected="#ffffff",
    checkbox_border_color_selected="#ffffff",
    checkbox_check_color="#000000",
"""
if "checkbox_background_color_selected" not in content:
    content = content.replace("    shadow_spread=\"0px\",", f"    shadow_spread=\"0px\",\n{theme_replace}")

# 2. Remove the custom CSS block I added earlier entirely
content = re.sub(r'/\* White Checkmarks \*/.*?(?=""")', '', content, flags=re.DOTALL)

with open(app_py, "w") as f:
    f.write(content)
