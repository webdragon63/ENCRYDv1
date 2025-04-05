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

int main() {
    unsigned char salt[SALT_SIZE];
    unsigned char iv[IV_SIZE];
    unsigned char key[KEY_SIZE];

    if (!RAND_bytes(salt, sizeof(salt)) || !RAND_bytes(iv, sizeof(iv)))
        handleErrors("Random generation failed");

    char password[256];
    char plaintext[1024];

    printf("Enter message to encrypt: ");
    fgets(plaintext, sizeof(plaintext), stdin);
    plaintext[strcspn(plaintext, "\n")] = 0;

    printf("Enter password: ");
    scanf("%255s", password);

    if (!PKCS5_PBKDF2_HMAC(password, strlen(password), salt, SALT_SIZE, 10000, EVP_sha256(), KEY_SIZE, key))
        handleErrors("Key derivation failed");

    FILE *fp = fopen("encrypted.bin", "wb");
    if (!fp) handleErrors("File open failed");

    fwrite(salt, 1, SALT_SIZE, fp);
    fwrite(iv, 1, IV_SIZE, fp);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);

    unsigned char ciphertext[1024 + EVP_MAX_BLOCK_LENGTH];
    int len, ciphertext_len = 0;

    if (!EVP_EncryptUpdate(ctx, ciphertext, &len, (unsigned char *)plaintext, strlen(plaintext)))
        handleErrors("Encryption failed");

    fwrite(ciphertext, 1, len, fp);
    ciphertext_len += len;

    if (!EVP_EncryptFinal_ex(ctx, ciphertext, &len))
        handleErrors("Final encryption failed");

    fwrite(ciphertext, 1, len, fp);
    ciphertext_len += len;

    EVP_CIPHER_CTX_free(ctx);
    fclose(fp);

    printf("Message Encrypted and saved to encrypted.bin\n");

    return 0;
}

