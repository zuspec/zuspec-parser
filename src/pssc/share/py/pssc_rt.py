"""The runtime seam a pssc-generated Python operation model calls into.

Copied beside the generated module by `op-model-py` (suppress with
`--no-core-copy` if your project installs it another way). Nothing here is
generated; this file is shipped source and is the whole of what a generated
model needs at run time.

THE BUS IS A PROTOCOL, NOT A BASE CLASS. A generated model calls `read32` /
`write32` on whatever object it was constructed with and imports nothing to do
it, so the object you pass may be a cocotb driver, a socket client, a register
model from another framework, or `MemoryBus` below. `Bus` exists to document
the four methods and to give a type checker something to point at -- inheriting
from it is optional and buys nothing.

Widths are named rather than parameterised (`read32`, not `read(32, addr)`)
because that is how the PSS core library declares them (`addr_reg_pkg`,
21.12) and how every other pssc backend renders them; a bus written against one
generated model works against them all.
"""
from __future__ import annotations

__all__ = ["Bus", "MemoryBus", "Chan1", "ChannelEmpty", "ChannelFull"]


class Bus:
    """What a generated model requires of the object it is constructed with.

    Implement the widths your device is actually accessed at; a generated model
    only calls the ones its registers need. The unimplemented default raises
    rather than returning zero -- a silent zero from a register read is a
    driver that reports a device stuck in reset.
    """

    def read8(self, addr: int) -> int:
        raise NotImplementedError(f"{type(self).__name__}.read8")

    def read16(self, addr: int) -> int:
        raise NotImplementedError(f"{type(self).__name__}.read16")

    def read32(self, addr: int) -> int:
        raise NotImplementedError(f"{type(self).__name__}.read32")

    def read64(self, addr: int) -> int:
        raise NotImplementedError(f"{type(self).__name__}.read64")

    def write8(self, addr: int, data: int) -> None:
        raise NotImplementedError(f"{type(self).__name__}.write8")

    def write16(self, addr: int, data: int) -> None:
        raise NotImplementedError(f"{type(self).__name__}.write16")

    def write32(self, addr: int, data: int) -> None:
        raise NotImplementedError(f"{type(self).__name__}.write32")

    def write64(self, addr: int, data: int) -> None:
        raise NotImplementedError(f"{type(self).__name__}.write64")

    def message(self, text: str) -> None:
        """`std_pkg::message()`. Defaults to printing; override to route it."""
        print(text)


class MemoryBus(Bus):
    """A flat sparse memory. Enough to bring a generated model up and to test it.

    Reads of never-written addresses return 0, which is right for a memory and
    wrong for a device: a status bit polled in a completion loop never sets, so
    a `repeat {} while` against this spins forever. That is a property of the
    stub, not of the generated code -- drive a real device model, or subclass
    and override the register in question.
    """

    def __init__(self, wordsize: int = 4):
        self.mem = {}
        self.wordsize = wordsize
        #: Every access, in order: `("read", width, addr, data)`. A test asserts
        #: on this rather than on the generated source, which is what makes it a
        #: check of BEHAVIOUR and not of spelling.
        self.log = []

    # -- the protocol -------------------------------------------------------

    def read8(self, addr):    return self._read(8, addr)

    def read16(self, addr):   return self._read(16, addr)

    def read32(self, addr):   return self._read(32, addr)

    def read64(self, addr):   return self._read(64, addr)

    def write8(self, addr, data):    self._write(8, addr, data)

    def write16(self, addr, data):   self._write(16, addr, data)

    def write32(self, addr, data):   self._write(32, addr, data)

    def write64(self, addr, data):   self._write(64, addr, data)

    def message(self, text):
        self.log.append(("message", 0, 0, text))

    # -- storage ------------------------------------------------------------

    def _read(self, width, addr):
        data = self.mem.get(addr, 0) & ((1 << width) - 1)
        self.log.append(("read", width, addr, data))
        return data

    def _write(self, width, addr, data):
        data &= (1 << width) - 1
        self.mem[addr] = data
        self.log.append(("write", width, addr, data))


class ChannelEmpty(Exception):
    """A blocking `get()` on an empty channel, with no scheduler to wait in."""


class ChannelFull(Exception):
    """A blocking `put()` on a full channel, with no scheduler to wait in."""


class Chan1(object):
    """A depth-1 `sync_pkg::channel_c`.

    Depth 1 only, matching `share/c/pssc_chan.h` and `share/cpp/pssc_chan.hpp`:
    a deeper channel is a ring buffer, which is a different type per capacity,
    and the generator refuses one rather than quietly widening it.

    `get`/`put` SUSPEND in PSS, and a plain Python model has no scheduler to
    suspend to, so they raise instead of blocking -- the same position the C and
    C++ targets take, and for the same reason: a `get()` that returned whatever
    was in the slot would report a completion nobody signalled. Use
    `try_get`/`try_put`, which the generator does lower.
    """

    __slots__ = ("value", "full")

    def __init__(self):
        self.value = 0
        self.full = False

    def try_put(self, value) -> bool:
        if self.full:
            return False
        self.value = value
        self.full = True
        return True

    def try_get(self, out):
        """Receive into *out*, a ONE-ELEMENT LIST; return whether anything came.

        The list is how a PSS output argument reaches Python. `try_get(tok)`
        writes through a pointer in C and cannot in Python, where an int is
        immutable and a name rebound inside a call is not rebound outside it --
        so the generator declares exactly those locals as cells (it knows which
        ones; the same analysis widens them to 64 bits in the C backend) and
        this writes into the cell.

        A tuple return would read better and would not work: the call appears
        in `if (!inflight.try_get(tok))`, where its value is a condition and
        there is nowhere to unpack a second result to.
        """
        if not self.full:
            return False
        self.full = False
        out[0] = self.value
        return True

    def put(self, value):
        raise ChannelFull(
            "put() blocks, and a generated Python operation model has no "
            "scheduler to block in. Use try_put().")

    def get(self):
        raise ChannelEmpty(
            "get() blocks, and a generated Python operation model has no "
            "scheduler to block in. Use try_get().")
