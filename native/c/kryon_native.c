#include "kryon_native.h"

#include <limits.h>
#include <stdio.h>
#include <string.h>

#define VERSION_TAG UINT64_C(0x4352574556323032)

static const uint64_t K1[12] = {
    UINT64_C(0xb762e9fdd7731f3b), UINT64_C(0xfc54b43362125049), UINT64_C(0x99bb41ce1f9f6bc2), UINT64_C(0x78f8118406b1b765),
    UINT64_C(0x260c848607528802), UINT64_C(0x7be8e7f71c49c052), UINT64_C(0xafb75e07e0840f0d), UINT64_C(0x0f597582042fa91b),
    UINT64_C(0x14536abe7afba732), UINT64_C(0xe6d36de84ff057e2), UINT64_C(0x520531b51228653d), UINT64_C(0x3c7d758ec628c034)
};

static const uint64_t K2[12] = {
    UINT64_C(0xd1d1cc5a1e22a635), UINT64_C(0xe33b725a0f9df976), UINT64_C(0x0e0667fea990a1ef), UINT64_C(0xeac86c8c69964150),
    UINT64_C(0xb29d7cef3bee15cc), UINT64_C(0x8c5385bd40adc713), UINT64_C(0xcee03400f71b2029), UINT64_C(0xacddd9673e87cf53),
    UINT64_C(0xfad087297cacd9be), UINT64_C(0x3f52953ba7e43eda), UINT64_C(0xaf3e9fcef32fcdf1), UINT64_C(0x8732b441ead04b9a)
};

