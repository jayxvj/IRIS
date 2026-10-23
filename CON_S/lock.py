import sys

ZERO = "\u200B"
ONE = "\u200C"

def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bits_to_invisible(bits):
    return ''.join(ONE if b == '1' else ZERO for b in bits)

file_name = sys.argv[1]

with open(file_name, "r", encoding="utf-8") as f:
    original = f.read()

bits = text_to_bits(original)
hidden_stream = bits_to_invisible(bits)

game_code = """
# =====================================
# MAZE ESCAPE GAME ENGINE 🎮
# =====================================

import random
print("Welcome to Maze Escape!")
print("Roll dice to move...")
"""

# Add separator (normal newline)
final_code = game_code + "\n" + hidden_stream

with open(file_name, "w", encoding="utf-8") as f:
    f.write(final_code)

print("File locked successfully.")
