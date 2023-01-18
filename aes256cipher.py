# -*- coding: utf-8 -*-

import sys
import random
import os
import hashlib
import base64
from AES_256_CBC import AES256CBC

def utf8_to_bytes(s: str) -> bytes:
    return s.encode("utf-8")

def bytes_to_utf8(bs: bytes) -> str:
    return str(bs, "utf-8")

def calc_hash256(x: str or bytes) -> bytes:
    type_x = type(x)
    if(type_x == bytes or type_x == bytearray):
        return hashlib.sha256(x).digest()
    elif(type_x == str):
        return hashlib.sha256( utf8_to_bytes(x) ).digest()
    else:
        raise AttributeError(f"Cannot cal hash of {type(x)}: \"{x}\". ")

def calc_hash256_str(x: str or bytes) -> str:
    type_x = type(x)
    if(type_x == bytes or type_x == bytearray):
        return hashlib.sha256(x).hexdigest()
    elif(type_x == str):
        return hashlib.sha256( utf8_to_bytes(x) ).hexdigest()
    else:
        raise AttributeError(f"Cannot cal hash of {type(x)}: \"{x}\". ")

def get_random_unicode(length):
    # https://stackoverflow.com/questions/1477294/generate-random-utf-8-string-in-python
    try:
        get_char = unichr
    except NameError:
        get_char = chr

    # Update this to include code point ranges to be sampled
    include_ranges = [
        ( 0x0021, 0x0021 ),
        ( 0x0023, 0x0026 ),
        ( 0x0028, 0x007E ),
        ( 0x00A1, 0x00AC ),
        ( 0x00AE, 0x00FF ),
        ( 0x0100, 0x017F ),
        ( 0x0180, 0x024F ),
        ( 0x2C60, 0x2C7F ),
        ( 0x16A0, 0x16F0 ),
        ( 0x0370, 0x0377 ),
        ( 0x037A, 0x037E ),
        ( 0x0384, 0x038A ),
        ( 0x038C, 0x038C ),
    ]

    alphabet = [
        get_char(code_point) for current_range in include_ranges
            for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))

