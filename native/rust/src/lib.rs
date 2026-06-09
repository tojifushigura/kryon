//! Kryon native Rust reference port.
//!
//! This v0.8 crate mirrors the Python canonical Kryon implementation and
//! is intended for cross-checking, future acceleration work, and fuzzing.
//! Kryon remains an unaudited research hash and must not be used as a
//! production replacement for SHA-2, SHA-3, BLAKE2, or BLAKE3.

const BLOCK_SIZE: usize = 32;
const VERSION_TAG: u64 = 0x4352574556323032;

const K1: [u64; 12] = [
    0xb762e9fdd7731f3b,
    0xfc54b43362125049,
    0x99bb41ce1f9f6bc2,
    0x78f8118406b1b765,
    0x260c848607528802,
    0x7be8e7f71c49c052,
    0xafb75e07e0840f0d,
    0x0f597582042fa91b,
    0x14536abe7afba732,
    0xe6d36de84ff057e2,
    0x520531b51228653d,
    0x3c7d758ec628c034,
];

const K2: [u64; 12] = [
    0xd1d1cc5a1e22a635,
    0xe33b725a0f9df976,
    0x0e0667fea990a1ef,
    0xeac86c8c69964150,
    0xb29d7cef3bee15cc,
    0x8c5385bd40adc713,
    0xcee03400f71b2029,
    0xacddd9673e87cf53,
    0xfad087297cacd9be,
    0x3f52953ba7e43eda,
    0xaf3e9fcef32fcdf1,
    0x8732b441ead04b9a,
];

