import base64
import binascii
import hashlib
import hmac
import random
import string
import struct


def bin_to_long(x):
    """
    Convert a binary string into a long integer

    This is a clever optimization for fast xor vector math
    """
    return int(binascii.hexlify(x), 16)


def long_to_bin(x, hex_format_string):
    """
    Convert a long integer into a binary string.
    hex_format_string is like "%020x" for padding 10 characters.
    """
    return binascii.unhexlify((hex_format_string % x).encode('ascii'))


def pbkdf2(password, salt, iterations, dklen=0):
    """
    Implements PBKDF2 as defined in RFC 2898, section 5.2

    HMAC+SHA256 is used as the default pseudo random function.

    As of 2014, 100,000 iterations was the recommended default which took
    100ms on a 2.7Ghz Intel i7 with an optimized implementation.
    
    see django.utils.crypto.py for more information.
    """
    assert iterations > 0
    digest = hashlib.sha256
    password = password.encode('utf-8')
    salt = salt.encode('utf-8')
    hlen = digest().digest_size
    if not dklen:
        dklen = hlen
    if dklen > (2 ** 32 - 1) * hlen:
        raise OverflowError('dklen too big')
    l = -(-dklen // hlen)
    r = dklen - (l - 1) * hlen

    hex_format_string = "%%0%ix" % (hlen * 2)

    inner, outer = digest(), digest()
    if len(password) > inner.block_size:
        password = digest(password).digest()
    password += b'\x00' * (inner.block_size - len(password))
    inner.update(password.translate(hmac.trans_36))
    outer.update(password.translate(hmac.trans_5C))

    def F(i):
        u = salt + struct.pack(b'>I', i)
        result = 0
        for j in range(int(iterations)):
            dig1, dig2 = inner.copy(), outer.copy()
            dig1.update(u)
            dig2.update(dig1.digest())
            u = dig2.digest()
            result ^= bin_to_long(u)
        return long_to_bin(result, hex_format_string)

    T = [F(x) for x in range(1, l)]
    return b''.join(T) + F(l)[:r]


def encode_password(password):
    algorithm = "pbkdf2_sha256"
    iterations = 100000
    salt = ''.join(
        random.SystemRandom().choice(
            string.ascii_letters + string.digits
        ) for i in range(12)
    )
    assert password is not None    
    hash = pbkdf2(password, salt, iterations)
    hash = base64.b64encode(hash).decode('ascii').strip()
    return "%s$%d$%s$%s" % (algorithm, iterations, salt, hash)
