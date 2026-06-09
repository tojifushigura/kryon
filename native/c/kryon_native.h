#ifndef KRYON_NATIVE_H
#define KRYON_NATIVE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define KRYON_BLOCK_SIZE 32u
#define KRYON_MAX_DIGEST_SIZE 64u
#define KRYON_NATIVE_VERSION "kryon-native-c-1.0.0"

typedef enum kryon_status {
    KRYON_OK = 0,
    KRYON_ERR_INVALID_ARGUMENT = 1
} kryon_status;

typedef struct kryon_ctx {
    uint64_t binary[12];
    uint16_t residue[24];
    uint8_t tail[KRYON_BLOCK_SIZE];
    size_t tail_len;
    uint64_t total_len;
    uint32_t out_bits;
    uint64_t block_index;
} kryon_ctx;

kryon_status kryon_init(kryon_ctx *ctx, uint32_t out_bits);
kryon_status kryon_update(kryon_ctx *ctx, const uint8_t *data, size_t len);
kryon_status kryon_final(const kryon_ctx *ctx, uint8_t *out, size_t out_len);
kryon_status kryon_digest(const uint8_t *data, size_t len, uint32_t out_bits, uint8_t *out, size_t out_len);
const char *kryon_native_version(void);

#ifdef __cplusplus
}
#endif

#endif
