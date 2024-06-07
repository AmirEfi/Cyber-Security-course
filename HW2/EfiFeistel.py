import random
import binascii


# Expands a 64-bit block to 128 bits
def expand(block):
    return ((block & 0xFFFF0000FFFF) << 16) | ((block & 0x0000FFFF0000) << 32) | ((block & 0xFFFF0000FFFF) >> 16)


def sbox(block):
    s_boxes = [
        [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8, 0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7],
        [0xF, 0xC, 0x2, 0x8, 0x4, 0x7, 0x1, 0xA, 0xE, 0xD, 0x0, 0x6, 0x9, 0xB, 0x3, 0x5],
        [0xA, 0x9, 0x8, 0x7, 0x6, 0x5, 0x4, 0x3, 0x2, 0x1, 0x0, 0xF, 0xE, 0xD, 0xC, 0xB],
        [0x3, 0x5, 0x7, 0x9, 0xB, 0xD, 0xF, 0x1, 0x0, 0x2, 0x4, 0x6, 0x8, 0xA, 0xC, 0xE]
    ]
    result = 0
    for i in range(32):
        nibble = (block >> (i * 4)) & 0xF
        sbox_choice = i % len(s_boxes)  # Use different S-boxes in round-robin fashion
        result |= s_boxes[sbox_choice][nibble] << (i * 4)
    return result


def permutation(block):
    perm = [27, 19, 3, 31, 11, 23, 15, 7, 0, 4, 8, 12, 16, 20, 24, 28,
            1, 5, 9, 13, 17, 21, 25, 29, 2, 6, 10, 14, 18, 22, 26, 30]
    result = 0
    for i in range(32):
        bit = (block >> i) & 1
        result |= bit << perm[i]
    return result


def generate_subKeys(key):
    sub_keys = []
    parts = [(key >> (i * 64)) & 0xFFFFFFFFFFFFFFFF for i in range(4)]
    for i in range(20):
        rotation_amount = (i + 1) * 3
        rotated_parts = [(p << rotation_amount | p >> (64 - rotation_amount)) & 0xFFFFFFFFFFFFFFFF for p in parts]
        combined = rotated_parts[0] ^ rotated_parts[1] ^ rotated_parts[2] ^ rotated_parts[3]
        permuted_key = permutation(combined) ^ (combined >> 32)  # Combine and permute
        sub_keys.append(permuted_key & 0xFFFFFFFFFFFFFFFF)
    return sub_keys


def round_function(right, sub_key):
    expanded = expand(right)
    x_or = expanded ^ sub_key
    substituted = sbox(x_or)
    permuted = permutation(substituted)
    rotated = (right << 13 | right >> (64 - 13)) & 0xFFFFFFFFFFFFFFFF
    return permuted ^ rotated


def feistel_encrypt(block, key):
    left = (block >> 64) & 0xFFFFFFFFFFFFFFFF
    right = block & 0xFFFFFFFFFFFFFFFF
    sub_keys = generate_subKeys(key)

    for i in range(20):
        new_right = left ^ round_function(right, sub_keys[i])
        left = right
        right = new_right

    return (right << 64) | left


def feistel_decrypt(block, key):
    left = (block >> 64) & 0xFFFFFFFFFFFFFFFF
    right = block & 0xFFFFFFFFFFFFFFFF
    sub_keys = generate_subKeys(key)

    for i in range(19, -1, -1):
        new_right = left ^ round_function(right, sub_keys[i])
        left = right
        right = new_right

    return (right << 64) | left


# Convert text to 128-bit blocks
def text_to_blocks(text):
    text_bytes = text.encode('utf-8')
    text_hex = binascii.hexlify(text_bytes).decode('utf-8')
    text_blocks = [int(text_hex[i:i+32], 16) for i in range(0, len(text_hex), 32)]
    if len(text_hex) % 32 != 0:
        text_blocks[-1] <<= (32 - len(text_hex) % 32) * 4
    return text_blocks


# Convert 128-bit blocks back to text
def blocks_to_text(blocks):
    hex_string = ''.join(f'{block:032x}' for block in blocks)
    text_bytes = binascii.unhexlify(hex_string.rstrip('0'))
    return text_bytes.decode('utf-8')


def encrypt_text(text, key):
    blocks = text_to_blocks(text)
    encrypted_blocks = [feistel_encrypt(block, key) for block in blocks]
    encrypted_hex = ''.join(f'{block:032X}' for block in encrypted_blocks)
    return encrypted_hex


def decrypt_text(encrypted_hex, key):
    block_size = 32  # 128 bits in hex (32 hex digits)
    encrypted_blocks = [int(encrypted_hex[i:i+block_size], 16) for i in range(0, len(encrypted_hex), block_size)]
    decrypted_blocks = [feistel_decrypt(block, key) for block in encrypted_blocks]
    return blocks_to_text(decrypted_blocks)


plaintext = input("Enter text to encrypt: ")
main_key = random.getrandbits(256)  # 256 bits key
encrypted_text = encrypt_text(plaintext, main_key)
decrypted_text = decrypt_text(encrypted_text, main_key)
print(f"Plain text: {plaintext}")
print(f"Key in hex: {main_key:064X}")
print(f"Encrypted/Cipher text in hex: {encrypted_text}")
print(f"Decrypted text: {decrypted_text}")