const RC64: [[u64; 12]; 18] = [
    [0xcf835f9ca21757ad, 0x2e43a162712f13d0, 0x5ce4fc5d52aa4fe0, 0xeccd04aec817e999, 0x20923aad14936640, 0x0d9c9e6dd7345af0, 0x80039fe957b219ce, 0x5cb55b1284bfc7ba, 0xde794f6fabaec79d, 0xae160eecb2206ae9, 0x83204f6b73d372a7, 0x7a96e0fece44f182],
    [0x38779d0b93e1996e, 0x7667187a36d44275, 0xa70a7e379eaf848f, 0xd05d1f0979585322, 0x3b2dddd4435f12d3, 0xf1fd4786fa9c726b, 0xf7e8530cfa849a5b, 0x8e820d98aca5a47a, 0xb77dd8e6b9796054, 0x48064cd0dc5ba430, 0x2c5b2fd2bd723c83, 0xc941741d365a3493],
    [0xd1e58ee5881afdf9, 0xe4aca897c78bd5a9, 0x46481ef2102b92c9, 0xf920cf5d4afc942a, 0xb9e80f1f063ffba9, 0xed050c88d2d4ac09, 0xbe3f1f93e2672e9e, 0x58807584480af818, 0x24c2757ba89be3d7, 0x0ad0362e18077b3c, 0x74a5f07248cf0343, 0xf5a13a7ff17f03f2],
    [0x0833759e383ab521, 0xc4146a31a2439cc4, 0x46aab5cad80c1672, 0x1229c3ac037d9cdf, 0xca56686ef5577f4a, 0xc170ead2e066aadd, 0x2027480033a7293a, 0xc95d8ff891429bc4, 0x67d7f3565627eba4, 0x23320088d2c03aa4, 0x578932b1da16f10c, 0xdb3940d94b357ee7],
    [0x1eb3de0dbbbdebb5, 0x3fb7c60bab9d7f91, 0x8780b1c9e9cdee15, 0xbc204d95b9ac2573, 0x49d1094064f12848, 0x0ecfd4d30b1f4e51, 0xeda4d5ebcb006250, 0x77261ba17addbbaf, 0xa9635fc6e9753fcf, 0xdb4afbe059919603, 0x53adc828316bc118, 0xd47c8b6ad8eb62b4],
    [0x1aae66fcdec903ed, 0xa3b95549e1af3a64, 0xabb81c94570876c5, 0x6d4725ecd79be3db, 0x0ac7fd2da167f881, 0x9855a9f96d2f9eff, 0xa982f52a51acac0d, 0x66163f5b99cc6c05, 0x65ca5f344c376c74, 0x1844ce4b3bb8f19f, 0xa05cee49f7f07365, 0x14d38aba71d769b7],
    [0x51118f4e0e77d235, 0xc9f739eb307602d8, 0xdf88d9400223c713, 0x69fde9a3572e4410, 0x87a62cfe6af5a880, 0x02672f4d16226c08, 0x8f13bb2670ecf882, 0x4a12fff8149fbfde, 0xc0980af3074ded0b, 0x99962198b76be99e, 0xb5f0cd6049da4bc3, 0x6436e835b2305e0e],
    [0x53659989ba2cea9d, 0x109e4039f22f1785, 0xf0948b87f2d036ef, 0x76fc517dec7aea3e, 0xcf68fc0e6429b5cb, 0x7f811c4300c993d1, 0xd91aea71539f4e9d, 0x62ef157bd50242b3, 0x9d61c6def718eb9b, 0xe707aa54236d676f, 0x9c6e75d5cf4eb464, 0x352a1278b3c97994],
    [0xd2be4327bf86f83f, 0xa50541e0f1e5f327, 0xe4976270660b75c1, 0xba3772d38f69cca8, 0x719e2e6a58b7eb24, 0x63c5d71ed2f775c2, 0x487d0694d7a62a8b, 0x1147f9a644881e2e, 0x2f97225d906249f9, 0xe5accfd8bde21bfd, 0x80c41354572005fa, 0xefa90fc99406ef73],
    [0x9b795fdcb78fc095, 0x951cb24ba0e5a9f2, 0xd75505700926b853, 0x0dc71628029f1740, 0x4bb69a95d2f076eb, 0x28f33f44091b622d, 0x583d15d6398d6a3c, 0x1da7ac61de2fe616, 0x50561ea1de23a6a0, 0x604b52996dadf9f4, 0x4a810be4fb99e614, 0x2aaf500b0628002f],
    [0x456a1cf5801532b0, 0x0e918f0623329f1f, 0xf51f9d36d5f953ff, 0xdd93408831cc4f3c, 0x7f39e3494d232c15, 0xf9ebfd359f4eb92a, 0x4b4d632c65400ffd, 0x9187b9dc2deb2f88, 0x40405fc82a849b07, 0x1fe9f4a2a8bb7ab6, 0x573c4a0e11315ed2, 0x1f708dfa9b4bbef6],
    [0x5d1ed5401b59248d, 0xd1387ecdf0efc15d, 0xec0a89c1779bedd8, 0x28d6c002a269721b, 0xbb796bf7e432b7b1, 0xcfb3694a19176508, 0xc39d872df5ddfff9, 0x043a2a0515d47ab3, 0x0269ded3686cf365, 0x6467c623c9c5037c, 0x305a42e98928c12e, 0xcedb184b97ab8875],
    [0x2c00b8a5c14ba580, 0x84cae4258110cf1f, 0x480d10f83013d133, 0xcef7d78f9f16efcc, 0x6dec6b6c89e6480f, 0x4d3aceb72e2f38e3, 0xf93401240d7befc0, 0x45fde0135a0311c8, 0xf2345a48ac69a57e, 0x02065ef50a978cd4, 0xee2f678931e04155, 0x9ab7a2b4e22544f1],
    [0x9c0e2b08b25a71bd, 0x45e89fdecf64f99f, 0x08de71d7242f01a7, 0x8a0ffa261091a8f6, 0x740ae69d54557277, 0x99f2df91e47009a5, 0xefba37d5ab19d262, 0x31ec0c6f0c3e5747, 0x1aed868a5e840fc1, 0x56950fa0799abcc8, 0x69afef92c795cdd1, 0xe1ebe2321f85599e],
    [0xdecbb96ae5a370cc, 0x7bc325b746a44ed6, 0x5f98e40bc421d4d1, 0x95214e4c9393c21f, 0xe440693fd38455eb, 0x6e9931a126290e28, 0xbb9525d88a075f7b, 0xf09c7124cb421ca8, 0x7a615db6b0ffa889, 0x1ec6da214a954ce4, 0x3cc642f670a7f4d3, 0x61ed15c371015d41],
    [0xc5d65cc5d7cda458, 0x48b37fdc12863b8a, 0xe863bfdd9da8bb2b, 0x3f97a992fa41c34b, 0x36adc8a913d8046e, 0xe3417f5652ae8b05, 0xcfe3e196bb394123, 0x5b2ae8de6dd1685f, 0x206a72a0399b1ce4, 0xaacbbecda576b8f5, 0x2cc31371371a1f24, 0x59e66840df9e547b],
    [0x93110e4f3ada1c62, 0x3ff69642b033727c, 0x6500b4b33a59e790, 0x13de5b4dd4e3a04b, 0xc670c670790794ee, 0x0c79a3518591030b, 0x70306be5d9ab146c, 0xd8070971c8e23759, 0x69a55b52f1a5f6cd, 0xaf9bfbd509608a3f, 0x37b172839da6e473, 0x1a24af34bf028514],
    [0xbc31bbffb2460d66, 0xa8979b6a62dc3a53, 0x4d1c6058055b4c64, 0x9a9c38aec40d04e6, 0xa7d93127578602e2, 0x349f91d30c28f960, 0x53c167ee1a9d5b5b, 0x9fc60fec3a91b369, 0x0c3d971903d62bef, 0xee35a7e17ad73532, 0x72d26cf73eddc5de, 0x2bfe1a8181b74c76]
];

