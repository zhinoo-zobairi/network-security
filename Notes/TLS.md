# Why all these types of security?!

## 1. Layered View (OSI perspective)

- **Layer 1: Physical (Bits as signals)**
- The Physical Layer (OSI L1) doesn’t care what the bits mean.
- Its only job: *take 0s and 1s → turn them into physical signals → send them across a medium → recover them as 0s and 1s at the other end.*
>Different media use different kinds of physics:
  >- Copper (Ethernet cables, old phone lines), medium is copper wire and signal = voltage changes (electrical pulses; **Bit 0 = low voltage, Bit 1 = high voltage**).
  >
  > - Fiber Optics (glass fiber), medium is glass fiber and signal = light pulses (laser/LED): **Bit 0 = no light pulse, Bit 1 = light pulse**
  > - Wireless (Wi-Fi, cellular, Bluetooth), medium is air and signal = radio waves (electromagnetic radiation), **bits are mapped onto changes in wave frequency/phase/amplitude.**
  >
  > They are all implementations of the Physical Layer, the very bottom of the stack.

- Laptop’s antenna, inside your Wi-Fi card:
  - modulates bits (0/1) into changes of the electromagnetic waves at 2.4 GHz or 5 GHz. Those modulated waves carry 802.11(document/version codes inside IEEE) frames (MAC header + payload + CRC).
	- Example:
	- Bit 0 → wave at 2.400000000 GHz with phase A.
	- Bit 1 → wave at 2.400000000 GHz with phase B.
- Router’s antenna, the receiver: 
  - does the reverse: electromagnetic waves → Antenna converts waves into → weak analog electrical signal → Wi-Fi radio chip samples signal (demodulates modulation) → recovers the digital bits → 802.11 frame reconstructed → CRC/MIC verified → IP packet → TCP segment → Application data
- Security risk: anyone nearby can **sniff signals** (radio interception, wire tapping), because radio is a shared medium. Any **NIC**(Wi-Fi card = Hardware that connects a computer to a network, has a MAC address and can be on **Managed mode** (normal, connects to an AP) or **Monitor mode**) set to monitor mode can capture frames on the channel, even if not connected to the **AP**(Access Point).

- **Layer 2: Data Link (Frames, MAC)**
  - Organizes raw bits from Physical into frames with meaning. Adds MAC addresses, local delivery, error detection.
  - It’s called Data Link Layer because it links two directly connected nodes (e.g., laptop ↔ router, router ↔ ISP).
That means:
  - Groups bits into **frames** with:
    - Destination MAC (hardware address)
    - Source MAC
    - Payload (higher-layer data)
    - Integrity check (CRC/MIC)
  - Ensures **single** hop delivery: Local delivery to your immediate neighbor (your router/AP)
  - Security tool: **WPA2/WPA3** (encrypts frames, adds MIC to detect tampering).

- **Layer 3: Network (Packets, IP)**
  - Payload of frame from Data Link is an **IP packet**:
    - Source IP (who sends)
    - Destination IP (who receives)
    - Payload (transport data)
  - Global addressing & routing (across the Internet).
  - Security tool: **IPsec** (encrypts/authenticates IP packets).

- **Layer 4: Transport (TCP/UDP, Ports)**
  - Payload of IP packet is a **TCP segment** (or UDP datagram):
    - Ports identify which application (e.g., 80 = HTTP, 443 = HTTPS).
    - TCP ensures order & retransmits lost packets.
  - Security tool: **TLS/DTLS** (encrypts the transport connection, authenticates servers with certificates).

- **Layer 7: Application (Protocols, Content)**
  - Payload of TCP segment is **application data**:
    - HTTP request, email (SMTP), DNS query, etc.
  - Security tools:
    - **TLS** → secures application traffic in transit (HTTPS, SMTPS, IMAPS).
    - **PGP/S/MIME** → encrypts/signs the *content itself* (end-to-end, independent of transport).
    - **DNSSEC** → protects DNS queries/answers.

- TLS sits **on top of TCP** (or UDP for DTLS).
- From TCP’s view, TLS is “just another application protocol.”
- Applications (HTTP, SMTP, IMAP, etc.) send data **inside TLS records**.
#### Without TLS (plaintext):
````
TCP Payload:
GET /login HTTP/1.1
Host: bank.com
Cookie: sessionid=abc123
````
#### With TLS (encrypted):
````
TCP Payload:
[TLS ciphertext blob]
````
👉 The HTTP request is now hidden inside the TLS record.