class AES256CBC_cipher():

    def __init__(self, key: str or bytes):
        if(len(key) == 0):
            raise ValueError(f"Key is empty: \"{key}\"")
        self.__key = calc_hash256(key)
        self.__iv = calc_hash256(b'is never the end'+self.__key+b'the end is never')[:16]
        self.__bs = 64        # 16*4. if changed, change __salt and __unsalt, __many_salt and __many_unsalt
        self.__bs_salted = 80 # 16*5. if changed, change __salt and __unsalt, __many_salt and __many_unsalt
        self.__READ_bs_count = 15
        self.__aes = AES256CBC()
    
    def encrypt_msg(self, msg: str) -> str:
        de = utf8_to_bytes(msg)

        de_pad = self.__pad(de, self.__bs)

        de_pad_salted = self.__many_salt(de_pad)

        en = self.__aes.EncryptCBC(de_pad_salted, self.__key, self.__iv)

        return base64.b64encode(en).decode("ascii")

    def decrypt_msg(self, en_msg: str) -> str:
        en = base64.b64decode(en_msg.encode("ascii"))
        
        de_pad_salted = self.__aes.DecryptCBC(en, self.__key, self.__iv)

        de_pad = self.__many_unsalt(de_pad_salted)

        de = self.__unpad(de_pad)

        return bytes_to_utf8(de)

    def _encrypt_bytes(self, x: bytes) -> bytes:
        de = x

        de_pad = self.__pad(de, self.__bs)

        de_pad_salted = self.__many_salt(de_pad)

        en = self.__aes.EncryptCBC(de_pad_salted, self.__key, self.__iv)

        return en

    def _decrypt_bytes(self, x: bytes) -> bytes:
        en = x
        
        de_pad_salted = self.__aes.DecryptCBC(en, self.__key, self.__iv)

        de_pad = self.__many_unsalt(de_pad_salted)

        de = self.__unpad(de_pad)

        return de

    def encrypt_file(self, de_src: str, en_dest: str) -> None:
        if(os.path.isfile(de_src) == False):
            raise ValueError(f"{de_src} is not file")
        de_src_abs = os.path.abspath(de_src)
        en_dest_abs = os.path.abspath(en_dest)
        i, N = 0, os.path.getsize(de_src_abs)
        if(N <= 0):
            ex = RuntimeError(f"File \"{de_src_abs}\" is empty. ")
            print(ex, file=sys.stderr)
            raise ex

        BUFF_SIZE = self.__READ_bs_count * self.__bs
        with open(de_src_abs, "rb") as fd_in, open(en_dest_abs, "wb") as fd_out:
            while(i < N):
                buff = fd_in.read(BUFF_SIZE)
                i += BUFF_SIZE
                print(f"encrypt_file {de_src}: Readed: {len(buff)} bytes")
                out = self._encrypt_bytes(buff)
                fd_out.write(out)
                print(f"encrypt_file {de_src}: Writed: {len(out)} bytes")
            fd_out.flush()

    def decrypt_file(self, en_src: str, de_dest: str) -> None:
        if(os.path.isfile(en_src) == False):
            raise ValueError(f"{en_src} is not file")
        en_src_abs = os.path.abspath(en_src)
        de_dest_abs = os.path.abspath(de_dest)
        i, N = 0, os.path.getsize(en_src_abs)
        if(N <= 0):
            ex = RuntimeError(f"File \"{en_src_abs}\" is empty. ")
            print(ex, file=sys.stderr)
            raise ex
        if(N % self.__bs_salted != 0):
            ex = RuntimeError(f"File \"{en_src_abs}\" was not encrypted by this cipher. ")

        BUFF_SIZE = self.__READ_bs_count * self.__bs_salted
        with open(en_src_abs, "rb") as fd_in, open(de_dest_abs, "wb") as fd_out:
            while(i < N):
                buff = fd_in.read(BUFF_SIZE)
                i += BUFF_SIZE
                print(f"decrypt_file {en_src}: Readed: {len(buff)} bytes")
                out = self._decrypt_bytes(buff)
                fd_out.write(out)
                print(f"decrypt_file {en_src}: Writed: {len(out)} bytes")
            fd_out.flush()

    def bytes_to_str(self, bs: bytes) -> bytes:
        return self.__aes.printHexArray_str(bs)

    def __many_salt(self, x: bytes) -> bytes:
        bs = self.__bs
        bs_salted = self.__bs_salted
        len_x = len(x)
        if(len_x == 0 or len_x % bs != 0):
            ex = ValueError(f"__many_salt: lenght of x must devided {bs}, but len = {len_x}")
            print(ex, file=sys.stderr)
            raise ex
        count = len_x // bs
        x_salted = bytearray(bs_salted*count)
        for i in range(count):
            salt_block = self.__salt(x[i*bs:(i+1)*bs])
            for j in range(bs_salted):
                x_salted[i*bs_salted + j] = salt_block[j]
        return bytes(x_salted)

    def __salt(self, x: bytes) -> bytes:
        # every fifth byte insert random stuff
        bs = self.__bs
        if(bs != len(x)):
            ex = ValueError(f"__salt: lenght of x must be {bs}, but len = {len(x)}")
            print(ex, file=sys.stderr)
            raise ex
        bs_salted = self.__bs_salted
        x_salted = bytearray(bs_salted)
        salt = random.randbytes(16)
        #salt = calc_hash256(os.urandom(32))[:16]
        j, s = 0, 0
        for i in range(bs_salted):
            if(i % 5 == 0):
                x_salted[i] = salt[s]
                s-=-1
            else:
                x_salted[i] = x[j]
                j+=1
        return bytes(x_salted)

    def __many_unsalt(self, x: bytes) -> bytes:
        bs_salted = self.__bs_salted
        bs = self.__bs
        len_x = len(x)
        if(len_x == 0 or len_x % bs_salted != 0):
            ex = ValueError(f"__many_salt: lenght of x must devided {bs_salted}, but len = {len_x}")
            print(ex, file=sys.stderr)
            raise ex
        count = len_x // bs_salted
        x_unsalted = bytearray(bs*count)
        for i in range(count):
            unsalt_block = self.__unsalt(x[i*bs_salted:(i+1)*bs_salted])
            for j in range(bs):
                x_unsalted[i*bs + j] = unsalt_block[j]
        return bytes(x_unsalted)

    def __unsalt(self, x: bytes) -> bytes:
        # every fifth byte remove
        bs_salted = self.__bs_salted
        if(bs_salted != len(x)):
            ex = ValueError(f"__unsalt: lenght of x must be {bs_salted}, but len = {len(x)}")
            print(ex, file=sys.stderr)
            raise ex
        bs = self.__bs
        x_unsalted = bytearray(bs)
        i = 0
        for j in range(bs_salted):
            if(j % 5 != 0):
                x_unsalted[i] = x[j]
                i+=1
        return bytes(x_unsalted)

        bs = self.__bs
        bs_salted = 80 # 16*5
        x_salted = bytearray(bs_salted)
        salt = random.randbytes(16)
        j, s = 0, 0
        for i in range(bs_salted):
            if(i % 5 == 0):
                x_salted[i] = salt[s]
                s-=-1
            else:
                x_salted[i] = x[j]
                j+=1
        return bytes(x_salted)

    @staticmethod
    def __pad(x: bytes, bs: int) -> bytes:
        count = (bs - len(x) % bs) % bs
        shi = count.to_bytes(1, "big")
        return x + shi*count
    
    @staticmethod
    def __unpad(x: bytes) -> bytes:
        len_bs = len(x)
        last = x[len_bs-1] # last is int?
        #count = int.from_bytes(last, "big")
        count = last
        return x[:-count]
    
    def _tests(self):
        cipher = AES256CBC_cipher("key")
        #for i in range(1000):
        for i in range(0):
            bs = random.randbytes(random.randint(1, 700000))
            #bs = random.randbytes(random.randint(1, 100))
            #bs = b'\x00'*random.randint(0, 17)
            #bs = b'\x01'*random.randint(0, 17)
            #bs = b'\xff'*random.randint(0, 17)
            bs_pad = cipher.__pad(bs, cipher.__bs)
            if(len(bs_pad) % cipher.__bs != 0):
                print(f"({i+1}) error __pad: ")
                print(f"Before: {cipher.bytes_to_str(bs)}\nAfter: {cipher.bytes_to_str(bs_pad)}")
                exit()

            bs_pad_salt = b''
            for i in range(0, len(bs_pad), cipher.__bs):
                bs_pad_salt += cipher.__salt(bs_pad[i:i+cipher.__bs])
            if(len(bs_pad_salt) % cipher.__bs_salted != 0):
                print(f"({i+1}) error __salt: ")
                print(f"src: {cipher.bytes_to_str(bs_pad)}\nsalted: {cipher.bytes_to_str(bs_pad_salt)}")
                exit()

            bs_pad_unsalt = b''
            for i in range(0, len(bs_pad_salt), cipher.__bs_salted):
                bs_pad_unsalt += cipher.__unsalt(bs_pad_salt[i:i+cipher.__bs_salted])
            if(len(bs_pad_unsalt) % cipher.__bs != 0):
                print(f"({i+1}) error __unsalt len: ")
                print(f"src: {cipher.bytes_to_str(bs_pad)}\nunsalted: {cipher.bytes_to_str(bs_pad_unsalt)}")
                exit()
            if(bs_pad_unsalt != bs_pad):
                print(f"({i+1}) error __unsalt dif: ")
                print(f"bs_pad: {cipher.bytes_to_str(bs_pad)}\nsalted: {cipher.bytes_to_str(bs_pad_salt)}\nunsalted: {cipher.bytes_to_str(bs_pad_unsalt)}")
                exit()
            
            bs_pad_salt2 = cipher.__many_salt(bs_pad)
            bs_pad_unsalt2 = cipher.__many_unsalt(bs_pad_salt)
            if(len(bs_pad_salt2) % cipher.__bs_salted != 0 or len(bs_pad_unsalt) % cipher.__bs != 0):
                print(f"({i+1}) error __many_salt/unsalt len: ")
                print(f"bs_pad: {cipher.bytes_to_str(bs_pad)}\nsalted: {cipher.bytes_to_str(bs_pad_salt2)}\nunsalted: {cipher.bytes_to_str(bs_pad_unsalt2)}")
                exit()

            if(bs_pad != bs_pad_unsalt2):
                print(f"({i+1}) error __many_salt/unsalt dif: ")
                print(f"bs_pad: {cipher.bytes_to_str(bs_pad)}\nsalted: {cipher.bytes_to_str(bs_pad_salt2)}\nunsalted: {cipher.bytes_to_str(bs_pad_unsalt2)}")
                exit()

            bs_unpad = cipher.__unpad(bs_pad_unsalt)
            if(bs != bs_unpad):
                print(f"({i+1}) error __unpad: ")
                print(f"src: {cipher.bytes_to_str(bs)}\nunpad: {cipher.bytes_to_str(bs_unpad)}")
                exit()

        for i in range(0):
            key = get_random_unicode(random.randint(1, 300))
            aes = AES256CBC_cipher(key)
            for i in range(100):
                src = get_random_unicode(random.randint(1, 15000))
                en1 = aes.encrypt_msg(src)
                en2 = aes.encrypt_msg(src)
                de1 = aes.decrypt_msg(en1)
                de2 = aes.decrypt_msg(en2)

                aes2 = AES256CBC_cipher(key)
                en3 = aes.encrypt_msg(src)
                de3 = aes.decrypt_msg(en3)
                if(src != de1 or src != de2 or src != de3):
                    print(f"({i+1}) error encrypt/decrypt: ")
                    exit()

        for i in range(10):
            key = get_random_unicode(random.randint(1, 300))
            aes = AES256CBC_cipher(key)
            src_path = "src_file"
            en_path1, de_path1 = "en_file1", "de_file1"
            en_path2, de_path2 = "en_file2", "de_file2"
            en_path3, de_path3 = "en_file3", "de_file3"
            for i in range(100):
                with open(src_path, "wb") as fd:
                    #fd.write(random.randbytes(random.randint(1, 4096*5)))
                    fd.write(random.randbytes(random.randint(1, 1000)))
                print(i)
                aes.encrypt_file(src_path, en_path1)
                aes.decrypt_file(en_path1, de_path1)
                aes.encrypt_file(src_path, en_path2)
                aes.decrypt_file(en_path2, de_path2)

                aes2 = AES256CBC_cipher(key)
                en3 = aes.encrypt_file(src_path, en_path3)
                de3 = aes.decrypt_file(en_path3, de_path3)
                with open(src_path, "rb") as fd0, open(de_path1, "rb") as fd1, open(de_path2, "rb") as fd2, open(de_path3, "rb") as fd3: 
                    src, de1, de2, de3 = fd0.read(), fd1.read(), fd2.read(), fd3.read()
                    if(src != de1 or src != de2 or src != de3):
                        print(f"({i+1}) error file encrypt/decrypt: ")
                        print(f"size: src={len(src)}, de1={len(de1)}, de2={len(de2)}, de3={len(de3)}")
                        print(f"src={cipher.bytes_to_str(src)}\nde1={cipher.bytes_to_str(de1)}\nde2={cipher.bytes_to_str(de2)}\nde3={cipher.bytes_to_str(de3)}")
                        exit()
                
                os.unlink(src_path), os.unlink(en_path1), os.unlink(de_path1), os.unlink(en_path2), os.unlink(de_path2), os.unlink(en_path3), os.unlink(de_path3)

            
        print("All is ok")

if __name__ == '__main__':
    cipher = AES256CBC_cipher("key")
    cipher._tests()
