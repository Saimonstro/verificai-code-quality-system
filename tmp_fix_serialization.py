import sys
import os

file_path = r"k:\Trabalho\Hitss\VerificAI\verificai-code-quality-system\backend\app\api\v1\general_analysis.py"
if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    sys.exit(1)

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

new_lines = []
replaced_count = 0
for line in lines:
    if "request.dict(exclude_unset=True)" in line:
        new_line = line.replace("request.dict(exclude_unset=True)", "request.model_dump()")
        new_lines.append(new_line)
        replaced_count += 1
    else:
        new_lines.append(line)

if replaced_count > 0:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Successfully replaced {replaced_count} occurrences.")
else:
    print("No occurrences found to replace.")
