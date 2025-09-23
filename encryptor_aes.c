#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>

#define SALT_SIZE 16
#define IV_SIZE 16
#define KEY_SIZE 32
#define BUFFER_SIZE 4096

void handleErrors() {
    ERR_print_errors_fp(stderr);
    abort();
}

void derive_key(const char *password, unsigned char *salt, unsigned char *key) {
    if (!PKCS5_PBKDF2_HMAC(password, strlen(password), salt, SALT_SIZE, 10000, EVP_sha256(), KEY_SIZE, key))
        handleErrors();
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <input.txt> <output.bin>\n", argv[0]);
        return 1;
    }

    char password[256];
    printf("Enter password: ");
    scanf("%255s", password);

    FILE *fin = fopen(argv[1], "rb");
    FILE *fout = fopen(argv[2], "wb");
    if (!fin || !fout) {
        perror("File error");
        return 1;
    }

    unsigned char salt[SALT_SIZE], iv[IV_SIZE], key[KEY_SIZE];
    RAND_bytes(salt, sizeof(salt));
    RAND_bytes(iv, sizeof(iv));

    derive_key(password, salt, key);

    fwrite(salt, 1, SALT_SIZE, fout);
    fwrite(iv, 1, IV_SIZE, fout);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);

    unsigned char inbuf[BUFFER_SIZE], outbuf[BUFFER_SIZE + EVP_MAX_BLOCK_LENGTH];
    int inlen, outlen;

    while ((inlen = fread(inbuf, 1, BUFFER_SIZE, fin)) > 0) {
        if (!EVP_EncryptUpdate(ctx, outbuf, &outlen, inbuf, inlen))
            handleErrors();
        fwrite(outbuf, 1, outlen, fout);
    }

    if (!EVP_EncryptFinal_ex(ctx, outbuf, &outlen))
        handleErrors();
    fwrite(outbuf, 1, outlen, fout);

    EVP_CIPHER_CTX_free(ctx);
    fclose(fin);
    fclose(fout);

    printf("Encryption completed!\n");
    return 0;
}
