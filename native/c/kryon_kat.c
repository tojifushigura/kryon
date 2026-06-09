#include "kryon_native.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void print_hex(const uint8_t *buf, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        printf("%02x", buf[i]);
    }
}

int main(void) {
    const char *messages[] = {"", "abc", "The quick brown fox jumps over the lazy dog"};
    uint8_t out[KRYON_MAX_DIGEST_SIZE];
    for (size_t i = 0; i < sizeof(messages) / sizeof(messages[0]); ++i) {
        const char *msg = messages[i];
        kryon_status st = kryon_digest((const uint8_t *)msg, strlen(msg), 384u, out, sizeof(out));
        if (st != KRYON_OK) {
            fprintf(stderr, "digest failed for message %zu: %d\n", i, (int)st);
            return 1;
        }
        printf("%s\t", msg);
        print_hex(out, 48u);
        printf("\n");
    }
    return 0;
}