const RC257: [[u16; 24]; 18] = [
    [13, 89, 169, 172, 51, 4, 203, 164, 209, 179, 115, 63, 37, 153, 234, 25, 130, 230, 105, 135, 201, 88, 144, 95],
    [181, 197, 147, 211, 8, 126, 40, 26, 168, 134, 147, 219, 119, 246, 51, 15, 195, 72, 192, 196, 120, 42, 131, 25],
    [116, 100, 152, 180, 156, 105, 124, 209, 180, 161, 78, 199, 248, 141, 210, 232, 195, 73, 238, 211, 25, 137, 38, 210],
    [218, 65, 120, 26, 166, 42, 117, 152, 186, 175, 195, 68, 8, 136, 243, 176, 246, 56, 245, 13, 111, 153, 245, 17],
    [15, 183, 34, 12, 51, 8, 130, 224, 86, 45, 0, 32, 188, 13, 106, 180, 170, 235, 77, 164, 225, 144, 98, 85],
    [249, 177, 22, 244, 212, 58, 68, 5, 255, 198, 204, 218, 78, 204, 221, 216, 249, 193, 244, 227, 234, 36, 122, 138],
    [65, 122, 118, 196, 109, 50, 223, 42, 122, 125, 4, 214, 156, 117, 162, 132, 68, 16, 247, 106, 187, 235, 83, 183],
    [35, 58, 66, 170, 225, 131, 14, 147, 222, 0, 34, 23, 43, 173, 113, 241, 91, 24, 94, 161, 93, 118, 216, 1],
    [70, 92, 55, 190, 98, 71, 142, 254, 155, 70, 101, 212, 68, 14, 155, 76, 120, 45, 12, 70, 111, 158, 218, 92],
    [54, 144, 83, 166, 47, 90, 227, 225, 136, 244, 222, 4, 218, 83, 177, 39, 255, 210, 242, 141, 223, 59, 133, 123],
    [165, 0, 29, 50, 225, 134, 152, 192, 194, 28, 12, 64, 92, 68, 17, 36, 121, 92, 73, 247, 111, 160, 53, 122],
    [121, 77, 154, 22, 251, 20, 163, 174, 156, 118, 208, 147, 230, 111, 154, 34, 32, 200, 51, 29, 68, 25, 147, 241],
    [80, 32, 186, 178, 76, 113, 237, 164, 221, 217, 38, 208, 149, 65, 141, 221, 224, 103, 56, 255, 216, 4, 231, 167],
    [92, 59, 117, 158, 205, 8, 139, 124, 221, 218, 84, 223, 54, 160, 48, 149, 69, 68, 24, 101, 226, 198, 224, 110],
    [98, 73, 234, 27, 222, 3, 172, 68, 15, 201, 91, 25, 140, 176, 255, 213, 123, 186, 195, 87, 111, 164, 237, 182],
    [255, 200, 39, 248, 145, 137, 35, 72, 196, 123, 180, 176, 254, 167, 108, 24, 100, 180, 183, 62, 15, 214, 175, 220],
    [167, 96, 243, 177, 35, 71, 150, 108, 18, 81, 90, 239, 6, 59, 132, 77, 173, 125, 22, 14, 169, 206, 73, 0],
    [34, 23, 43, 173, 113, 241, 91, 24, 94, 161, 93, 118, 216, 1, 93, 122, 143, 61, 227, 245, 28, 30, 121, 105]
];

