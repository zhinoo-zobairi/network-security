# Warm-Up: Packet Encapsulation & De-Encapsulation

This section is the **overview so far** — before we jump into IPSec itself.  
We start with a plain packet (no security, everything visible) and then show where different security protocols (MACsec, IPSec, TLS, QUIC) intervene.

## Baseline: No Security

A network packet without security looks like this. **Each header describes and controls the payload immediately to its right.**

````
+-----------------------------------------------------------+
| Ethernet Header | IP Header | TCP/UDP Header | App Data   |
+-----------------------------------------------------------+
````

- **Ethernet Header (L2):** Source/destination MAC, type, etc.  
- **IP Header (L3):** Source/destination IP, TTL, protocol, etc.  
- **TCP/UDP Header (L4):** Ports, sequence numbers, flags, etc.  
- **App Data (L7):** Application content (HTTP request, email, etc.).  

**Everything is visible on the wire.**

## Encapsulation (Sending Side)

1. **Application Layer (L7)**  
   - **Baseline:** Creates the data (e.g., `GET /index.html HTTP/1.1 …`).  
   - **With TLS/QUIC:**  
     - TLS encrypts just the application data before passing it to TCP.  
     - QUIC integrates TLS 1.3 and encrypts application data at this stage too.  

   Result:  
   - No security → `[App Data]`  
   - With TLS/QUIC → `[Encrypted App Data]`

2. **Transport Layer (L4 – TCP/UDP)**  
   - **Baseline:** Adds TCP/UDP header (ports, seq numbers, flags).  
     - Result: `[TCP/UDP Header | App Data]`  
   - **With TLS:** TCP header stays in cleartext, but payload is already TLS-encrypted.  
     - Result: `[TCP Header | Encrypted App Data]`  
   - **With QUIC:** UDP header visible, QUIC payload (including its transport metadata + app data) encrypted.  
     - Result: `[UDP Header | Encrypted QUIC Payload]`  

3. **Network Layer (L3 – IP)**  
   - **Baseline:** Adds IP header (src/dst IPs, TTL, protocol).  
     - Result: `[IP Header | TCP/UDP Header | App Data]`  
   - **With IPSec Transport Mode:**  
     - TCP/UDP header + App Data are encrypted (ESP payload).  
     - IP header remains visible.  
     - Result: `[IP Header | Encrypted (TCP/UDP Header + App Data)]`  
   - **With IPSec Tunnel Mode:**  
     - Entire original IP packet encrypted.  
     - New IP header added for routing.  
     - Result: `[New IP Header | Encrypted (Orig IP Header + TCP/UDP Header + App Data)]`

4. **Data Link Layer (L2 – Ethernet, Wi-Fi, …)**  
   - **Baseline:** Adds Ethernet (or Wi-Fi) header + trailer (MAC addresses, type, checksum).  
     - Result: `[Ethernet Header | IP Packet | Ethernet Trailer]`  
   - **With MACsec:**  
     - Encrypts the Ethernet payload (which is the entire IP packet).  
     - Ethernet header stays visible for switching.  
     - Result: `[Ethernet Header | Encrypted (IP Packet) | MACsec Trailer]`


5. **Physical Layer (L1)**  
   - **Baseline:** Converts frame to signals (electrical, optical, or radio).  
   - **Security:** At this level, no protocol encrypts the raw signal itself. Security always comes from higher layers (MACsec, IPSec, TLS, QUIC).  

## De-Encapsulation (Receiving Side)

The reverse happens:

1. **Physical Layer (L1)**  
   - Signals → bits.  
   - No security here.

2. **Data Link Layer (L2)**  
   - Removes Ethernet header/trailer.  
   - If MACsec is active → decrypts payload, verifies integrity.  
   - Exposes IP packet.

3. **Network Layer (L3 – IP)**  
   - Removes IP header.  
   - If IPSec is active → decrypts ESP payload (transport mode) or entire inner packet (tunnel mode).  
   - Exposes TCP/UDP segment.

4. **Transport Layer (L4 – TCP/UDP)**  
   - Removes transport header.  
   - If TLS is active → passes encrypted payload upward for TLS decryption.  
   - If QUIC is active → decrypts QUIC payload itself (since QUIC integrates crypto at L4).  
   - Exposes application data (or decrypted QUIC/TLS content).

5. **Application Layer (L7)**  
   - Processes the original request (e.g., HTTP).  
   - With TLS/QUIC → now sees cleartext after decryption.  

# IPSec 

- Before IPSec:
  - Security was added at the **application layer** (TLS, HTTPS, SMTPS, FTPS, …).
  - Problem: each application had to be modified to support encryption.

- With IPSec:
  - Security added at the **network layer (L3)** → transparent to applications.
  - Applications continue unchanged; OS handles security.

- IPSec provides:
  - **Encryption** – confidentiality of payload.
  - **Data integrity** – detect modification in transit.
  - **Authentication of sender** – data origin authentication.
  - **Replay protection** – prevents reuse of old packets.
  - **Negotiable algorithms** – peers agree dynamically.
  - **Key exchange** – done via **IKE (Internet Key Exchange)**.

## Characteristics

- Originally **mandatory for IPv6** (= any IPv6 stack had to come with IPSec code in the kernel); Over time, practice showed: **Not every use case needed IPSec**; because the web moved to TLS and VPNs had other technologies, today optional for both IPv4 and IPv6.
- Supports **compression before encryption** (since encrypted data doesn’t compress well).
- Requires **kernel/OS support** (unlike TLS, which runs in user space libraries).