static const uint64_t RC64[18][12] = {
    {UINT64_C(0xcf835f9ca21757ad), UINT64_C(0x2e43a162712f13d0), UINT64_C(0x5ce4fc5d52aa4fe0), UINT64_C(0xeccd04aec817e999), UINT64_C(0x20923aad14936640), UINT64_C(0x0d9c9e6dd7345af0), UINT64_C(0x80039fe957b219ce), UINT64_C(0x5cb55b1284bfc7ba), UINT64_C(0xde794f6fabaec79d), UINT64_C(0xae160eecb2206ae9), UINT64_C(0x83204f6b73d372a7), UINT64_C(0x7a96e0fece44f182)},
    {UINT64_C(0x38779d0b93e1996e), UINT64_C(0x7667187a36d44275), UINT64_C(0xa70a7e379eaf848f), UINT64_C(0xd05d1f0979585322), UINT64_C(0x3b2dddd4435f12d3), UINT64_C(0xf1fd4786fa9c726b), UINT64_C(0xf7e8530cfa849a5b), UINT64_C(0x8e820d98aca5a47a), UINT64_C(0xb77dd8e6b9796054), UINT64_C(0x48064cd0dc5ba430), UINT64_C(0x2c5b2fd2bd723c83), UINT64_C(0xc941741d365a3493)},
    {UINT64_C(0xd1e58ee5881afdf9), UINT64_C(0xe4aca897c78bd5a9), UINT64_C(0x46481ef2102b92c9), UINT64_C(0xf920cf5d4afc942a), UINT64_C(0xb9e80f1f063ffba9), UINT64_C(0xed050c88d2d4ac09), UINT64_C(0xbe3f1f93e2672e9e), UINT64_C(0x58807584480af818), UINT64_C(0x24c2757ba89be3d7), UINT64_C(0x0ad0362e18077b3c), UINT64_C(0x74a5f07248cf0343), UINT64_C(0xf5a13a7ff17f03f2)},
    {UINT64_C(0x0833759e383ab521), UINT64_C(0xc4146a31a2439cc4), UINT64_C(0x46aab5cad80c1672), UINT64_C(0x1229c3ac037d9cdf), UINT64_C(0xca56686ef5577f4a), UINT64_C(0xc170ead2e066aadd), UINT64_C(0x2027480033a7293a), UINT64_C(0xc95d8ff891429bc4), UINT64_C(0x67d7f3565627eba4), UINT64_C(0x23320088d2c03aa4), UINT64_C(0x578932b1da16f10c), UINT64_C(0xdb3940d94b357ee7)},
    {UINT64_C(0x1eb3de0dbbbdebb5), UINT64_C(0x3fb7c60bab9d7f91), UINT64_C(0x8780b1c9e9cdee15), UINT64_C(0xbc204d95b9ac2573), UINT64_C(0x49d1094064f12848), UINT64_C(0x0ecfd4d30b1f4e51), UINT64_C(0xeda4d5ebcb006250), UINT64_C(0x77261ba17addbbaf), UINT64_C(0xa9635fc6e9753fcf), UINT64_C(0xdb4afbe059919603), UINT64_C(0x53adc828316bc118), UINT64_C(0xd47c8b6ad8eb62b4)},
    {UINT64_C(0x1aae66fcdec903ed), UINT64_C(0xa3b95549e1af3a64), UINT64_C(0xabb81c94570876c5), UINT64_C(0x6d4725ecd79be3db), UINT64_C(0x0ac7fd2da167f881), UINT64_C(0x9855a9f96d2f9eff), UINT64_C(0xa982f52a51acac0d), UINT64_C(0x66163f5b99cc6c05), UINT64_C(0x65ca5f344c376c74), UINT64_C(0x1844ce4b3bb8f19f), UINT64_C(0xa05cee49f7f07365), UINT64_C(0x14d38aba71d769b7)},
    {UINT64_C(0x51118f4e0e77d235), UINT64_C(0xc9f739eb307602d8), UINT64_C(0xdf88d9400223c713), UINT64_C(0x69fde9a3572e4410), UINT64_C(0x87a62cfe6af5a880), UINT64_C(0x02672f4d16226c08), UINT64_C(0x8f13bb2670ecf882), UINT64_C(0x4a12fff8149fbfde), UINT64_C(0xc0980af3074ded0b), UINT64_C(0x99962198b76be99e), UINT64_C(0xb5f0cd6049da4bc3), UINT64_C(0x6436e835b2305e0e)},
    {UINT64_C(0x53659989ba2cea9d), UINT64_C(0x109e4039f22f1785), UINT64_C(0xf0948b87f2d036ef), UINT64_C(0x76fc517dec7aea3e), UINT64_C(0xcf68fc0e6429b5cb), UINT64_C(0x7f811c4300c993d1), UINT64_C(0xd91aea71539f4e9d), UINT64_C(0x62ef157bd50242b3), UINT64_C(0x9d61c6def718eb9b), UINT64_C(0xe707aa54236d676f), UINT64_C(0x9c6e75d5cf4eb464), UINT64_C(0x352a1278b3c97994)},
    {UINT64_C(0xd2be4327bf86f83f), UINT64_C(0xa50541e0f1e5f327), UINT64_C(0xe4976270660b75c1), UINT64_C(0xba3772d38f69cca8), UINT64_C(0x719e2e6a58b7eb24), UINT64_C(0x63c5d71ed2f775c2), UINT64_C(0x487d0694d7a62a8b), UINT64_C(0x1147f9a644881e2e), UINT64_C(0x2f97225d906249f9), UINT64_C(0xe5accfd8bde21bfd), UINT64_C(0x80c41354572005fa), UINT64_C(0xefa90fc99406ef73)},
    {UINT64_C(0x9b795fdcb78fc095), UINT64_C(0x951cb24ba0e5a9f2), UINT64_C(0xd75505700926b853), UINT64_C(0x0dc71628029f1740), UINT64_C(0x4bb69a95d2f076eb), UINT64_C(0x28f33f44091b622d), UINT64_C(0x583d15d6398d6a3c), UINT64_C(0x1da7ac61de2fe616), UINT64_C(0x50561ea1de23a6a0), UINT64_C(0x604b52996dadf9f4), UINT64_C(0x4a810be4fb99e614), UINT64_C(0x2aaf500b0628002f)},
    {UINT64_C(0x456a1cf5801532b0), UINT64_C(0x0e918f0623329f1f), UINT64_C(0xf51f9d36d5f953ff), UINT64_C(0xdd93408831cc4f3c), UINT64_C(0x7f39e3494d232c15), UINT64_C(0xf9ebfd359f4eb92a), UINT64_C(0x4b4d632c65400ffd), UINT64_C(0x9187b9dc2deb2f88), UINT64_C(0x40405fc82a849b07), UINT64_C(0x1fe9f4a2a8bb7ab6), UINT64_C(0x573c4a0e11315ed2), UINT64_C(0x1f708dfa9b4bbef6)},
    {UINT64_C(0x5d1ed5401b59248d), UINT64_C(0xd1387ecdf0efc15d), UINT64_C(0xec0a89c1779bedd8), UINT64_C(0x28d6c002a269721b), UINT64_C(0xbb796bf7e432b7b1), UINT64_C(0xcfb3694a19176508), UINT64_C(0xc39d872df5ddfff9), UINT64_C(0x043a2a0515d47ab3), UINT64_C(0x0269ded3686cf365), UINT64_C(0x6467c623c9c5037c), UINT64_C(0x305a42e98928c12e), UINT64_C(0xcedb184b97ab8875)},
    {UINT64_C(0x2c00b8a5c14ba580), UINT64_C(0x84cae4258110cf1f), UINT64_C(0x480d10f83013d133), UINT64_C(0xcef7d78f9f16efcc), UINT64_C(0x6dec6b6c89e6480f), UINT64_C(0x4d3aceb72e2f38e3), UINT64_C(0xf93401240d7befc0), UINT64_C(0x45fde0135a0311c8), UINT64_C(0xf2345a48ac69a57e), UINT64_C(0x02065ef50a978cd4), UINT64_C(0xee2f678931e04155), UINT64_C(0x9ab7a2b4e22544f1)},
    {UINT64_C(0x9c0e2b08b25a71bd), UINT64_C(0x45e89fdecf64f99f), UINT64_C(0x08de71d7242f01a7), UINT64_C(0x8a0ffa261091a8f6), UINT64_C(0x740ae69d54557277), UINT64_C(0x99f2df91e47009a5), UINT64_C(0xefba37d5ab19d262), UINT64_C(0x31ec0c6f0c3e5747), UINT64_C(0x1aed868a5e840fc1), UINT64_C(0x56950fa0799abcc8), UINT64_C(0x69afef92c795cdd1), UINT64_C(0xe1ebe2321f85599e)},
    {UINT64_C(0xdecbb96ae5a370cc), UINT64_C(0x7bc325b746a44ed6), UINT64_C(0x5f98e40bc421d4d1), UINT64_C(0x95214e4c9393c21f), UINT64_C(0xe440693fd38455eb), UINT64_C(0x6e9931a126290e28), UINT64_C(0xbb9525d88a075f7b), UINT64_C(0xf09c7124cb421ca8), UINT64_C(0x7a615db6b0ffa889), UINT64_C(0x1ec6da214a954ce4), UINT64_C(0x3cc642f670a7f4d3), UINT64_C(0x61ed15c371015d41)},
    {UINT64_C(0xc5d65cc5d7cda458), UINT64_C(0x48b37fdc12863b8a), UINT64_C(0xe863bfdd9da8bb2b), UINT64_C(0x3f97a992fa41c34b), UINT64_C(0x36adc8a913d8046e), UINT64_C(0xe3417f5652ae8b05), UINT64_C(0xcfe3e196bb394123), UINT64_C(0x5b2ae8de6dd1685f), UINT64_C(0x206a72a0399b1ce4), UINT64_C(0xaacbbecda576b8f5), UINT64_C(0x2cc31371371a1f24), UINT64_C(0x59e66840df9e547b)},
    {UINT64_C(0x93110e4f3ada1c62), UINT64_C(0x3ff69642b033727c), UINT64_C(0x6500b4b33a59e790), UINT64_C(0x13de5b4dd4e3a04b), UINT64_C(0xc670c670790794ee), UINT64_C(0x0c79a3518591030b), UINT64_C(0x70306be5d9ab146c), UINT64_C(0xd8070971c8e23759), UINT64_C(0x69a55b52f1a5f6cd), UINT64_C(0xaf9bfbd509608a3f), UINT64_C(0x37b172839da6e473), UINT64_C(0x1a24af34bf028514)},
    {UINT64_C(0xbc31bbffb2460d66), UINT64_C(0xa8979b6a62dc3a53), UINT64_C(0x4d1c6058055b4c64), UINT64_C(0x9a9c38aec40d04e6), UINT64_C(0xa7d93127578602e2), UINT64_C(0x349f91d30c28f960), UINT64_C(0x53c167ee1a9d5b5b), UINT64_C(0x9fc60fec3a91b369), UINT64_C(0x0c3d971903d62bef), UINT64_C(0xee35a7e17ad73532), UINT64_C(0x72d26cf73eddc5de), UINT64_C(0x2bfe1a8181b74c76)},
};