const IV_B: [u64; 12] = [
    0x243f6a8885a308d3,
    0x13198a2e03707344,
    0xa4093822299f31d0,
    0x082efa98ec4e6c89,
    0x452821e638d01377,
    0xbe5466cf34e90c6c,
    0xc0ac29b7c97c50dd,
    0x3f84d5b5b5470917,
    0x9216d5d98979fb1b,
    0xd1310ba698dfb5ac,
    0x2ffd72dbd01adfb7,
    0xb8e1afed6a267e96,
];

const IV_R: [u16; 24] = [43, 61, 81, 103, 127, 153, 181, 211, 243, 20, 56, 94, 134, 176, 220, 9, 57, 107, 159, 213, 12, 70, 130, 192];

const ALPHA: [u16; 12] = [11, 17, 29, 37, 43, 53, 7, 13, 19, 31, 47, 59];

const BETA: [u16; 12] = [5, 23, 41, 3, 27, 49, 9, 35, 15, 45, 21, 61];

const GAMMA: [u16; 12] = [7, 19, 33, 47, 13, 29, 43, 57, 11, 25, 39, 53];

const PI: [usize; 12] = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5];

const PSI: [usize; 24] = [0, 5, 10, 15, 20, 1, 6, 11, 16, 21, 2, 7, 12, 17, 22, 3, 8, 13, 18, 23, 4, 9, 14, 19];


#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Error {
    InvalidOutputBits,
    InvalidRoundProfile,
    MessageTooLarge,
    InternalBlockSize,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RoundProfile {
    pub absorb_rounds: usize,
    pub final_absorb_rounds: usize,
    pub final_mix_rounds: usize,
    pub post_mix_rounds: usize,
}

impl RoundProfile {
    pub const fn canonical() -> Self {
        Self {
            absorb_rounds: 10,
            final_absorb_rounds: 14,
            final_mix_rounds: 16,
            post_mix_rounds: 6,
        }
    }

    pub fn validate(&self) -> Result<(), Error> {
        let values = [
            self.absorb_rounds,
            self.final_absorb_rounds,
            self.final_mix_rounds,
            self.post_mix_rounds,
        ];
        if values.iter().any(|&v| v == 0 || v > 18) {
            return Err(Error::InvalidRoundProfile);
        }
        Ok(())
    }
}

impl Default for RoundProfile {
    fn default() -> Self {
        Self::canonical()
    }
}

#[derive(Debug, Clone)]
pub struct Context {
    out_bits: u16,
    profile: RoundProfile,
    b: [u64; 12],
    r_state: [u16; 24],
    tail: Vec<u8>,
    total_len: u64,
    block_index: u64,
}

fn rotl64(x: u64, n: u32) -> u64 {
    x.rotate_left(n & 63)
}

fn validate_out_bits(out_bits: u16) -> Result<(), Error> {
    match out_bits {
        256 | 384 | 512 => Ok(()),
        _ => Err(Error::InvalidOutputBits),
    }
}

fn initial_state(out_bits: u16) -> Result<([u64; 12], [u16; 24]), Error> {
    validate_out_bits(out_bits)?;
    let mut b = IV_B;
    let mut r_state = IV_R;

    b[0] ^= VERSION_TAG;
    b[1] ^= rotl64(VERSION_TAG, u32::from(out_bits / 8));
    b[10] ^= u64::from(out_bits);
    b[11] ^= (u64::from(out_bits) << 32) | (BLOCK_SIZE as u64);

    for j in 0..24 {
        let out_part = ((u64::from(out_bits) >> (j % 8)) & 0xff) as u16;
        let tag_part = ((VERSION_TAG >> (j % 56)) & 0xff) as u16;
        r_state[j] = ((u32::from(r_state[j]) + u32::from(out_part) + j as u32 + u32::from(tag_part)) % 257) as u16;
    }

    Ok((b, r_state))
}

