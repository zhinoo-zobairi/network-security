# Hash Functions and Digital Signatures

## 1. What Is a Hash Function?

A **hash function** is an algorithm that takes an input of arbitrary length and produces a fixed-size output, called the **digest** or **fingerprint**.

### Example:

```plaintext
Input (message): "I love crypto!"
Hash: 8fe3b8c2d4ea59a6... (256-bit value)
```

---

## 2. Why Do We Use Hashes in Cryptography?

Hash functions are used to provide:

* **Data integrity** – detect if a message has been modified
* **Authentication** – prove the message is from who you think it is
* **Digital signatures** – hash is signed instead of the full message

---

## 3. Properties of a Good Hash Function

Let $H: X \rightarrow Y$ be a hash function.

### ✅ Basic Required Properties:

1. **Fixed Output Length**:

   * No matter the input length, $H(m)$ is always a fixed size (e.g. 256 bits).

2. **Fast and Easy to Compute**:

   * Given $m$, it should be quick to compute $H(m)$.

3. **Pre-image resistance**:

   * Given hash output $h$, it should be computationally infeasible to find any input $m$ such that $H(m) = h$
   * (Like knowing a fingerprint and trying to find the person)

4. **Second pre-image resistance**:

   * Given a message $m$, it should be hard to find $m' \neq m$ such that $H(m') = H(m)$

   Suppose you already know:
   ```
   H("banana") = "b7f4..."
   ```
   You should not be able to find another `m₂ = "grapefruit123"` that also hashes to `"b7f4..."`.
   > This is a stronger property than pre-image resistance; now we’re assuming the attacker knows one valid message and tries to forge another with the same fingerprint.
5. **Collision resistance**:

   * It should be hard to find **any** pair $m \neq m'$ such that $H(m) = H(m')$
   * (This is what makes digital signatures secure!)

   An attacker shouldn’t be able to find any pair like:
   ```
   H("invoice_A.pdf") == H("invoice_B.pdf")
   ```
   > It’s like two completely different people having the same fingerprint: rare and dangerous in security.

> 💡 If a function satisfies only pre-image and second-preimage resistance, it's a **weak hash function**.
> If it also resists collisions → **strong hash function**.

---

## 4. Attacks on Hash Functions

### First Pre-image Attack: 🔑

> Given a hash $h$, find any message $m$ such that $H(m) = h$.

### Second Pre-image Attack: 🔄 

> Given a known message $m$, find another $m' \neq m$ such that $H(m') = H(m)$. The attacker starts with: A specific known input m₁ (maybe a signed message, public data, etc.) You are told: “Here’s Bob’s fingerprint. Now go find someone else with that exact same fingerprint.” You’re limited to this fingerprint.

### Collision Attack: 💥 

> Find any two messages $m \neq m'$ with $H(m) = H(m')$. The attacker starts with: Nothing. No message is given. You can freely try random combinations. Like trying to find any two people in the world with the same fingerprint; doesn’t matter who, as long as the fingerprints match.

> ⚠️ This is the most dangerous, because you don’t even need to control the message: just generate a pair with same hash. 

---

## 5. The Birthday Attack (with Paradox)
![alt text](images/Birthday_Paradox.png)
The **Birthday Paradox** says:

* With just **23 people** in a room, there's a >50% chance two share a birthday.

In hash functions:

* If the output is $n$ bits, you only need about $2^{n/2}$ tries to find a collision.
* For a 256-bit hash (like SHA-256), \~$2^{128}$ attempts are needed → still large, but NOT $2^{256}$.

> That’s why 128-bit hashes are no longer considered safe: birthday attacks are realistic!

---
## 💡 Is Hashing for Passwords and Hash Tables the Same?

Not quite, but related:

* **Hash Tables (Data Structures)** use fast, non-cryptographic hashes to distribute keys evenly.
* **Cryptographic Hashes** (e.g., SHA-256) are slow and secure, designed to be tamper-proof: You can’t tweak a message without invalidating the signature, unless you can create a valid one for the new message, which is supposed to be computationally infeasible.

Both use the same *idea*: deterministic mapping but have different goals.

---

## 6. How Are Hashes Built Internally?

Most cryptographic hash functions (like SHA-256) use a **block-wise structure**:

