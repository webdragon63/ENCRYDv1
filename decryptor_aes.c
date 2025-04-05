#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

#define SALT_SIZE 16
#define IV_SIZE 16
#define KEY_SIZE 32

void handleErrors(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <encrypted_file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    const char *filename = argv[1];
    FILE *fp = fopen(filename, "rb");
    if (!fp) handleErrors("File open failed");

    unsigned char salt[SALT_SIZE], iv[IV_SIZE];
    fread(salt, 1, SALT_SIZE, fp);
    fread(iv, 1, IV_SIZE, fp);

    char password[256];
    printf("Enter password: ");
    scanf("%255s", password);

    unsigned char key[KEY_SIZE];
    if (!PKCS5_PBKDF2_HMAC(password, strlen(password), salt, SALT_SIZE, 10000, EVP_sha256(), KEY_SIZE, key))
        handleErrors("Key derivation failed");

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);

    unsigned char buffer[1024], plaintext[1024 + EVP_MAX_BLOCK_LENGTH];
    int len, plaintext_len = 0;

    while ((len = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        int out_len;
        if (!EVP_DecryptUpdate(ctx, plaintext, &out_len, buffer, len))
            handleErrors("Decrypt failed");

        fwrite(plaintext, 1, out_len, stdout);
        plaintext_len += out_len;
    }

    if (!EVP_DecryptFinal_ex(ctx, plaintext, &len))
        handleErrors("Wrong Password or Data Corrupted");

    fwrite(plaintext, 1, len, stdout);
    plaintext_len += len;

    printf("\n");

    EVP_CIPHER_CTX_free(ctx);
    fclose(fp);

    return 0;
}

