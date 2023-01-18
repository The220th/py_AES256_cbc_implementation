# py_AES256_cbc_implementation

python AES256-CBC implementation.

Based on [https://github.com/SergeyBel/AES](https://github.com/SergeyBel/AES).

# Usage

``` python
from AES_256_CBC import AES256CBC

key  = b'Super secret keySuper secret key' # 32 bytes (256 bits)
iv   = b'randoom init str' # 16 bytes
text = b'the end is never' # must be: len(text) % 16 == 0
aes = AES256CBC()

# Encrypt:
encrypted_bytes = aes.EncryptCBC(text, key, iv) # b'\xcd;7\x7f\x03\xef:b\x9f`5\xf59C\xb2\xbb'

# Decrypt:
decrypted_bytes = aes.DecryptCBC(encrypted_bytes, key, iv) # b'the end is never'

print(text == decrypted_bytes)
```

# kaes256CBC wrapper usage

``` python
from kaes256cipher import kaes256CBC

aes = kaes256CBC("Your key")

# text encrypt/decrypt:
encrypted_message1 = aes.encrypt_msg("Your message. Любой длины. UTF-8 support. 😽")
print(encrypted_message1) # KNFTw7KMxksJul7Ojjc...fTCnMK0O6uvS6r3+T94P
encrypted_message2 = aes.encrypt_msg("Your message. Любой длины. UTF-8 support. 😽")
print(encrypted_message2) # TpB2ctJ9LjoMYGPk50P...casywlZBQwW5sOu6Td1z

# Salt injected in original message
print(encrypted_message1 == encrypted_message2) # False

import random
encrypted_message = random.choice([encrypted_message1, encrypted_message2])

decrypted_msg = aes.decrypt_msg(encrypted_message) # Your message. Любой длины. UTF-8 support. 😽
print(decrypted_msg)



# files encrypt/decrypt:
aes.encrypt_file("/path/to/src/unencrypted/file", "/path/to/encrypted/file") # Very slow. Use gpg better

aes.decrypt_file("/path/to/encrypted/file", "/path/to/decrypted/file") # Very slow. Use gpg better

content1 = open("/path/to/src/unencrypted/file", "rb").read()
content2 = open("/path/to/decrypted/file", "rb").read()

print(content1 == content2) # True
```