from Crypto.Cipher import AES

key = b"StavenZobairi___" # byte string is a string that stores raw bytes instead of text characters, each character inside is stored as a single byte using its ASCII code. It looks like text, but under the hood, Python stores it as ASCII codes: 16 bytes total, perfect for AES-128!

r1 = bytes.fromhex("32 20 50 69 6C 6C 65 6E 20 41 73 70 69 72 69 6E")
r2= bytes.fromhex("33 20 50 69 6C 6C 65 6E 20 41 73 70 69 72 69 6E")
r3= bytes.fromhex("34 20 50 69 6C 6C 65 6E 20 41 73 70 69 72 69 6E")
r4= bytes.fromhex("35 20 50 69 6C 6C 65 6E 20 41 73 70 69 72 69 6E")


cipher = AES.new(key, AES.MODE_ECB)   # Chiffre / Verschlüsselungsverfahren - to encrypt r1, I’ll first need to create the cipher

# Chiffretext / Ergebnis der Verschlüsselung - then encrypt
c1 = cipher.encrypt(r1)               
c2 = cipher.encrypt(r2)
c3 = cipher.encrypt(r3)
c4 = cipher.encrypt(r4)
print(c1, c2)
hex_cipher_list = [c1.hex(), c2.hex(), c3.hex(), c4.hex()]

for i in range(0, len(hex_cipher_list)):
    print(f"Ciphertext{i+1}: {hex_cipher_list[i]}")


# Hamming Distance or the number of bits that differ between two byte sequences

def hamming(c1: bytes, c2: bytes) -> int:
    total = 0
    for byte_from_c1, byte_from_c2 in zip(c1, c2):
        diff = byte_from_c1 ^ byte_from_c2
        total += bin(diff).count("1")
    return total

print(f"Hamming distance c1 vs c2: {hamming(c1, c2)}")
print(f"Hamming distance c1 vs c3: {hamming(c1, c3)}")
print(f"Hamming distance c1 vs c4: {hamming(c1, c4)}")

'''
b'Q\n!\xe9\x9c\x94(\xe0$\xb5_\xc1\x84\x1b\x112' b'\x83%\xf4\xcc}d\x03\xff\xa8\x9a>\x9b)Wh0'
Ciphertext1: 510a21e99c9428e024b55fc1841b1132
Ciphertext2: 8325f4cc7d6403ffa89a3e9b29576830
Ciphertext3: 6e231c3cfceb516b6d55992b46d67245
Ciphertext4: b97b4d598cebd0f932d556045db69d5f
Hamming distance c1 vs c2: 63
Hamming distance c1 vs c3: 70
Hamming distance c1 vs c4: 60
'''