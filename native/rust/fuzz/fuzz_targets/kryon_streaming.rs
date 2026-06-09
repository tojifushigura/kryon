#![no_main]

use libfuzzer_sys::fuzz_target;
use kryon_native::{digest, Context};

fuzz_target!(|data: &[u8]| {
    for &bits in &[256_u16, 384_u16, 512_u16] {
        let expected = digest(data, bits).unwrap();
        let mid = data.len() / 2;
        let mut ctx = Context::new(bits).unwrap();
        ctx.update(&data[..mid]).unwrap();
        let _ = ctx.finalize().unwrap();
        ctx.update(&data[mid..]).unwrap();
        assert_eq!(ctx.finalize().unwrap(), expected);
    }
});
