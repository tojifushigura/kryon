use std::env;
use std::io::{self, Read};

use kryon_native::hexdigest;

fn json_escape(value: &str) -> String {
    let mut out = String::new();
    for ch in value.chars() {
        match ch {
            '\\' => out.push_str("\\\\"),
            '"' => out.push_str("\\\""),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c.is_control() => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out
}

fn hex_decode(s: &str) -> Result<Vec<u8>, String> {
    if s.len() % 2 != 0 {
        return Err("hex length must be even".to_string());
    }
    let mut out = Vec::with_capacity(s.len() / 2);
    let bytes = s.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        let hi = (bytes[i] as char).to_digit(16).ok_or_else(|| "invalid hex".to_string())?;
        let lo = (bytes[i + 1] as char).to_digit(16).ok_or_else(|| "invalid hex".to_string())?;
        out.push(((hi << 4) | lo) as u8);
        i += 2;
    }
    Ok(out)
}

fn hex_encode_prefix(data: &[u8], max_bytes: usize) -> String {
    let mut out = String::new();
    for byte in data.iter().take(max_bytes) {
        out.push_str(&format!("{:02x}", byte));
    }
    out
}

fn main() {
    let mut digest_bits: u16 = 384;
    let args: Vec<String> = env::args().collect();
    let mut i = 1;
    while i < args.len() {
        if args[i] == "--digest-bits" && i + 1 < args.len() {
            digest_bits = args[i + 1].parse().expect("invalid --digest-bits");
            i += 2;
        } else {
            i += 1;
        }
    }

    let mut input = String::new();
    io::stdin().read_to_string(&mut input).expect("read stdin");
    let mut rows: Vec<String> = Vec::new();
    for line in input.lines() {
        if line.trim().is_empty() {
            continue;
        }
        let parts: Vec<&str> = line.splitn(3, '\t').collect();
        if parts.len() != 3 {
            panic!("expected name<TAB>category<TAB>hex");
        }
        let name = parts[0];
        let category = parts[1];
        let data = hex_decode(parts[2]).expect("decode corpus hex");
        let digest = hexdigest(&data, digest_bits).expect("digest");
        rows.push(format!(
            "{{\"name\":\"{}\",\"category\":\"{}\",\"length\":{},\"preview_hex\":\"{}\",\"kryon\":\"{}\"}}",
            json_escape(name),
            json_escape(category),
            data.len(),
            hex_encode_prefix(&data, 32),
            digest
        ));
    }
    println!("[{}]", rows.join(","));
}
