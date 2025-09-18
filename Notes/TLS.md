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

## 1. History
- **SSL (Secure Sockets Layer)**: developed by Netscape (1994).  
- **SSL 3.0** became the foundation of TLS.  
- **TLS versions:**
  - TLS 1.0 – RFC 2246 (1999) → obsolete  
  - TLS 1.1 – RFC 4346 (2006) → obsolete  
  - TLS 1.2 – RFC 5246 (2008) → still widely used  
  - TLS 1.3 – RFC 8446 (2018) → modern standard, simpler, more secure  

## 2. Supported TCP-Based Services (with reserved ports)
TLS is not limited to HTTP — it can secure many TCP-based applications.

| Protocol | Port | Secure Version | Purpose |
|----------|------|----------------|---------|
| **HTTP** | 443  | **HTTPS**      | Browsing the web securely |
| **Telnet** | 992 | **Telnets**   | Remote terminal login (legacy, insecure without TLS) |
| **FTP (control)** | 990 | **FTPS** | Secure file transfer control channel |
| **FTP (data)** | 989 | **FTPS-data** | Secure file transfer data channel |
| **SMTP** | 465 | **SMTPS** | Secure mail submission (sending email from client to server) |
| **POP3** | 995 | **POP3S** | Secure mail retrieval (client fetching mail from server) |

## 3. TLS Functionality
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