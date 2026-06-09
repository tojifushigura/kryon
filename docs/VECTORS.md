# Kryon v0.3 Known Answer Tests

These vectors are for the canonical Kryon profile shipped in v0.3. The canonical profile is intentionally compatible with v0.2, so these values match v0.2. Reduced-round outputs are non-canonical and are not listed here.

## Kryon-256

| Message | Hex digest |
|---|---|
| empty string | `d9fc42dac38f7097467399af7a8b1cc0210939b968bd074ea17a147b8e3a1516` |
| `abc` | `17efe42ac4aecf5c5ba152cade5d2996f82511e0c9fdf1059ddf65be4beb2c59` |
| `The quick brown fox jumps over the lazy dog` | `d959d4712ba1edbf198f93de5040931d28b5ee2f823cf3f7ad6d4ea45af258da` |
| `The quick brown fox jumps over the lazy dog.` | `09f5b2a86e2e0876a95dd9fa88c14e731ae7858c869756ea85a574432fbad953` |
| bytes 0..255 | `cbfc83d21c2c727cea9c2fa7946ef729a58e707d45f2d9b71fe268a6adc61363` |

## Kryon-384

| Message | Hex digest |
|---|---|
| empty string | `ce22c2f741871b79ad60664f786b3e314cab314d5c9e8d7b63c725ba7596e681f9de5dccbd19d8243c82e57a22ab25ae` |
| `abc` | `06f61fabf777a7653a46c921eb46bc9a52c876f0cb7afd60495118b5b81f73830b0cab537db8aea4bade55d717f71370` |
| `The quick brown fox jumps over the lazy dog` | `6afd3754f279989a9b76b1bbf093bb2dc36557e4371089a7c02dacd9aac1ff918c8bff4846933e02d908c6ebcdba4e1e` |
| `The quick brown fox jumps over the lazy dog.` | `5264377a4363950ed2806aa52905b9e4472135618b028edbf10318b572aa708d9754c210f4c4384a8ba579466d58bcd2` |
| bytes 0..255 | `8a4375ebecba66420e34c64a4d87c9f386a2bc34722cc1263cebcb116849dd4c1146f7b50b251efed6495ee1726bfd61` |

## Kryon-512

| Message | Hex digest |
|---|---|
| empty string | `9ded230a30a6ae0dc975d6efd68418c2cea514293d06fbec6d0329ab8bad8672c76bb427d96aab9b662921fd14c0693c224fcefddf62b5ba9dc60fccb9ebb5c0` |
| `abc` | `aa27831f187a0804f3045ca10a1a352fe0cea4c487f9eecaed328968447d02ec89e4296f50bb1e268bd8960aedbe54a5fc1a7226302988a1129cf9385e26ced3` |
| `The quick brown fox jumps over the lazy dog` | `b1be6a996ece11e99afcec264d33186b4b1521c836f0e8a7fdaa2a2be8231e426f6f048739ef9a29e822daaafcf254474f79ee76b40492699426a4187140a9bf` |
| `The quick brown fox jumps over the lazy dog.` | `fb241928fe42ad20b5bed145196ce1447bdd181f6372329ce16bd10c83964ad40069aa6fb2ef99f7421588dcc516818ebc47954d08ddb34318dd02ceea051988` |
| bytes 0..255 | `2ad2a37b1e31a268ce58f19229cbacb3a7b71f84b0ff86d574c60ec3a74b064204849ba6d840a74f0e6caab30090ccb8f6b9f75c202e16aa8fc565d44d383ca5` |
