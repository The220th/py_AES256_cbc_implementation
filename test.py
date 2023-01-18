# -*- coding: utf-8 -*-

import subprocess
import random

from AES_256_CBC import AES256CBC
from aes256cipher import AES256CBC_cipher

CPP_EXE_NAME = "./cpp/cpp_aes"

# def exe_cpp(en: bytes, key: bytes, iv: bytes, EN_DE: bool) -> str:
#     process = subprocess.Popen(CPP_EXE_NAME, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

#     enLen = len(en)
#     if(EN_DE == False):
#         process.stdin.write(f"en {enLen}\n".encode("ascii"))
#     else:
#         process.stdin.write(f"de {enLen}\n".encode("ascii"))
#     process.stdin.write(en)
#     process.stdin.write(key)
#     process.stdin.write(iv)
#     process.stdin.flush()
#     out = process.stdout.read().decode("ascii")
#     return out

def exe_cpp(en_de: bytes, key: bytes, iv: bytes, EN_DE: bool) -> str:
    endeLen = len(en_de)
    if(EN_DE == False):
        proc_in = f"en {endeLen}\n".encode("ascii") + en_de + key + iv
    else:
        proc_in = f"de {endeLen}\n".encode("ascii") + en_de + key + iv
    proc = subprocess.run([f"{CPP_EXE_NAME}"], capture_output=True, input=proc_in)
    
    return proc.stdout.decode("ascii")

def gen_en_de() -> bytes:
    count = random.randint(1, 100)
    return random.randbytes(count*16)

def gen_key() -> bytes:
    return random.randbytes(32)

def gen_iv() -> bytes:
    return random.randbytes(16)

if __name__ == "__main__":

    en_de, key, iv = gen_en_de(), gen_key(), gen_iv()
    for i in range(10):
        aes = AES256CBC()
        for j in range(10):
            EN_DE = random.choice([False, True])
            if(random.choice([False, True])):
                en_de = gen_en_de()
            if(random.choice([False, True])):
                key = gen_key()
            if(random.choice([False, True])):
                iv = gen_iv()
            # en, key, iv = gen_en(), gen_key(), gen_iv()

            if(EN_DE == False):
                cpp_says = exe_cpp(en_de, key, iv, EN_DE)
                py_says_bytes  = aes.EncryptCBC(en_de, key, iv)
                py_says = aes.printHexArray_str(py_says_bytes)
            else:
                cpp_says = exe_cpp(en_de, key, iv, EN_DE)
                py_says_bytes  = aes.DecryptCBC(en_de, key, iv)
                py_says = aes.printHexArray_str(py_says_bytes)
            if(cpp_says != py_says):
                print(f"error")
                print(f"EN_DE={EN_DE}, en_de={en_de}, key={key}, iv={iv}")
                exit()
    for i in range(10):
        aes = AES256CBC()
        for j in range(10):
            if(random.choice([False, True])):
                en_de = gen_en_de()
            if(random.choice([False, True])):
                key = gen_key()
            if(random.choice([False, True])):
                iv = gen_iv()
            # en, key, iv = gen_en(), gen_key(), gen_iv()
            rem = aes.printHexArray_str(en_de)

            cpp_says = exe_cpp(en_de, key, iv, False)
            encrypted  = aes.EncryptCBC(en_de, key, iv)
            py_says = aes.printHexArray_str(encrypted)
            if(cpp_says != py_says):
                print(f"error before")
                print(f"en_de={en_de}, key={key}, iv={iv}")
                exit()
            
            cpp_says = exe_cpp(encrypted, key, iv, True)
            decrypted  = aes.DecryptCBC(encrypted, key, iv)
            py_says = aes.printHexArray_str(decrypted)
            if(cpp_says != py_says):
                print(f"error different")
                print(f"en_de={en_de}, key={key}, iv={iv}")
                exit()
            if(py_says != rem):
                print(f"error after")
                print(f"src={en_de}, en={encrypted}, de={decrypted}\n")
                print(f"en_de={en_de}, key={key}, iv={iv}")
                exit()

    cipher = AES256CBC_cipher("key")
    cipher._tests()

    print("All is ok")