static const uint16_t RC257[18][24] = {
    {13, 89, 169, 172, 51, 4, 203, 164, 209, 179, 115, 63, 37, 153, 234, 25, 130, 230, 105, 135, 201, 88, 144, 95},
    {181, 197, 147, 211, 8, 126, 40, 26, 168, 134, 147, 219, 119, 246, 51, 15, 195, 72, 192, 196, 120, 42, 131, 25},
    {116, 100, 152, 180, 156, 105, 124, 209, 180, 161, 78, 199, 248, 141, 210, 232, 195, 73, 238, 211, 25, 137, 38, 210},
    {218, 65, 120, 26, 166, 42, 117, 152, 186, 175, 195, 68, 8, 136, 243, 176, 246, 56, 245, 13, 111, 153, 245, 17},
    {15, 183, 34, 12, 51, 8, 130, 224, 86, 45, 0, 32, 188, 13, 106, 180, 170, 235, 77, 164, 225, 144, 98, 85},
    {249, 177, 22, 244, 212, 58, 68, 5, 255, 198, 204, 218, 78, 204, 221, 216, 249, 193, 244, 227, 234, 36, 122, 138},
    {65, 122, 118, 196, 109, 50, 223, 42, 122, 125, 4, 214, 156, 117, 162, 132, 68, 16, 247, 106, 187, 235, 83, 183},
    {35, 58, 66, 170, 225, 131, 14, 147, 222, 0, 34, 23, 43, 173, 113, 241, 91, 24, 94, 161, 93, 118, 216, 1},
    {70, 92, 55, 190, 98, 71, 142, 254, 155, 70, 101, 212, 68, 14, 155, 76, 120, 45, 12, 70, 111, 158, 218, 92},
    {54, 144, 83, 166, 47, 90, 227, 225, 136, 244, 222, 4, 218, 83, 177, 39, 255, 210, 242, 141, 223, 59, 133, 123},
    {165, 0, 29, 50, 225, 134, 152, 192, 194, 28, 12, 64, 92, 68, 17, 36, 121, 92, 73, 247, 111, 160, 53, 122},
    {121, 77, 154, 22, 251, 20, 163, 174, 156, 118, 208, 147, 230, 111, 154, 34, 32, 200, 51, 29, 68, 25, 147, 241},
    {80, 32, 186, 178, 76, 113, 237, 164, 221, 217, 38, 208, 149, 65, 141, 221, 224, 103, 56, 255, 216, 4, 231, 167},
    {92, 59, 117, 158, 205, 8, 139, 124, 221, 218, 84, 223, 54, 160, 48, 149, 69, 68, 24, 101, 226, 198, 224, 110},
    {98, 73, 234, 27, 222, 3, 172, 68, 15, 201, 91, 25, 140, 176, 255, 213, 123, 186, 195, 87, 111, 164, 237, 182},
    {255, 200, 39, 248, 145, 137, 35, 72, 196, 123, 180, 176, 254, 167, 108, 24, 100, 180, 183, 62, 15, 214, 175, 220},
    {167, 96, 243, 177, 35, 71, 150, 108, 18, 81, 90, 239, 6, 59, 132, 77, 173, 125, 22, 14, 169, 206, 73, 0},
    {34, 23, 43, 173, 113, 241, 91, 24, 94, 161, 93, 118, 216, 1, 93, 122, 143, 61, 227, 245, 28, 30, 121, 105},
};

