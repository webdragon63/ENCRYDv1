all:
	gcc encryptor_aes.c -o output/encryptor -lcrypto
	gcc decryptor_aes.c -o output/decryptor -lcrypto
