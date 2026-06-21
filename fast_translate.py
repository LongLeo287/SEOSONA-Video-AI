import os, re
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='vi', target='en')

root = r'D:\LongLeo\SEOSONA AI\SEOSONA Video'
pattern = re.compile(r'[àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]', re.IGNORECASE)

# 1. Collect all lines with Vietnamese
dirs_to_scan = ['1_AGENTS', '2_SKILLS', '4_BRAIN', '8_WORKSPACE']
lines_to_translate = set()
files_to_modify = []

for d in dirs_to_scan:
    scan_dir = os.path.join(root, d)
    if not os.path.exists(scan_dir): continue
    for dirpath, _, filenames in os.walk(scan_dir):
        for f in filenames:
            if f.endswith('.py'):
                filepath = os.path.join(dirpath, f)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        for line in file:
                            if pattern.search(line):
                                lines_to_translate.add(line)
                                if filepath not in files_to_modify:
                                    files_to_modify.append(filepath)
                except: pass

print(f"Found {len(lines_to_translate)} unique lines to translate in Python files.")

# 2. Bulk translate them (deep_translator allows up to 5000 chars per batch)
translation_map = {}
batch = []
batch_len = 0

def process_batch(b):
    if not b: return
    text_to_trans = "\n|||\n".join(b)
    try:
        translated_text = translator.translate(text_to_trans)
        translated_lines = translated_text.split("|||")
        for orig, trans in zip(b, translated_lines):
            translation_map[orig] = trans.strip() + "\n"
    except Exception as e:
        print("Batch error:", e)
        # Fallback to individual
        for item in b:
            try:
                translation_map[item] = translator.translate(item) + "\n"
            except:
                translation_map[item] = item

for line in lines_to_translate:
    if batch_len + len(line) + 5 > 4500:
        process_batch(batch)
        batch = []
        batch_len = 0
    batch.append(line.rstrip('\n'))
    batch_len += len(line) + 5

if batch: process_batch(batch)

# 3. Replace in files
for filepath in files_to_modify:
    with open(filepath, 'r', encoding='utf-8') as f:
        content_lines = f.readlines()
    
    new_content = []
    for line in content_lines:
        if line in translation_map:
            new_content.append(translation_map[line])
        else:
            new_content.append(line)
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    print(f"Updated {os.path.basename(filepath)}")

print("Done translating Python files!")
