import sys

ZERO = "\u200B"
ONE = "\u200C"

def invisible_to_bits(data):
    return ''.join('1' if c == ONE else '0' for c in data)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    result = ""
    for b in chars:
        if len(b) == 8:
            result += chr(int(b, 2))
    return result

file_name = sys.argv[1]

with open(file_name, "r", encoding="utf-8") as f:
    content = f.read()

hidden_chars = ''.join(c for c in content if c in (ZERO, ONE))

if not hidden_chars:
    print("No hidden data found.")
    exit()

bits = invisible_to_bits(hidden_chars)
original_code = bits_to_text(bits)

if not original_code.strip():
    print("Recovery failed. Hidden data corrupted.")
    exit()

with open(file_name, "w", encoding="utf-8") as f:
    f.write(original_code)

print("Original code restored successfully.")