static const uint64_t IV_B[12] = {
    UINT64_C(0x243f6a8885a308d3), UINT64_C(0x13198a2e03707344), UINT64_C(0xa4093822299f31d0), UINT64_C(0x082efa98ec4e6c89),
    UINT64_C(0x452821e638d01377), UINT64_C(0xbe5466cf34e90c6c), UINT64_C(0xc0ac29b7c97c50dd), UINT64_C(0x3f84d5b5b5470917),
    UINT64_C(0x9216d5d98979fb1b), UINT64_C(0xd1310ba698dfb5ac), UINT64_C(0x2ffd72dbd01adfb7), UINT64_C(0xb8e1afed6a267e96)
};

static const uint16_t IV_R[24] = {
    43, 61, 81, 103, 127, 153, 181, 211, 243, 20, 56, 94,
    134, 176, 220, 9, 57, 107, 159, 213, 12, 70, 130, 192
};

static const uint16_t ALPHA[12] = {
    11, 17, 29, 37, 43, 53, 7, 13, 19, 31, 47, 59
};
static const uint16_t BETA[12] = {
    5, 23, 41, 3, 27, 49, 9, 35, 15, 45, 21, 61
};
static const uint16_t GAMMA[12] = {
    7, 19, 33, 47, 13, 29, 43, 57, 11, 25, 39, 53
};
static const uint16_t PI[12] = {
    0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5
};
static const uint16_t PSI[24] = {
    0, 5, 10, 15, 20, 1, 6, 11, 16, 21, 2, 7,
    12, 17, 22, 3, 8, 13, 18, 23, 4, 9, 14, 19
};