fn permute(binary_state: &[u64; 12], residue_state: &[u16; 24], rounds: usize) -> Result<([u64; 12], [u16; 24]), Error> {
    if rounds > RC64.len() {
        return Err(Error::InvalidRoundProfile);
    }

    let mut b = *binary_state;
    let mut r_state = *residue_state;

    for round in 0..rounds {
        let mut lift = [0u64; 12];
        for i in 0..12 {
            let a = u64::from(r_state[(2 * i) % 24]);
            let c = u64::from(r_state[(2 * i + 1) % 24]);
            let x = (a + 1)
                .wrapping_mul(K1[i])
                .wrapping_add((c + 1).wrapping_mul(K2[i]))
                .wrapping_add(RC64[round][i]);
            let y = rotl64(
                ((a + 1).wrapping_mul(0x9e3779b185ebca87))
                    ^ ((c + 1).wrapping_mul(0xc2b2ae3d27d4eb4f)),
                ((7 * i + 3 * round + 1) % 64) as u32,
            );
            lift[i] = x ^ y;
        }

        let mut mixed = [0u64; 12];
        for i in 0..12 {
            let mut t = b[i]
                .wrapping_add(rotl64(b[(i + 1) % 12], u32::from(ALPHA[i])))
                .wrapping_add(lift[i]);
            t ^= rotl64(b[(i + 4) % 12], u32::from(BETA[i]));
            t = t.wrapping_add(rotl64(b[(i + 8) % 12], u32::from(GAMMA[i])));
            t ^= rotl64(lift[(i + 3) % 12], ((i * 9 + round * 5 + 1) % 64) as u32);
            mixed[i] = t;
        }

        let mut next_b = [0u64; 12];
        for i in 0..12 {
            next_b[i] = mixed[PI[i]] ^ lift[(5 * i + 7) % 12];
        }
        b = next_b;

        let mut residue_mixed = [0u16; 24];
        for j in 0..24 {
            let injected = ((b[j % 12] >> if j < 12 { 0 } else { 32 }) & 0xff) as u32;
            let x = (u32::from(r_state[j])
                + 3 * u32::from(r_state[(j + 1) % 24])
                + 5 * u32::from(r_state[(j + 7) % 24])
                + 7 * u32::from(r_state[(j + 13) % 24])
                + injected
                + u32::from(RC257[round][j]))
                % 257;
            residue_mixed[j] = ((x * x % 257) * x % 257) as u16;
        }

        let mut next_r = [0u16; 24];
        for j in 0..24 {
            next_r[j] = residue_mixed[PSI[j]];
        }
        r_state = next_r;
    }

    Ok((b, r_state))
}

fn padding_blocks(tail: &[u8], total_len: u64, out_bits: u16) -> Vec<u8> {
    let mut payload = Vec::with_capacity(tail.len() + 1 + BLOCK_SIZE * 2);
    payload.extend_from_slice(tail);
    payload.push(0x80);

    let mut trailer = Vec::with_capacity(16);
    trailer.extend_from_slice(&total_len.to_le_bytes());
    trailer.extend_from_slice(&(u32::from(out_bits)).to_le_bytes());
    trailer.extend_from_slice(b"CW02");

    while (payload.len() + trailer.len()) % BLOCK_SIZE != 0 {
        payload.push(0);
    }
    payload.extend_from_slice(&trailer);
    payload
}

impl Context {
    pub fn new(out_bits: u16) -> Result<Self, Error> {
        Self::with_profile(out_bits, RoundProfile::canonical())
    }

    pub fn with_profile(out_bits: u16, profile: RoundProfile) -> Result<Self, Error> {
        profile.validate()?;
        let (b, r_state) = initial_state(out_bits)?;
        Ok(Self {
            out_bits,
            profile,
            b,
            r_state,
            tail: Vec::with_capacity(BLOCK_SIZE),
            total_len: 0,
            block_index: 0,
        })
    }