## IPSec Protocols
**A protocol is a set of rules + a format for communication between peers.**

Every IP packet has a field in its header called *Protocol* (IPv4) or **Next Header** (IPv6).

This field says: “*What’s inside me?*”

Examples:

- 6 → payload is TCP.

- 17 → payload is UDP.

- 1 → payload is ICMP.

- 50 → payload is ESP.

- 51 → payload is AH.

So the IP header doesn’t care what the payload is. It just says: 
>“The next chunk is of type X.”

When IPSec is used, **instead of the IP payload being directly TCP/UDP**, it can be an **IPSec header**. So IPSec “**sits in between**” IP and TCP/UDP:
It doesn’t replace TCP or UDP.
It wraps them, so TCP/UDP are still there, just deeper inside.
### 1. AH – Authentication Header
````
IP Header (Protocol=51)
    └── AH Header
           └── TCP Header
                 └── Application Data
````

- **RFC 2402 (1998)** → replaced by **RFC 4302** (2005) and **RFC 4305**.  
- **Protocol number: 51.**  
- Services:  
  - Integrity protection.  
  - Authentication of sender.  
  - Replay protection.  
  - ⚠️ No encryption.  
- Works by calculating a **MAC** (Message Authentication Code) over:
  - Entire IP packet (IP header + payload + AH header).  
  - Excludes fields that change during transit (e.g., TTL). These are set to zero during MAC calculation.  
- **Fragmentation**: must reassemble fragments before verification, since MAC is over the whole packet.

#### AH Header Format
![alt text](images/AH-Header.png)
- **Next Header (8 bits):** Identifies protocol after AH (similar to Protocol field in IP header).  
- **Payload Length (8 bits):** Length of AH in 32-bit words.  
- **SPI – Security Parameter Index (32 bits):** Identifies the security association and cryptographic algorithms to use.  
- **Sequence Number (32 bits):** Prevents replay attacks.  
- **Authentication Data (variable):** Integrity check value (MAC).

### 2. ESP – Encapsulating Security Payload
Now, the IP header says: “*My payload is ESP.*”
````
[ IP Header (Protocol=50) | ESP Header | Encrypted Payload | ESP Trailer | ESP Auth ]
````
````
IP Header (Protocol=50)
    └── ESP Header
           └── [TCP Header + Application Data] (encrypted)

````

Inside ESP, you’ll eventually find the TCP/UDP header + app data (encrypted if ESP is in encryption mode).
- **RFC 2406 (1998)** → replaced by **RFC 4303** (2005).  
- **Protocol number: 50.**  
- Services:  
  - Encryption (confidentiality).  
  - Integrity protection.  
  - Authentication of sender.  
  - Replay protection.  
- **MAC calculation** only covers:  
  - ESP header.  
  - Payload (data).  
  - ESP trailer.  
  - ❌ The IP header is not covered (unlike AH).  

#### ESP in Transport Mode
![alt text](images/ESP.png)


- **Before ESP**:  
````
IPv4 | Orig IP hdr | (any options) | TCP | Data |
````

- **After ESP**:  
````
IPv4 | Orig IP hdr | ESP hdr | TCP | Data | ESP trlr | ESP ICV |
````

- Encryption covers `[TCP | Data | ESP trailer]`.  
- Integrity protection covers `[ESP hdr | TCP | Data | ESP trailer | ICV]`.  

---

## IPSec Modes
![alt text](images/Transport-Tunnel-Mode-Protocols.png)
### Transport Mode
- Protects only the **IP payload** (TCP/UDP header + application data).
- Original IP header remains visible for routing.
- Used for **end-to-end host communication**.
- ESP → encrypts payload.  
- AH → authenticates payload + selected IP header fields.

### Tunnel Mode
- Protects the **entire original IP packet** (IP header + TCP/UDP + application).
- Adds a **new IP header** for routing between gateways.
- Used for **gateway-to-gateway VPNs** (site-to-site tunnels).
- Hides internal addressing from outside.

## IPSec Use Cases

1. **Full traffic encryption between two hosts**
 - IPSec can secure all IP traffic between endpoints.  
 - Main use today: building **secure tunnels** → Virtual Private Networks (VPNs).  

2. **Protection of routing information**
 - OSPF routing updates.  
 - ICMPv6 messages:  
   - **Router Advertisement** (new router announces itself).  
   - **Neighbor Advertisement** (router advertises itself to other routing domains).  

![alt text](images/TunnelModeFormat.png)

### Tunnel Mode Format

- **New IP header**: routes between gateways.  
- **ESP header/trailer/auth**: added by IPSec.  
- **Orig IP header + payload**: fully encrypted.  

### IPSec VPN Example
![alt text](images/IPSecVPN.png)

- End hosts send normal IP traffic into the LAN.  
- Networking device with IPSec (firewall/router) encapsulates traffic.  
- Over the public Internet: packets travel inside a **virtual tunnel**, protected by IPSec.  
- Remote gateway decrypts and forwards traffic to its local LAN.  

## Summary

- IPSec secures traffic at **Layer 3**, invisible to applications.  
- Provides **encryption, integrity, authentication, replay protection**.  
- Two main protocols:  
- **AH** → Integrity + Authentication, no encryption.  
- **ESP** → Encryption + Integrity + Authentication.  
- Two modes:  
- **Transport mode** → protects only payload.  
- **Tunnel mode** → protects entire packet.  
- Common use cases:  
- VPNs (site-to-site or host-to-host).  
- Securing routing protocols.