1. The input is padded so its length is a multiple of a fixed block size (e.g. 512 bits)
2. Each block is processed by a **compression function** that updates an internal state (We take a **block**, **mash** it with the current status of the hash, and **update** it again. Each step of cooking a food depends on the result from the last, so the final “taste” (digest) depends on all steps.): 
3. The final hash is the result of the last state

### Example Padding:

Input: "hello" → binary string of length 40 bits

* Padding: add `1` bit (Add 10000000 as one byte, because we can’t just add 1 bit, so we pack it into a byte), then `0`s, then original length as bits
* This ensures uniqueness and prevents collision padding tricks
* After padding → 512 bits total
- This block is now ready for SHA-1/SHA-2/etc. to crunch it with the compression function.


## Merkle–Damgård Construction

Most popular hash functions (like MD5, SHA-1, SHA-256) follow this structure:

### Steps:

1. **Pad** the message (next section)
2. **Split into blocks** of fixed size (e.g., 512 bits)
3. **Iterate over blocks** using a compression function
4. Final output is the last state



## Padding Process

To make the input message fit neatly into blocks, it goes through a **specific padding scheme**:

### Steps:

1. **Add a single 1 bit** (like `0x80`, ASCII is 1 byte, and that 0x80 is also 1 byte with just 1 leading 1-bit.)
2. **Add 0s** until the total length is 64 bits short of the next multiple of the block size
3. **Append original message length** in **64-bit big-endian** binary



### Example: Padding "hello"

* "hello" = 5 bytes = 40 bits
* Add 1-bit: `0x80`
* Pad with 0s until total length ≡ 448 mod 512
* Append: `0000...00101000` (which is 40 in 64-bit big-endian)

```plaintext
hello10000000..............00000000 00000000 00000000 00101000
```

✅ Now the message is ready to be split into 512-bit blocks and processed.



## Why Use Big-Endian?

**Big-endian** means most significant byte first. It's a convention for encoding multi-byte integers. Hash algorithms adopt this to:

* Maintain consistency across platforms
* Enable standardization of outputs
---

## 7. Use in Digital Signatures

We don’t sign the entire message directly (too slow!).

Imagine Alice wants to prove to Bob that she wrote a message and that it wasn’t tampered with.

Problem: Messages can be very long (e.g. a 10MB PDF).

🔴 Signing the entire message with RSA is computationally expensive.

✅ **Solution: Hash it first, then sign the digest (short fingerprint).
(Hashing transforms a long message into a short fixed-length output. Alice signs the hash of the message, not the message itself) :**
* Message: `m = "Hi Bob!"`
* Compute $H(m)$ → e.g., SHA-256 output (a 256-bit digest)
* Sign the digest using a private key: $s = h^d mod n$ = $\text{Sign}(H(m))$ = **(RSA signature)**

>It’s not just the hash, it’s the RSA encryption of the hash with her private key.

   - d is Alice’s private key
   - n is part of her RSA keypair
* She sends ✉️ 
m and s (message + signature)
* Bob verifies:

  * He doesn’t trust the hash Alice sent; she could fake both the message and a wrong hash. He computes the hash himself from the received message: $h' = H(m)$
  * Then checks if it matches what the signature says:
  * Use public key to verify the signature against the digest: $h'' = s^e mod n$
  	   - e is Alice’s public key exponent
	   - n is her public modulus
* If $h'' == h'$, the signature is valid.
This gives:

* Integrity ✅
* Authentication ✅
* Non-repudiation ✅
![alt text](images/sign_hashed_1.jpg)
![alt text](images/sign_hashed_2.jpg) 
![alt text](images/sign_hashed_3.jpg) 

That *magical reversal* happens only because the numbers were chosen to satisfy this golden rule:

```math
d · e ≡ 1 mod φ(n)
```

That’s the whole **mathematical engine** behind RSA. In your example:


* $d = 7$, $e = 3$
* `φ(n) = 20`
* So:

  ```math
  7 · 3 = 21 ≡ 1 mod 20
  ```

### 🔐 What This Means:

```math
(h^d)^e mod n = h^{de} mod n = h^1 mod n = h
```
This is the **mathematical magic** of RSA:

- The exponent $de$ "collapses" to $1$ *inside the modulo world*,  
- So we get back the original $h$, even after two exponentiations!

Like a key made to match a lock 🔐🗝️ So **no matter what** the message hash \( h \) is, you always get it back when:

1. **Sign it** using the private exponent \( d \):  
   
   ```math
   s = h^d mod n
   ```