    pub fn update(&mut self, data: &[u8]) -> Result<(), Error> {
        if data.is_empty() {
            return Ok(());
        }
        let new_total = self
            .total_len
            .checked_add(data.len() as u64)
            .ok_or(Error::MessageTooLarge)?;
        self.total_len = new_total;
        self.tail.extend_from_slice(data);

        while self.tail.len() >= BLOCK_SIZE {
            let block: Vec<u8> = self.tail.drain(..BLOCK_SIZE).collect();
            self.absorb_block(&block, false)?;
        }
        Ok(())
    }

    pub fn finalize(&self) -> Result<Vec<u8>, Error> {
        let mut h = self.clone();
        let final_payload = padding_blocks(&h.tail, h.total_len, h.out_bits);
        h.tail.clear();
        let final_blocks = final_payload.len() / BLOCK_SIZE;
        for i in 0..final_blocks {
            let start = i * BLOCK_SIZE;
            let block = &final_payload[start..start + BLOCK_SIZE];
            h.absorb_block(block, i == final_blocks - 1)?;
        }

        for i in 0..12 {
            let a = u64::from(h.r_state[(2 * i) % 24]);
            let c = u64::from(h.r_state[(2 * i + 1) % 24]);
            let d = u64::from(h.r_state[(2 * i + 5) % 24]);
            let fold = (a & 0x1ff) | ((c & 0x1ff) << 9) | ((d & 0x1ff) << 18);
            h.b[i] ^= rotl64(fold.wrapping_mul(0xd6e8feb86659fd93), ((11 * i) % 64) as u32);
            h.b[i] = h.b[i].wrapping_add(rotl64(K2[i] ^ h.total_len, ((7 * i + 3) % 64) as u32));
        }

        for j in 0..24 {
            h.r_state[j] = ((u32::from(h.r_state[j])
                + ((h.b[j % 12] >> (j % 32)) & 0xff) as u32
                + u32::from(RC257[0][j])
                + u32::from(h.out_bits & 0xff))
                % 257) as u16;
        }

        (h.b, h.r_state) = permute(&h.b, &h.r_state, h.profile.final_mix_rounds)?;

        for i in 0..12 {
            let a = u64::from(h.r_state[(2 * i) % 24]);
            let c = u64::from(h.r_state[(2 * i + 11) % 24]);
            h.b[i] ^= rotl64(((a + 1).wrapping_mul(K1[i])) ^ ((c + 1).wrapping_mul(K2[i])), ((3 + 5 * i) % 64) as u32);
        }

        (h.b, h.r_state) = permute(&h.b, &h.r_state, h.profile.post_mix_rounds)?;

        let mut out = Vec::with_capacity(96);
        for word in h.b {
            out.extend_from_slice(&word.to_le_bytes());
        }
        out.truncate(usize::from(h.out_bits / 8));
        Ok(out)
    }

    pub fn hexdigest(&self) -> Result<String, Error> {
        Ok(hex_encode(&self.finalize()?))
    }

    pub fn digest_size(&self) -> usize {
        usize::from(self.out_bits / 8)
    }

    pub fn block_size(&self) -> usize {
        BLOCK_SIZE
    }

    pub fn total_len(&self) -> u64 {
        self.total_len
    }

    pub fn out_bits(&self) -> u16 {
        self.out_bits
    }