#### What TLS Does *Not* Protect
- **TCP/IP headers**: source/dest IP, ports, sequence numbers.  
- **Metadata**: packet size, timing, traffic patterns.  

A sniffer still sees:
````
Src IP: 192.168.1.5
Dst IP: 141.89.220.50
Dst Port: 443
Packet length: 1514 bytes
Time: 12:30:01
````
…but cannot see the actual HTTP request or cookie.

## Example: Logging into a Website Without Security

1. **Physical:** Raw Wi-Fi signals can be sniffed by anyone nearby.
2. **Link:** Frame shows MAC addresses, integrity check.
3. **Network:** Packet shows your IP → bank’s IP.
4. **Transport:** TCP segment shows port 80 (HTTP).
5. **Application:** HTTP request in plaintext:
````
GET /login HTTP/1.1
Host: bank.com
Cookie: sessionid=abc123
````
👉 Attacker sees your **login cookie**(= A small piece of data stored in your browser by a website (key-value pair), used to maintain state across multiple HTTP requests (since HTTP is stateless)). That sessionid is essentially your ticket proving you’re logged in. If an attacker steals it (via sniffing, XSS, etc.), they can impersonate you without knowing your password → session hijacking.

---

## Example: Same Login With WPA3 + TLS

1. **Physical/Link:** Wi-Fi frames encrypted with WPA3 → payload is gibberish.
2. **Network:** IP addresses still visible (you must know where to deliver), but payload is protected.
3. **Transport:** TCP session inside TLS → attacker cannot read/alter data.
4. **Application:** HTTP becomes HTTPS → cookies, passwords, and messages are encrypted end-to-end.

👉 Attacker sees only **encrypted blobs**, not your login data.
 
## Security by Layer 
| Layer        | Unit        | Addressing    | Risk                 | Security Tool |
|--------------|-------------|---------------|----------------------|---------------|
| Physical     | Bits/waves  | None          | Radio interception   | — |
| Data Link    | Frame       | MAC address   | Local sniffing/tamper| WPA2/WPA3 |
| Network      | Packet      | IP address    | Traffic analysis, spoofing | IPsec |
| Transport    | Segment     | Ports         | MITM, injection      | TLS/DTLS |
| Application  | Message     | Protocol data | Content leakage      | PGP, S/MIME, DNSSEC |

✅ **One sentence takeaway:**  
Networking is built in layers: each layer wraps the one above, each layer has its own risks, and each has its own security mechanisms (WPA3 → IPsec → TLS → PGP) and **NOW it is time for TLS:**
# Transport Layer Security (TLS) 🔒

## History
- **SSL (Secure Sockets Layer)**: developed by Netscape (1994).  
- **SSL 3.0** became the foundation of TLS.  
- **TLS versions:**
  - TLS 1.0 – RFC 2246 (1999) → obsolete  
  - TLS 1.1 – RFC 4346 (2006) → obsolete  
  - TLS 1.2 – RFC 5246 (2008) → still widely used  
  - TLS 1.3 – RFC 8446 (2018) → modern standard, simpler, more secure  

## Supported TCP-Based Services (with reserved ports)
TLS is not limited to HTTP — it can secure many TCP-based applications.

| Protocol | Port | Secure Version | Purpose |
|----------|------|----------------|---------|
| **HTTP** | 443  | **HTTPS**      | Browsing the web securely |
| **Telnet** | 992 | **Telnets**   | Remote terminal login (legacy, insecure without TLS) |
| **FTP (control)** | 990 | **FTPS** | Secure file transfer control channel |
| **FTP (data)** | 989 | **FTPS-data** | Secure file transfer data channel |
| **SMTP** | 465 | **SMTPS** | Secure mail submission (sending email from client to server) |
| **POP3** | 995 | **POP3S** | Secure mail retrieval (client fetching mail from server) |

## TLS Functionality
- **Authentication**: server identity (and optionally client) proven via certificates.  
- **Confidentiality**: all communication is encrypted.  
- **Integrity**: Message Authentication Code (MAC) detects tampering.  
- **OSI view**: takes over responsibilities of Session + Presentation layers.  

✅ **In short:** TLS secures TCP-based applications with authentication, encryption, and integrity, and uses well-known ports for secure protocol variants.

