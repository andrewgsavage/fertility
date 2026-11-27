"""dBase (.dbf) files, and DATASUS's compressed .dbc variant.

read_dbf maps the file and returns the chosen columns as fixed-width byte strings, fast
enough for the multi-million-row birth registers.

A .dbc file is the .dbf header stored as is, a 4-byte CRC, then the records compressed with
PKWARE's DCL "implode". dbc_to_dbf expands it with common/dbc2dbf.c (after the structure of
Mark Adler's blast.c in zlib's contrib), compiled with gcc on first use into NSO/data/bin/.
"""

import shutil
import struct
import subprocess

import numpy as np

from common.paths import REPO, data_dir

DBC_SOURCE = REPO / "common" / "dbc2dbf.c"


def read_dbf(path, columns=None):
    """{field name: numpy array of bytes} for the given fields (all if None)."""
    with open(path, "rb") as f:
        head = f.read(32)
        n, header_len, record_len = struct.unpack("<IHH", head[4:12])
        fields, offset = [], 1  # byte 0 of each record is the deletion flag
        while True:
            d = f.read(32)
            if d[0] == 0x0D:
                break
            name = d[:11].split(b"\0")[0].decode("latin1")
            fields.append((name, offset, d[16]))
            offset += d[16]
    if offset != record_len:
        raise ValueError(f"{path}: fields add up to {offset} bytes, records are {record_len}")
    raw = np.memmap(path, dtype=np.uint8, mode="r", offset=header_len, shape=(n, record_len))
    names = [f[0] for f in fields]
    missing = set(columns or ()) - set(names)
    if missing:
        raise KeyError(f"{path}: no fields {sorted(missing)}; has {names}")
    out = {}
    for name, o, width in fields:
        if columns is None or name in columns:
            out[name] = np.ascontiguousarray(raw[:, o:o + width]).view(f"S{width}").ravel()
    del raw
    return out


def to_int(values, missing=-1):
    """Byte strings of digits (space-padded) as ints; blanks and non-digits become `missing`."""
    s = np.char.strip(values)
    ok = np.char.isdigit(s)
    out = np.full(len(s), missing, dtype=np.int64)
    out[ok] = s[ok].astype(np.int64)
    return out


def _decoder():
    exe = data_dir("NSO") / "bin" / "dbc2dbf.exe"
    if not exe.exists() or exe.stat().st_mtime < DBC_SOURCE.stat().st_mtime:
        gcc = shutil.which("gcc")
        if gcc is None:
            raise RuntimeError("dbc_to_dbf needs gcc on PATH to compile common/dbc2dbf.c")
        exe.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([gcc, "-O2", "-o", str(exe), str(DBC_SOURCE)], check=True)
    return exe


def dbc_to_dbf(dbc, dbf):
    """Expand a DATASUS .dbc file into a .dbf file."""
    subprocess.run([str(_decoder()), str(dbc), str(dbf)], check=True, capture_output=True)
    return dbf
