## Protocol Format Recap

This demo used a **binary protocol**: data sent as raw bytes, not human-readable text.

### Message Format:
`[length][payload][terminator]`
>“In a heartbeat request, the client sends a small message that says:“Hey server, I’m sending you N bytes of real data. Echo this back to me so I know you’re alive.”
- `length`: 1 byte — how many bytes the client **claims** to send.
- `payload`: N bytes — actual content.
- `'terminator'`: terminator byte to signal end of input (ASCII 0x58).

**Important**: The server trusts `LEN` blindly, leading to a vulnerability.

Then the server replies:

`Z[length][copied_data]`

💡 It literally echoes the message back, just as a liveness confirmation. This is common in real protocols like TLS, TCP keepalives, or even ICMP (ping); we say: “Please confirm you got this message by sending it back.”



---
## Binary Protocol Concepts

### What is a binary protocol?

A **binary protocol** transmits data as raw byte sequences instead of readable text. It's compact and efficient but harder to debug and more error-prone.

| Concept        | Text Protocols          | Binary Protocols         |
|----------------|--------------------------|---------------------------|
| **Readable**   | Yes (`HTTP`, `JSON`)   | No (must be parsed)     |
| **Efficiency** | Moderate               | High (compact, fast)    |
| **Use Cases**  | APIs, Web requests        | TLS, SSH, gRPC, IoT       |
| **Debugging**  | Easy with `curl`, browser | Needs tools (`hexdump`)   |

---

### Anatomy of the Heartbleed Protocol

- The client sends:  
  `[LENGTH][DATA][X]`  
  - `LENGTH`: how many bytes should be echoed back  
  - `DATA`: the actual payload  
  - `'X'`: ASCII terminator (0x58)

- The server replies:  
  `Z` + `[echoed length]` + `copied data`

---

## Lesson Learned

-  **Never trust user input blindly**, always verify declared lengths match actual received data.
- Binary protocols can easily cause memory leaks if bounds are unchecked.
- Defensive coding practices are critical in low-level C programs.

---
## File Descriptions

- `hbs.c`: C source file for the TCP server with the Heartbleed bug.
- `good`: a well-formed client message (`04 41 41 41 41 58`) → claims 4 bytes, sends 4.
- `evil`: a malicious client message (`20 58`) → claims **32 bytes**, but actual payload is only 1 byte: 58 = 'X' (also happens to serve as terminator)! So, the server interprets 58 as part of the payload, not as a terminator in this case:

**Server:**
1. Reads until 'X' (so total of 2 bytes: `[0x20][0x58]`)

2.	Trusts the first byte blindly → `0x20 = 32`

3.	Starts copying 32 bytes from memory starting at the second byte (which is just 'X'), even though:

4. Client only sent 1 byte

5. The rest is whatever garbage was already in memory

That’s the “bleed”: a memory leak of 31 bytes the client was never supposed to see.

---


## Binary Protocol Anatomy

### Client Sends

`[length][payload][terminator]`

| Byte Offset | Meaning             | Example (good)            | Example (evil)             |
|-------------|---------------------|----------------------------|-----------------------------|
| `0`         | Payload length (N)  | `0x04` → 4                 | `0x20` → 32                 |
| `1..N`      | Payload             | `0x41 0x41 0x41 0x41` = AAAA | `0x58` = 'X' (alone)        |
| `N+1`       | Terminator ('X')    | `0x58`                     | `0x41` → overreads occur    |

---

### Server Replies

[Z][length][copied_payload]

| Byte Offset | Meaning             |
|-------------|---------------------|
| `0`         | ASCII `'Z'`         |
| `1`         | Echoed length       |
| `2..2+N`    | Copied payload      |

---

## Code Logic Mapping

### Receiving the Request

```c
while (i < BUF_SIZE && byte != 'X') {
    recv(client_fd, &byte, 1, 0);
    buffer[i++] = byte;
}
```

- buffer[0] → claimed [length]
- buffer[1..i-2] → [payload]
- byte == 'X' → [terminator], not passed to handler
Fixing Heartbleed in handle_request

`uint8_t claimed_len = buffer[0];`

`size_t actual_len = received_len - 1;`

`uint8_t safe_len = claimed_len <= actual_len ? claimed_len : actual_len;`
---
### Crafting a safe response

`reply[0] = 'Z';`

``reply[1] = safe_len;``

`memcpy(reply + 2, buffer + 1, safe_len);`

`send(socket, reply, 2 + safe_len, 0);`

Which builds:

`[Z][safe_len][payload]`

--- 
**Hexdump:**

04 41 41 41 41 58   →  [LEN=4] [Data=AAAA] [X]

**Response:**

5 bytes received
→ Z 04 41 41 41 41


---

### Evil Case (Before Patch)

**Hexdump:**

20 58   →  [Claiming 32], sent only 'X'

Response (before fix):
→ Z 20 + 31 bytes of leaked memory!

---


✅ Evil Case (After Patch)

Response:

→ `Z 00  (nothing copied)`