>Let's take a look at the previous session: TLS vs PGP:
>
>**TLS** sits between the **transport and application layers**. It encrypts the connection/session, so that any data passing over TCP (HTTP, SMTP, IMAP, etc.) is protected while in transit. Once the session ends, the protection is gone.
>
> **PGP** lives **fully at the application layer**. It encrypts and signs the message content itself (email text, attachments, files). Even if the message is copied, stored, or forwarded through many servers, it stays protected until the intended recipient decrypts it.
>
>👉 **In short: TLS = channel security, PGP = content security.**

## TLS 
##	TLS has sub-protocols:
*Terminology stuck from history. What the slides call “SSL-Handshake Protocol” is today’s TLS Handshake Protocol.*
- SSL-Handshake Protocol is the “setup phase.”: Austausch der notwendigen Informationen für die dezentrale Berechnung der Schlüssel (MAC- und Sitzungsschlüssel) und Aushandeln der kryptographischen Verfahren.
- When your browser starts talking to a server, it says:
> *“I know how to do encryption with AES, or ChaCha20, or others. Which one do you prefer?”*

  That list is called **cipher suites**. The server picks one.
- Both sides (browser + server) each send a 32-byte random number at the start. They **mix** these into the key calculation. This makes sure **every session is unique**, even if you connect to the same server again.

- **Master secret** is the **big shared secret** that both sides calculate during the handshake. They never send it across the Internet. They both create it independently, using the exchanged random numbers and some math (Diffie-Hellman or RSA). 

- **From master secret**, smaller keys are made → the ones used to encrypt your data → **SSL-ChangeCipherSpec Protocol** = After handshake math is done, each side sends a tiny signal (“from now on, encrypt with the session keys”).

**So**,
**Key derivation (general):**

`(Key-agreement → pre_master_secret)` → `PRF(pre_master_secret, client_random ∥ server_random)` → `master_secret` → `PRF(master_secret, "key expansion", server_random ∥ client_random)` → `key_block` → **split** → `client_write_key | server_write_key | client_write_MAC_key | server_write_MAC_key | IVs`

- *Notes:* “Key-agreement” can be RSA-encrypted premaster, Diffie-Hellman, ECDHE, etc. The PRF (pseudo-random function) mixes secrets + randoms to produce the `master_secret` and expands it into the `key_block`.  
- *Result:* the Record layer uses the `*_write_key` for confidentiality and the `*_MAC_key` for integrity (and IVs/nonces for cipher operation).

### Example
In Wireshark, when you open Booking.com, you’ll see lines like:
````
TLSv1.3 Handshake Protocol: Client Hello
   Cipher Suites: TLS_AES_128_GCM_SHA256, TLS_CHACHA20_POLY1305_SHA256, ...
   Random: (32 bytes)
---
TLSv1.3 Handshake Protocol: Server Hello
   Cipher Suite: TLS_AES_128_GCM_SHA256
   Random: (32 bytes)
   Certificate: *.booking.com
````
- ClientHello = browser’s proposal (ciphers, random).
- ServerHello = server’s answer (chosen cipher, its random, certificate).

In Wireshark when the handshake math is done → You’ll see a one-liner: `Change Cipher Spec`
Even though attackers can see the handshake, they **cannot** calculate the master secret, because the math (Diffie-Hellman) makes it impossible without the private key.

- At the end, both sides send a **Finished message**. This includes a **checksum (MAC) of all handshake steps**. If an attacker had changed anything, the checksums wouldn’t match → connection is aborted.
>The whole point of the handshake is to **compute keys**:
>- The outcome isn’t just the master secret. This “master secret” is the seed. From that, TLS derives:
>- **MAC key** (for integrity: HMAC-SHA256 checks on each record).
>- **Encryption key** (for confidentiality: AES, ChaCha).
>- **Session keys** for both directions (client→server, server→client).
> - So: Handshake = not just agreeing on algorithms, but actually **producing the working keys for Record Protocol**.
>
>👉 Bridge: the handshake’s job is to **prepare Record Protocol**. Without MAC + session keys, Record Protocol can’t encrypt or check integrity.

- **SSL-Record Protocol**: “Do encryption/decryption (and maybe compression).” = Takes the HTTP request, slices it into records, encrypts with AES/ChaCha, adds MAC (integrity check).
- **SSL-ApplicationData Protocol**: “Forward encrypted data to application.” = Your browser sees the decrypted result and renders Booking.com, but on the wire, it’s all gibberish. This is where the **“real business”** (HTML, JS, API calls) happens.

- **Alert Protocol** will fire, if something goes wrong, TLS sends a special Alert message before closing:
- Example: certificate invalid → browser shows “Your connection is not private.”
- Example: keys don’t match → TLS alert “handshake_failure.”

