#include "kryon_native.h"
#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int hex_value(int c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static uint8_t *parse_hex(const char *hex, size_t *out_len) {
    size_t n = strlen(hex);
    while (n > 0 && (hex[n - 1] == '\n' || hex[n - 1] == '\r')) n--;
    if (n % 2 != 0) return NULL;
    uint8_t *buf = (uint8_t *)malloc(n / 2 == 0 ? 1 : n / 2);
    if (!buf) return NULL;
    for (size_t i = 0; i < n; i += 2) {
        int hi = hex_value((unsigned char)hex[i]);
        int lo = hex_value((unsigned char)hex[i + 1]);
        if (hi < 0 || lo < 0) {
            free(buf);
            return NULL;
        }
        buf[i / 2] = (uint8_t)((hi << 4) | lo);
    }
    *out_len = n / 2;
    return buf;
}

static void print_hex(const uint8_t *buf, size_t len) {
    for (size_t i = 0; i < len; ++i) printf("%02x", buf[i]);
}

int main(void) {
    char line[262144];
    uint8_t out[KRYON_MAX_DIGEST_SIZE];
    while (fgets(line, sizeof(line), stdin)) {
        char *tab = strchr(line, '\t');
        if (!tab) {
            fprintf(stderr, "bad corpus line\n");
            return 2;
        }
        *tab = '\0';
        char *name = line;
        char *hex = tab + 1;
        size_t len = 0;
        uint8_t *data = parse_hex(hex, &len);
        if (!data) {
            fprintf(stderr, "bad hex for %s\n", name);
            return 2;
        }
        kryon_status st = kryon_digest(data, len, 384u, out, sizeof(out));
        free(data);
        if (st != KRYON_OK) {
            fprintf(stderr, "digest failed for %s: %d\n", name, (int)st);
            return 1;
        }
        printf("%s\t", name);
        print_hex(out, 48u);
        printf("\n");
    }
    return 0;
}
