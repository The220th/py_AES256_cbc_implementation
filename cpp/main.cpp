#include <iostream>
#include <string>
#include <cstdio>

#include "AES256CBC.h"

using namespace std;

int main()
{
	unsigned en_len;
	// unsigned char mode[2];
	string mode;
	cin >> mode;
	cin >> en_len;
	// cout << mode << endl;
	// cout << en_len << endl;
	getchar(); // 0x0a - space
	unsigned char *en_de = new unsigned char[en_len];
	unsigned char *out   = new unsigned char[en_len];
	unsigned char key[32];
	unsigned char iv[16];
	for(int i = 0; i < en_len; ++i) en_de[i] = getchar();
	for(int i = 0; i < 32; ++i) key[i] = getchar();
	for(int i = 0; i < 16; ++i) iv[i] = getchar();

	AES256CBC aes = AES256CBC();
	// aes.printHexArray(en, en_len); cout << endl;
	// aes.printHexArray(key, 32); cout << endl;
	// aes.printHexArray(iv, 16); cout << endl;
	if(mode == "en")
	{
		unsigned char* buff = aes.EncryptCBC(en_de, out, en_len, key, iv);
		aes.printHexArray(buff, en_len);
	}
	else
	{
		cout << "Error" << endl;
	}


	delete en_de;
	delete out;

	return 0;
	// AES256CBC aes = AES256CBC();
	// int enLen = 16;
	// unsigned char en[16] = {0x1, 0x2, 0x3, 0x4, 0x1, 0x2, 0x3, 0x4, 0x1, 0x2, 0x3, 0x4, 0x1, 0x2, 0x3, 0x4};
	// unsigned char iv[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
	// unsigned char key[32] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
	// unsigned char out[16] = {0};
	// unsigned char* buff = aes.EncryptCBC(en, out, enLen, key, iv);
	// aes.printHexArray(buff, 16);
	// return 0;
}