static uint64_t rotl64(uint64_t x, unsigned n) {
    n &= 63u;
    if (n == 0u) {
        return x;
    }
    return (uint64_t)((x << n) | (x >> (64u - n)));
}

static uint64_t load64_le(const uint8_t *p) {
    return ((uint64_t)p[0]) |
           ((uint64_t)p[1] << 8) |
           ((uint64_t)p[2] << 16) |
           ((uint64_t)p[3] << 24) |
           ((uint64_t)p[4] << 32) |
           ((uint64_t)p[5] << 40) |
           ((uint64_t)p[6] << 48) |
           ((uint64_t)p[7] << 56);
}

static void store64_le(uint8_t *p, uint64_t x) {
    for (unsigned i = 0; i < 8u; ++i) {
        p[i] = (uint8_t)((x >> (8u * i)) & 0xffu);
    }
}

static void store32_le(uint8_t *p, uint32_t x) {
    for (unsigned i = 0; i < 4u; ++i) {
        p[i] = (uint8_t)((x >> (8u * i)) & 0xffu);
    }
}

static uint16_t cube_mod257(uint32_t x) {
    x %= 257u;
    return (uint16_t)((x * x % 257u) * x % 257u);
}

static void permute(uint64_t b[12], uint16_t r_state[24], unsigned rounds) {
    uint64_t lift[12];
    uint64_t mixed[12];
    uint16_t residue_mixed[24];

    for (unsigned r = 0u; r < rounds; ++r) {
        for (unsigned i = 0u; i < 12u; ++i) {
            uint64_t a = (uint64_t)r_state[(2u * i) % 24u];
            uint64_t c = (uint64_t)r_state[(2u * i + 1u) % 24u];
            uint64_t x = (uint64_t)((a + 1u) * K1[i] + (c + 1u) * K2[i] + RC64[r][i]);
            uint64_t y = rotl64((((a + 1u) * UINT64_C(0x9E3779B185EBCA87)) ^ ((c + 1u) * UINT64_C(0xC2B2AE3D27D4EB4F))), (7u * i + 3u * r + 1u) % 64u);
            lift[i] = x ^ y;
        }

        for (unsigned i = 0u; i < 12u; ++i) {
            uint64_t t = b[i] + rotl64(b[(i + 1u) % 12u], ALPHA[i]) + lift[i];
            t ^= rotl64(b[(i + 4u) % 12u], BETA[i]);
            t += rotl64(b[(i + 8u) % 12u], GAMMA[i]);
            t ^= rotl64(lift[(i + 3u) % 12u], (i * 9u + r * 5u + 1u) % 64u);
            mixed[i] = t;
        }
        for (unsigned i = 0u; i < 12u; ++i) {
            b[i] = mixed[PI[i]] ^ lift[(5u * i + 7u) % 12u];
        }

        for (unsigned j = 0u; j < 24u; ++j) {
            uint32_t injected = (uint32_t)((b[j % 12u] >> (j < 12u ? 0u : 32u)) & 0xffu);
            uint32_t x = (uint32_t)r_state[j]
                + 3u * (uint32_t)r_state[(j + 1u) % 24u]
                + 5u * (uint32_t)r_state[(j + 7u) % 24u]
                + 7u * (uint32_t)r_state[(j + 13u) % 24u]
                + injected
                + (uint32_t)RC257[r][j];
            residue_mixed[j] = cube_mod257(x);
        }
        uint16_t next_r[24];
        for (unsigned j = 0u; j < 24u; ++j) {
            next_r[j] = residue_mixed[PSI[j]];
        }
        memcpy(r_state, next_r, sizeof(next_r));
    }
}

