import ctypes as c
import struct
from pathlib import Path

from config import load_config

# Run with Termux Python. LD_PRELOAD selects whether the compatibility library is active.
libc = c.CDLL("libc.so")
_, _, settings = load_config()
samba = c.CDLL(
    str(Path(settings["termux_prefix"]) / "lib/samba/libcliauth-private-samba.so")
)
libc.malloc.argtypes = [c.c_size_t]
libc.malloc.restype = c.c_void_p
libc.free.argtypes = [c.c_void_p]


class Blob(c.Structure):
    _fields_ = [("data", c.c_void_p), ("length", c.c_size_t)]


parse = samba.msrpc_parse
parse.argtypes = [c.c_void_p, c.POINTER(Blob), c.c_char_p]
parse.restype = c.c_bool
# A synthetic NTLM header with a four-byte target name; no real credentials.
data = b"NTLMSSP\0" + struct.pack("<IHHII", 2, 4, 4, 24, 0) + b"TEST"
address = libc.malloc(len(data))
assert address
try:
    c.memmove(address, data, len(data))
    packet, target = Blob(address, len(data)), Blob()
    command, flags = c.c_uint32(), c.c_uint32()
    assert parse(
        None,
        c.byref(packet),
        b"CdBd",
        c.c_char_p(b"NTLMSSP"),
        c.byref(command),
        c.byref(target),
        c.byref(flags),
    )
    assert command.value == 2 and c.string_at(target.data, target.length) == b"TEST"
    print("NTLM header parsing passed")
finally:
    libc.free(address)
