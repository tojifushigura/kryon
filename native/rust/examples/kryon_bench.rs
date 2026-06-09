use kryon_native::digest;
use std::env;
use std::time::Instant;

fn main() {
    let args: Vec<String> = env::args().collect();
    let iterations: usize = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(2000);
    let size: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(4096);
    let mut data = vec![0u8; size];
    for (i, b) in data.iter_mut().enumerate() {
        *b = ((i * 131 + 17) & 0xff) as u8;
    }

    let started = Instant::now();
    let mut acc = 0u8;
    for i in 0..iterations {
        data[0] = data[0].wrapping_add((i & 0xff) as u8);
        let d = digest(&data, 384);
        acc ^= d[0];
    }
    let elapsed = started.elapsed();
    let total_bytes = iterations as f64 * size as f64;
    let mib_s = total_bytes / elapsed.as_secs_f64() / (1024.0 * 1024.0);
    println!("iterations={iterations} size={size} elapsed_ms={} throughput_mib_s={:.2} accumulator={acc}", elapsed.as_millis(), mib_s);
}