static void initial_state(kryon_ctx *ctx, uint32_t out_bits) {
    memcpy(ctx->binary, IV_B, sizeof(IV_B));
    memcpy(ctx->residue, IV_R, sizeof(IV_R));
    ctx->binary[0] ^= VERSION_TAG;
    ctx->binary[1] ^= rotl64(VERSION_TAG, out_bits / 8u);
    ctx->binary[10] ^= (uint64_t)out_bits;
    ctx->binary[11] ^= (((uint64_t)out_bits << 32) | (uint64_t)KRYON_BLOCK_SIZE);
    for (unsigned j = 0u; j < 24u; ++j) {
        ctx->residue[j] = (uint16_t)(((uint32_t)ctx->residue[j] + ((out_bits >> (j % 8u)) & 0xffu) + j + ((VERSION_TAG >> (j % 56u)) & 0xffu)) % 257u);
    }
}

static void absorb_block(kryon_ctx *ctx, const uint8_t block[KRYON_BLOCK_SIZE], int is_final) {
    uint64_t idx = ctx->block_index;
    uint64_t words[4];
    for (unsigned i = 0u; i < 4u; ++i) {
        words[i] = load64_le(block + 8u * i);
    }
    for (unsigned i = 0u; i < 4u; ++i) {
        unsigned lane = (unsigned)((i + (idx & 3u)) % 12u);
        ctx->binary[lane] ^= words[i];
        ctx->binary[(lane + 5u) % 12u] += rotl64(words[i] ^ K1[(idx + i) % 12u], (unsigned)((idx + 13u * i) % 64u));
    }

    ctx->binary[4] ^= ((idx << 1u) | (uint64_t)(is_final != 0));
    ctx->binary[5] ^= rotl64((idx + 1u) * UINT64_C(0x9E3779B185EBCA87), (unsigned)(idx % 64u));
    ctx->binary[11] ^= ((idx << 48u) ^ ((uint64_t)KRYON_BLOCK_SIZE << 40u) ^ ((uint64_t)ctx->out_bits << 8u) ^ VERSION_TAG);

    if (is_final) {
        ctx->binary[8] ^= ctx->total_len;
        ctx->binary[9] ^= rotl64((ctx->total_len ^ ((uint64_t)ctx->out_bits << 32u)), 17u);
        ctx->binary[10] ^= rotl64((ctx->total_len + 1u) * UINT64_C(0xD6E8FEB86659FD93), 29u);
    }

    for (unsigned j = 0u; j < 24u; ++j) {
        uint32_t byte_a = (uint32_t)block[j % KRYON_BLOCK_SIZE];
        uint32_t byte_b = (uint32_t)block[(j * 7u + 13u) % KRYON_BLOCK_SIZE];
        uint32_t byte_c = (uint32_t)block[(j * 11u + 5u) % KRYON_BLOCK_SIZE];
        uint32_t length_inject = is_final ? (uint32_t)((ctx->total_len >> ((j % 8u) * 8u)) & 0xffu) : 0u;
        ctx->residue[j] = (uint16_t)(((uint32_t)ctx->residue[j] + byte_a + 3u * byte_b + 5u * byte_c + j + (uint32_t)(idx & 0xffu) + length_inject + (is_final ? 17u : 0u)) % 257u);
    }

    permute(ctx->binary, ctx->residue, is_final ? 14u : 10u);
    ctx->block_index += 1u;
}

const char *kryon_native_version(void) {
    return "kryon-native-c-reference-0.8.0";
}

kryon_status kryon_init(kryon_ctx *ctx, uint32_t out_bits) {
    if (ctx == 0) {
        return KRYON_ERR_INVALID_ARGUMENT;
    }
    if (!(out_bits == 256u || out_bits == 384u || out_bits == 512u)) {
        return KRYON_ERR_INVALID_ARGUMENT;
    }
    memset(ctx, 0, sizeof(*ctx));
    ctx->out_bits = out_bits;
    initial_state(ctx, out_bits);
    return KRYON_OK;
}

