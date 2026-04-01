import os

file_path = r"k:\Trabalho\Hitss\VerificAI\verificai-code-quality-system\backend\app\api\v1\general_analysis.py"

with open(file_path, 'rb') as f:
    content = f.read()

# Search for any .dict( usage
target = b".dict("
pos = 0
found = False
while True:
    idx = content.find(target, pos)
    if idx == -1: break
    found = True
    context = content[max(0, idx-50):idx+100]
    print(f"Match at byte {idx}: {context!r}")
    pos = idx + 1

if not found:
    print("No '.dict(' found in binary.")
    # Show first 500 bytes to check encoding/file start
    print(f"First 500 bytes: {content[:500]!r}")