    fn absorb_block(&mut self, block: &[u8], final_block: bool) -> Result<(), Error> {
        if block.len() != BLOCK_SIZE {
            return Err(Error::InternalBlockSize);
        }

        let idx = self.block_index;
        let mut words = [0u64; 4];
        for i in 0..4 {
            let mut buf = [0u8; 8];
            buf.copy_from_slice(&block[i * 8..i * 8 + 8]);
            words[i] = u64::from_le_bytes(buf);
        }

        for i in 0..4 {
            let lane = (i + (idx & 3) as usize) % 12;
            self.b[lane] ^= words[i];
            self.b[(lane + 5) % 12] = self.b[(lane + 5) % 12].wrapping_add(rotl64(
                words[i] ^ K1[(idx as usize + i) % 12],
                ((idx + 13 * i as u64) % 64) as u32,
            ));
        }

        self.b[4] ^= idx.wrapping_shl(1) | (if final_block { 1 } else { 0 });
        self.b[5] ^= rotl64(idx.wrapping_add(1).wrapping_mul(0x9e3779b185ebca87), (idx % 64) as u32);
        self.b[11] ^= (idx << 48) ^ ((BLOCK_SIZE as u64) << 40) ^ (u64::from(self.out_bits) << 8) ^ VERSION_TAG;

        if final_block {
            self.b[8] ^= self.total_len;
            self.b[9] ^= rotl64(self.total_len ^ (u64::from(self.out_bits) << 32), 17);
            self.b[10] ^= rotl64(self.total_len.wrapping_add(1).wrapping_mul(0xd6e8feb86659fd93), 29);
        }

        for j in 0..24 {
            let byte_a = u32::from(block[j % BLOCK_SIZE]);
            let byte_b = u32::from(block[(j * 7 + 13) % BLOCK_SIZE]);
            let byte_c = u32::from(block[(j * 11 + 5) % BLOCK_SIZE]);
            let length_inject = if final_block {
                ((self.total_len >> ((j % 8) * 8)) & 0xff) as u32
            } else {
                0
            };
            self.r_state[j] = ((u32::from(self.r_state[j])
                + byte_a
                + 3 * byte_b
                + 5 * byte_c
                + j as u32
                + (idx & 0xff) as u32
                + length_inject
                + (if final_block { 17 } else { 0 }))
                % 257) as u16;
        }

        let rounds = if final_block {
            self.profile.final_absorb_rounds
        } else {
            self.profile.absorb_rounds
        };
        (self.b, self.r_state) = permute(&self.b, &self.r_state, rounds)?;
        self.block_index = self.block_index.wrapping_add(1);
        Ok(())
    }
}

pub fn digest(data: &[u8], out_bits: u16) -> Result<Vec<u8>, Error> {
    let mut ctx = Context::new(out_bits)?;
    ctx.update(data)?;
    ctx.finalize()
}

pub fn hexdigest(data: &[u8], out_bits: u16) -> Result<String, Error> {
    Ok(hex_encode(&digest(data, out_bits)?))
}

pub fn hex_encode(data: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(data.len() * 2);
    for &byte in data {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}

pub fn version() -> &'static str {
    "kryon-native-rust-0.8.0"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_invalid_output_size() {
        assert_eq!(Context::new(128).unwrap_err(), Error::InvalidOutputBits);
    }

    #[test]
    fn exposes_version() {
        assert!(version().contains("0.8.0"));
    }

    #[test]
    fn kat_empty_384() {
        assert_eq!(
            hexdigest(b"", 384).unwrap(),
            "ce22c2f741871b79ad60664f786b3e314cab314d5c9e8d7b63c725ba7596e681f9de5dccbd19d8243c82e57a22ab25ae"
        );
    }

    #[test]
    fn kat_abc_384() {
        assert_eq!(
            hexdigest(b"abc", 384).unwrap(),
            "06f61fabf777a7653a46c921eb46bc9a52c876f0cb7afd60495118b5b81f73830b0cab537db8aea4bade55d717f71370"
        );
    }

    #[test]
    fn streaming_equals_one_shot() {
        let mut ctx = Context::new(384).unwrap();
        ctx.update(b"a").unwrap();
        ctx.update(b"b").unwrap();
        ctx.update(b"c").unwrap();
        assert_eq!(ctx.hexdigest().unwrap(), hexdigest(b"abc", 384).unwrap());
    }

    #[test]
    fn finalize_does_not_consume_context() {
        let mut ctx = Context::new(384).unwrap();
        ctx.update(b"ab").unwrap();
        let before = ctx.hexdigest().unwrap();
        ctx.update(b"c").unwrap();
        assert_ne!(before, ctx.hexdigest().unwrap());
        assert_eq!(ctx.hexdigest().unwrap(), hexdigest(b"abc", 384).unwrap());
    }

    #[test]
    fn digest_sizes() {
        assert_eq!(digest(b"abc", 256).unwrap().len(), 32);
        assert_eq!(digest(b"abc", 384).unwrap().len(), 48);
        assert_eq!(digest(b"abc", 512).unwrap().len(), 64);
    }
}
