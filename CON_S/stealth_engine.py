ZERO = "\u200B"
ONE = "\u200C"

def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(b, 2)) for b in chars if len(b) == 8)

def bits_to_invisible(bits):
    return ''.join(ONE if b == '1' else ZERO for b in bits)

def invisible_to_bits(data):
    return ''.join('1' if c == ONE else '0' for c in data)
