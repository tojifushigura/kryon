use kryon_native::hexdigest;

fn main() {
    for msg in ["", "abc", "The quick brown fox jumps over the lazy dog"] {
        let digest = hexdigest(msg.as_bytes(), 384).expect("valid digest");
        println!("{msg:?} {digest}");
    }
}