kryon_status kryon_update(kryon_ctx *ctx, const uint8_t *data, size_t len) {
    if (ctx == 0 || (data == 0 && len != 0u)) {
        return KRYON_ERR_INVALID_ARGUMENT;
    }
    if (len == 0u) {
        return KRYON_OK;
    }
    if (ctx->total_len > UINT64_MAX - (uint64_t)len) {
        return KRYON_ERR_INVALID_ARGUMENT;
    }
    ctx->total_len += (uint64_t)len;

    size_t offset = 0u;
    while (offset < len) {
        size_t space = KRYON_BLOCK_SIZE - ctx->tail_len;
        size_t take = (len - offset < space) ? (len - offset) : space;
        memcpy(ctx->tail + ctx->tail_len, data + offset, take);
        ctx->tail_len += take;
        offset += take;
        if (ctx->tail_len == KRYON_BLOCK_SIZE) {
            absorb_block(ctx, ctx->tail, 0);
            ctx->tail_len = 0u;
        }
    }
    return KRYON_OK;
}

kryon_status kryon_final(const kryon_ctx *ctx, uint8_t *out, size_t out_len) {
    if (ctx == 0 || out == 0 || out_len < (size_t)(ctx->out_bits / 8u)) {
        return KRYON_ERR_INVALID_ARGUMENT;
    }
    kryon_ctx h = *ctx;
    uint8_t payload[64];
    size_t pos = 0u;
    memcpy(payload + pos, h.tail, h.tail_len);
    pos += h.tail_len;
    payload[pos++] = 0x80u;
    size_t trailer_len = 16u;
    while (((pos + trailer_len) % KRYON_BLOCK_SIZE) != 0u) {
        payload[pos++] = 0u;
    }
    store64_le(payload + pos, h.total_len);
    pos += 8u;
    store32_le(payload + pos, h.out_bits);
    pos += 4u;
    payload[pos++] = 'C';
    payload[pos++] = 'W';
    payload[pos++] = '0';
    payload[pos++] = '2';

    for (size_t offset = 0u; offset < pos; offset += KRYON_BLOCK_SIZE) {
        int is_final = (offset + KRYON_BLOCK_SIZE == pos);
        absorb_block(&h, payload + offset, is_final);
    }

    for (unsigned i = 0u; i < 12u; ++i) {
        uint64_t a = (uint64_t)h.residue[(2u * i) % 24u];
        uint64_t c = (uint64_t)h.residue[(2u * i + 1u) % 24u];
        uint64_t d = (uint64_t)h.residue[(2u * i + 5u) % 24u];
        uint64_t fold = (a & 0x1ffu) | ((c & 0x1ffu) << 9u) | ((d & 0x1ffu) << 18u);
        h.binary[i] ^= rotl64(fold * UINT64_C(0xD6E8FEB86659FD93), (11u * i) % 64u);
        h.binary[i] += rotl64(K2[i] ^ h.total_len, (7u * i + 3u) % 64u);
    }
    for (unsigned j = 0u; j < 24u; ++j) {
        h.residue[j] = (uint16_t)(((uint32_t)h.residue[j] + ((h.binary[j % 12u] >> (j % 32u)) & 0xffu) + RC257[0][j] + (h.out_bits & 0xffu)) % 257u);
    }
    permute(h.binary, h.residue, 16u);
    for (unsigned i = 0u; i < 12u; ++i) {
        uint64_t a = (uint64_t)h.residue[(2u * i) % 24u];
        uint64_t c = (uint64_t)h.residue[(2u * i + 11u) % 24u];
        h.binary[i] ^= rotl64(((a + 1u) * K1[i]) ^ ((c + 1u) * K2[i]), (3u + 5u * i) % 64u);
    }
    permute(h.binary, h.residue, 6u);

    uint8_t full[96];
    for (unsigned i = 0u; i < 12u; ++i) {
        store64_le(full + 8u * i, h.binary[i]);
    }
    memcpy(out, full, (size_t)(h.out_bits / 8u));
    return KRYON_OK;
}

kryon_status kryon_digest(const uint8_t *data, size_t len, uint32_t out_bits, uint8_t *out, size_t out_len) {
    kryon_ctx ctx;
    kryon_status st = kryon_init(&ctx, out_bits);
    if (st != KRYON_OK) {
        return st;
    }
    st = kryon_update(&ctx, data, len);
    if (st != KRYON_OK) {
        return st;
    }
    return kryon_final(&ctx, out, out_len);
}
