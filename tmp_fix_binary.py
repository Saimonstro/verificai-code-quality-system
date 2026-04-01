import os

file_path = r"k:\Trabalho\Hitss\VerificAI\verificai-code-quality-system\backend\app\api\v1\general_analysis.py"

with open(file_path, 'rb') as f:
    content = f.read()

target = b"request.dict(exclude_unset=True)"
idx = content.find(target)

if idx != -1:
    print(f"Found at byte {idx}")
    line_number = content[:idx].count(b'\n') + 1
    print(f"Calculated line number: {line_number}")
    
    new_content = content[:idx] + b"request.model_dump()" + content[idx+len(target):]
    with open(file_path, 'wb') as f:
        f.write(new_content)
    print("Success: Replaced in binary mode.")
else:
    print("Error: String not found even in binary mode.")
    # Search for just "request.dict" to see what's there
    idx2 = content.find(b"request.dict")
    if idx2 != -1:
        print(f"Found 'request.dict' at byte {idx2}. Around: {content[idx2:idx2+50]!r}")
    else:
        print("Even 'request.dict' not found.")
