all:
	@mkdir -p output
	@bash -c '\
		if gcc encryptor_aes.c -o output/encryptor -lcrypto >/dev/null 2>&1 && \
		   gcc decryptor_aes.c -o output/decryptor -lcrypto >/dev/null 2>&1; then \
			echo "Build Success"; \
		else \
			echo "Build Failed"; \
		fi'
