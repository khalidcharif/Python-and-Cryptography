#! /usr/bin/env python3
modul= 2**32

#adition function modulos 2^32  
def add32(x, y):
    return (x+y) % modul


# right rotate function 
def rightrotate32(x, n):
    right_part = x >> n
    left_part = (x << (32 - n)) % modul
    return left_part | right_part

# little sigama0 function 
def little_sigma0(x):
    return rightrotate32(x, 7) ^ rightrotate32(x, 18) ^ (x >> 3)

# little_sigma1 fucntion 
def little_sigma1(x):
    return rightrotate32(x, 17) ^ rightrotate32(x, 19) ^ (x >> 10)

# message_schedule function 
def message_schedule(block):
    W=[int.from_bytes(block[i:i+4], byteorder="big") for i in range(0, 64, 4)]
    for i in range(16, 64):
        t= (W[i-16] + little_sigma0(W[i-15]) + W[i-7] + little_sigma1(W[i-2])) % modul
        W.append(t)
    return W

# big_sigma0 fucntion
def big_sigma0(x):
    return rightrotate32(x, 2) ^ rightrotate32(x, 13) ^ rightrotate32(x, 22)

#big_sigma1() function 
def  big_sigma1(x):
    return rightrotate32(x, 6) ^ rightrotate32(x, 11) ^ rightrotate32(x, 25)

# choice function 
def choice(x, y, z):
    return (x & y) ^ (~x & z)

# majority function
def majority(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)

# round function 
def round(state, round_constant, schedule_word):
    ch    = choice(state[4], state[5], state[6])
    temp1 = (state[7] + big_sigma1(state[4]) + ch + round_constant + schedule_word) % modul
    maj   = majority(state[0], state[1], state[2])
    temp2 = (big_sigma0(state[0]) + maj) % modul
    new_state = [
        (temp1 + temp2) % modul,
        state[0],
        state[1],
        state[2],
        (state[3] + temp1) % modul,
        state[4],
        state[5],
        state[6],
        ]
    return new_state


ROUND_CONSTANTS = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

#compress fucntion 
def compress(input_state, block):
    W = message_schedule(block)
    state = input_state
    for i in range(0, 64):
        state = round(state, ROUND_CONSTANTS[i], W[i])
    state = [
        (input_state[0] + state[0]) % modul,
        (input_state[1] + state[1]) % modul,
        (input_state[2] + state[2]) % modul,
        (input_state[3] + state[3]) % modul,
        (input_state[4] + state[4]) % modul,
        (input_state[5] + state[5]) % modul,
        (input_state[6] + state[6]) % modul,
        (input_state[7] + state[7]) % modul,
        ]
    return state

# padding function 
def padding(input_length):
    remainder_bytes = (input_length + 8) % 64  # bytes in the final block, including the encoded bit length
    filler_bytes = 64 - remainder_bytes        # padding bytes we need to add, including the initial 0x80 byte
    zero_bytes = filler_bytes - 1              # 0x00 padding we need to add
    out=bytearray()
    out.append(0x80)
    while(zero_bytes>0):
        out.append(0x00)
        zero_bytes=zero_bytes-1
    out+= (8*input_length).to_bytes(8, 'big')
    return out


IV = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]

#sha256 fucntion 
def sha256(message):
    outt=[]
    for m in message:
        blocks =[]
        codedmessage = b''
        codedmessage += m.encode()
        pad = padding(len(codedmessage))
        codedmessage += pad
        state = IV
        for i in range(0, len(codedmessage), 64):
            blocks.append(codedmessage[i:i+64])
        for b in blocks:
            state = compress(state, b)
        out=bytearray()
        for s in state :
            out = out + s.to_bytes(4, 'big')
        outt.append(out.hex())
    return outt



