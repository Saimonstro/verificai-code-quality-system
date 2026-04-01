import os

file_path = r"k:\Trabalho\Hitss\VerificAI\verificai-code-quality-system\backend\app\api\v1\general_analysis.py"

encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
found = False
for enc in encodings:
    try:
        with open(file_path, 'r', encoding=enc) as f:
            content = f.read()
        if "request.dict(exclude_unset=True)" in content:
            print(f"Match found using encoding: {enc}")
            new_content = content.replace("request.dict(exclude_unset=True)", "request.model_dump()")
            with open(file_path, 'w', encoding=enc) as fw:
                fw.write(new_content)
            print("Successfully replaced with request.model_dump()")
            found = True
            break
    except Exception as e:
        print(f"Failed with {enc}: {e}")
        continue

if not found:
    print("Could not find the target string with any common encoding.")
    # Show first 500 chars to debug
    try:
        with open(file_path, 'rb') as f:
            print(f"Hex start of file: {f.read(20).hex()}")
    except:
        pass
