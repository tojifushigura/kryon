.PHONY: c-kat c-corpus clean

CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -pedantic

c-kat: kryon_kat
	./kryon_kat

c-corpus: kryon_corpus
	./kryon_corpus

kryon_kat: kryon_native.c kryon_native.h kryon_kat.c
	$(CC) $(CFLAGS) kryon_native.c kryon_kat.c -o kryon_kat

kryon_corpus: kryon_native.c kryon_native.h kryon_corpus.c
	$(CC) $(CFLAGS) kryon_native.c kryon_corpus.c -o kryon_corpus

clean:
	rm -f kryon_kat kryon_corpus
