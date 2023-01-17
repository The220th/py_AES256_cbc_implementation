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