2. **Verify it** using the public exponent \( e \):  
   ```math
   h' = s^e mod n
   ```
✅ **This gives us:**
- **Integrity** (you know what was signed)
- **Authentication** (you know who signed it)
- **Non-repudiation** (they can't deny signing it)

---

## 🔐 MD5 vs SHA-1: Understanding One-Way Hash Functions Step-by-Step

### What is a One-Way Hash Function?

A **one-way hash function** turns any input (text, file, password) into a short, fixed-size fingerprint called a **hash**. You can't reverse the process (hence "one-way").

It’s used for:

* Verifying data integrity (did the file change?)
* Signing messages digitally
* Secure password storage


## MD5 (Message Digest 5)

![alt text](images/MD5.png)

### What MD5 Does

* Takes **any length message**, breaks it into **512-bit blocks**
* Processes each block using **64 fixed steps**
* Outputs a **128-bit hash**

###  How MD5 Works:

1. **Padding the message**: Make it a multiple of 512 bits, plus 64 bits for message length. You have a 512-bit block: that’s just a chunk of your original message, cut into 512 bits (64 bytes).

2. **Initialize state**: The MD5 algorithm doesn’t take those 512 bits and spit out a hash in one go. Instead: It initializes four 32-bit values (A, B, C, D). These are your internal “state”. So, start with 4 fixed values: A, B, C, D (32 bits each)

3. **Process blocks**:

   * Then it processes the 512-bit block in 64 rounds; one tiny step at a time. Each 512-bit block goes through 64 **rounds/steps** of mixing using XOR, AND, NOT, shifts
   * The result of one block becomes the input for the next
4. **Final hash**: After all blocks are processed, you combine A, B, C, D → 128-bit hash

### Why 64 steps?
Because the 512-bit block is broken into **16 * 32-bit words**. Each round uses some bitwise magic on one of these words. But they use a scheduling system that repeats and reshuffles these 16 words across 64 steps. This “stretches” and “mixes” the information deeply.
### Why It Was Popular

* Very fast on Intel CPUs

   Let's say you have:
`0x12345678`
   - Big-endian (like how humans read):
   Stored as: 12 34 56 78
   - Little-endian (used by Intel CPUs):
Stored as: 78 56 34 12

MD5 was designed for Intel’s architecture, so it reads multi-byte data assuming little-endian order
* Easy to implement in software

### Why It’s Broken ❌ 

* In 2004, attackers could generate **collisions** (Find two different inputs produce the same hash output.)
* Finding a collision takes \~2^64 operations — much easier than expected

---

## SHA-1 (Secure Hash Algorithm 1)
![alt text](images/SHA-1.png)
### What SHA-1 Does

* Same general structure as MD5
* Uses **512-bit blocks**
* Outputs a **160-bit hash** (32 bits longer than MD5)

### How SHA-1 Works:

1. **Padding**: Like MD5, pads the message to fit 512-bit blocks
2. **Initialize state**: 5 constants: A, B, C, D, E
3. **Process blocks**:

   * Each block goes through **80 rounds** of bitwise mixing
   * Adds more complexity than MD5
4. **Final hash**: Combine A, B, C, D, E → 160-bit hash

### Why It Was Better Than MD5

* Longer hash = more possible outputs = better collision resistance (in theory)
* Harder to crack, at first

### Why It’s Also Broken

* In 2005, Prof. Xiaoyun Wang showed a **differential attack**:

  * Collisions could be found in \~2^63 operations (not 2^80 as expected)
* Later, others broke even reduced-round SHA-1

---

## Security Breakdown

| Feature                | MD5             | SHA-1           |
| ---------------------- | --------------- | --------------- |
| Output size            | 128 bits        | 160 bits        |
| Designed in            | 1991 (Rivest)   | 1993 (NIST)     |
| Internal state         | A, B, C, D      | A, B, C, D, E   |
| Steps per block        | 64              | 80              |
| Collision resistance   | \~2^64 (broken) | \~2^63 (broken) |
| Architecture optimized | Little-endian   | Big-endian      |
| Secure today?          | ❌             | ❌             |

---

### So What’s the Difference?
![alt text](images/MD5VsSHA-1.png)
* SHA-1 was designed to be **more secure** by adding more rounds and a longer output
* But both are **now insecure** for cryptographic uses

---