In Wireshark, you’d literally see a line:
```
Alert (Level: Fatal, Description: Handshake Failure)
```

### Let's now zoom into Session State and Connection State parameters.

Think about what TLS has to **“remember”** internally after the handshake:
- Some values belong to the whole session (they can be reused if you reconnect) = **SESSION**
- Other values belong to a single TCP connection (they are fresh each time) = **CONNECTION**


## Session State (TLS 1.2 style)
Values stored after handshake (can be reused in resumptions):
- **session identifier** → chosen by server, marks a resumable session.  
- **peer certificate** → e.g., `*.booking.com` X.509 certificate.  
- **compression method** → typically `null` (compression mostly disabled).  
- **cipher spec** → chosen algorithm bundle, e.g., `TLS_AES_128_GCM_SHA256`, it’s the outcome of the negotiation process that started with the cipher suite proposals.
- **master secret** → 48-byte shared root secret derived from the handshake.  
- **is resumable** → whether session can be resumed for future connections.

💡 *Think of session state as the “contract” between client and server — it records what they agreed on and can be reused to save time later.*


## Connection State (Security Parameters)
Each TCP connection under that session uses its own state:
- **connection end** → am I client or server?  
- **master secret** → imported from session.  
- **client_random / server_random** → 32-byte values exchanged in Hello messages.  
- **PRF algorithm** → pseudo-random function for key expansion (often SHA-256).  
- **bulk encryption algorithm** → e.g., AES-GCM, ChaCha20.  
- **MAC algorithm** → e.g., HMAC-SHA256, for integrity checks.  
- **compression algorithm** → typically none.  

💡 *The connection state is the **working toolbox**. From the master secret + randoms, the PRF expands into actual working keys*:
- `client_write_key`, `server_write_key` (for encryption).  
- `client_write_MAC_key`, `server_write_MAC_key` (for integrity).  
- Initialization vectors (IV is a block of random or unique bits that is added to encryption at the start of a message. It makes sure that if you encrypt the same plaintext twice with the same key, the ciphertext looks different.)

The old-style notation (TLS 1.2) with all pieces written out:
![alt text](images/cipher-suite-name.png)
#### TLS 1.2 Cipher Suites' moving parts:

A cipher suite in TLS ≤1.2 is a combination of multiple crypto building blocks:

**General form:**  
`TLS_<KeyExchange>_<Authentication>_WITH_<Encryption>_<MAC>`

##### 1. Key Exchange
- RSA (no forward secrecy)  
- DH / ECDHE (Diffie–Hellman, elliptic curve variant → forward secrecy)  

##### 2. Authentication / Signature
- RSA  
- ECDSA  
- DSA  

##### 3. Bulk Encryption (Cipher)
- AES_128_CBC  
- AES_256_GCM  
- 3DES (weak, legacy)  
- RC4 (broken, legacy)  

##### 4. MAC (Hash for Integrity)
- SHA1 (weak)  
- SHA256  
- SHA384  
- MD5 (broken)  

##### 5. Elliptic Curve (if ECDHE/ECDSA)
- P-256  
- P-384  
- P-521  

💡 *Why it mattered:*  
Too many options meant servers often supported insecure combinations (RC4, 3DES, MD5, SHA1). Attackers could downgrade connections to these weak suites.  
TLS 1.3 removed this flexibility → only strong AEAD ciphers + modern hashes:
## TLS 1.3 simplifies notation.
- Only **AEAD algorithms** allowed (Authenticated Encryption with Associated Data, RFC 8446).  
- Format: `TLS_AEAD_HASH`  
- Example: `TLS_AES_128_GCM_SHA256`  
  - AEAD = AES-128-GCM (encryption + integrity combined).  
  - HASH = SHA256 (for handshake key derivation).  

💡 *Real-world:* If you visit `https://booking.com` today and capture traffic in Wireshark, you’ll see:
````
Cipher Suite: TLS_AES_128_GCM_SHA256
````
This exact choice dictates the keys in your connection state.

#### Jede Handshake-Nachricht ist wie folgt aufgebaut:
`Type (1 Byte) | Length (3 Bytes) | Content (≥0 Bytes)`
- Type: identifies the message (e.g., ClientHello = 1, ServerHello = 2, etc.).
-	Length: how long the message is.
-	Content: the actual fields (e.g., randoms, cipher list, cert, etc.).

## TLS Handshake detailed phases

### Phase 1: Client → Server (ClientHello)
The **ClientHello** message contains:
- **Maximum version number** the client supports (e.g., TLS 1.2, TLS 1.3).  
- **NonceC**: 32-bit timestamp + 28-byte random value `Rc`.  
  - Used later in key derivation (prevents replay attacks, ensures freshness).  
- **Session Identifier**:  
  - `0` → new session (fresh handshake).  
  - nonzero → request to resume a previous session.  
- **Cipher suite proposals** (list of supported algorithms):  
  - Hashes (MD5, SHA-1, SHA-256, …).  
  - Signature algorithms (RSA, DSA, ECDSA).  
  - Symmetric ciphers (AES, 3DES, RC4).  
  - Key exchange methods (RSA, DH, ECDH).  
- **Compression methods**: usually just “null.”  

💡 At this point, the client is saying:  
> “Here’s what I can do, here’s a random number for entropy, and here’s whether I want a new session or to resume an old one.”

---

### Phase 2: Server → Client (ServerHello and related)
The **ServerHello** message contains:
- **Chosen TLS version**: highest version both sides support.  
- **NonceS**: 32-bit timestamp + 28-byte random value `Rs`.  
- **Cipher suite selection**: chosen from client’s proposal.  
  - Example: `TLS_RSA_WITH_AES_256_CBC_SHA256`  
    - Key Exchange = RSA  
    - Bulk Cipher = AES-256-CBC  
    - MAC Algorithm = SHA256  
- **Compression method**: usually none.  

### Optional messages in Phase 2:
1. **Variant 1: Certificate** → Server has a certificate with long-term keys. Example: RSA certificate. The public key inside the certificate is already enough for the client to send the pre-master secret (encrypted with RSA). Result: no need for a separate ServerKeyExchange. Only Certificate is sent ✅ 
2. **Variant 2: ServerKeyExchange** → Server uses ephemeral keys (forward secrecy). Example: ECDHE_RSA (Ephemeral Diffie-Hellman with RSA signature). The certificate proves the server’s identity (RSA signature). But the actual key exchange is done with ephemeral DH parameters (new, random keys per session) → The server must send those DH parameters in ServerKeyExchange. Client uses them + its own DH parameters to derive the pre-master secret.  
3. **CertificateRequest** → if server requires client authentication. Includes accepted CA list.  
4. **ServerHelloDone** → signals end of Phase 2.  

### Client’s checks after Phase 2:
- Validate the server’s certificate (issuer trusted? valid date? hostname match?).  
- Verify that the chosen cipher suite is in the client’s proposal list.  

💡 Now the server has responded:  
> “We’ll use TLS 1.2, here’s my random number, here’s my certificate, and here’s the cipher suite I chose. Now it’s your turn to prove you can continue.”

![alt text](images/client_validates_server_certificate.png)

When the server sends its certificate in the `Certificate` message,  
the client (browser) must check not only:
- Is the certificate signed by a trusted CA?  
- Is it within its validity period?  
- Does the hostname match?  

…but also: **Has this certificate been revoked?**

### Certificate Issuance & Publishing
- **Subscriber (server owner)** → requests a certificate (CSR = Certificate Signing Request).  
- **RA (Registration Authority)** → validate the identity of the subscriber (the one requesting the cert). Acts as a **front desk** for the CA.
- **CA (Certification Authority)** → The entity that actually issues and cryptographically signs the certificate. It’s the CA’s private key that creates the signature you later verify in your browser. The CA’s private key must be extremely well-protected (often in an HSM — hardware security module).
	•	It’s safer if the CA only signs certificates and never directly deals with customers.
- Certificate is published and installed on the **web server**.

### Client-side validation steps
1. **Request certificate** from the web server (part of TLS handshake).  
2. **Verify signature**: check if the server’s certificate is signed by a CA in the **client’s trust store**.  
3. **Check for revocation**: ensure the certificate has NOT been revoked.  

### How revocation is checked
- **CRL (Certificate Revocation List)**:  
  - CA periodically publishes a signed list of revoked certificates.  
  - Client downloads and checks whether the server’s cert is listed.  
- **OCSP (Online Certificate Status Protocol)**:  
  - Client queries an OCSP responder server in real-time.  
  - Gets back a signed “good” or “revoked” response.  
- As of 2024 → CRLs are still commonly used, OCSP more modern but adds latency.

💡 *Bridge to TLS handshake:*    
- If validation fails → client sends an **Alert protocol** message and closes the connection.  
- Only if validation succeeds does the client continue to Phase 3 (ClientKeyExchange etc.).