#!/usr/bin/env python3
"""Inspect an IPA without extracting or executing it (Python standard library)."""

import argparse
import hashlib
import json
import plistlib
import struct
import zipfile
from pathlib import Path, PurePosixPath


THIN = {b'\xcf\xfa\xed\xfe': ('<', 32), b'\xce\xfa\xed\xfe': ('<', 28),
        b'\xfe\xed\xfa\xcf': ('>', 32), b'\xfe\xed\xfa\xce': ('>', 28)}
FAT = {b'\xca\xfe\xba\xbe': ('>', 20, 'II'),
       b'\xca\xfe\xba\xbf': ('>', 32, 'QQ'),
       b'\xbe\xba\xfe\xca': ('<', 20, 'II'),
       b'\xbf\xba\xfe\xca': ('<', 32, 'QQ')}


def encryption_info(data):
    slices = [(0, len(data))]
    if data[:4] in FAT:
        endian, width, fields = FAT[data[:4]]
        count = struct.unpack_from(endian + 'I', data, 4)[0]
        if 8 + count * width > len(data):
            raise ValueError('Truncated universal Mach-O header')
        slices = [struct.unpack_from(endian + fields, data, 16 + i * width)
                  for i in range(count)]
    result = []
    for offset, size in slices:
        if offset + size > len(data) or size < 28:
            raise ValueError('Invalid Mach-O slice bounds')
        endian, header_size = THIN[data[offset:offset + 4]]
        count, command_bytes = struct.unpack_from(endian + 'II', data, offset + 16)
        position = offset + header_size
        end = position + command_bytes
        if end > offset + size:
            raise ValueError('Truncated Mach-O load commands')
        for _ in range(count):
            if position + 8 > end:
                raise ValueError('Truncated Mach-O command')
            command, command_size = struct.unpack_from(endian + 'II', data, position)
            if command_size < 8 or position + command_size > end:
                raise ValueError('Invalid Mach-O command size')
            if command in (0x21, 0x2c):
                if command_size < (24 if command == 0x2c else 20):
                    raise ValueError('Truncated encryption command')
                cryptoff, cryptsize, cryptid = struct.unpack_from(
                    endian + 'III', data, position + 8)
                if cryptoff + cryptsize > size:
                    raise ValueError('Encryption range exceeds Mach-O slice')
                result.append(dict(slice_offset=offset, cryptoff=cryptoff,
                                   cryptsize=cryptsize, cryptid=cryptid))
            position += command_size
    return result


def inspect(path):
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive paths')
        for name in names:
            parts = PurePosixPath(name)
            if parts.is_absolute() or '..' in parts.parts:
                raise ValueError('Unsafe archive path')
        damaged = archive.testzip()
        if damaged:
            raise ValueError(f'Archive CRC check failed: {damaged}')
        plists = [n for n in names if n.startswith('Payload/')
                  and n.count('/') == 2 and n.endswith('.app/Info.plist')]
        if len(plists) != 1:
            raise ValueError('Expected exactly one main app Info.plist')
        info = plistlib.loads(archive.read(plists[0]))
        executable = plists[0].rsplit('/', 1)[0] + '/' + info['CFBundleExecutable']
        binaries = {}
        for name in names:
            if name.endswith('/'):
                continue
            with archive.open(name) as stream:
                magic = stream.read(4)
            if magic in THIN or magic in FAT:
                binaries[name] = encryption_info(archive.read(name))
        if executable not in binaries or not binaries[executable]:
            raise ValueError('Main executable has no recognized encryption metadata')
        return dict(filename=path.name, size_bytes=path.stat().st_size,
                    sha256=digest, archive_crc='passed',
                    bundle_id=info['CFBundleIdentifier'],
                    version=info['CFBundleShortVersionString'],
                    build=info['CFBundleVersion'], minimum_os=info.get('MinimumOSVersion'),
                    executable=executable, encryption=binaries,
                    dylibs=[n for n in names if n.endswith('.dylib')],
                    profiles=[n for n in names if n.endswith('.mobileprovision')])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ipa', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--sha256', help='Require an expected input hash')
    parser.add_argument('--require-decrypted', action='store_true')
    args = parser.parse_args()
    try:
        report = inspect(args.ipa)
        if args.sha256 and report['sha256'] != args.sha256.lower():
            raise ValueError('IPA SHA-256 does not match expected input')
        if args.require_decrypted and any(
                item['cryptid'] != 0 for items in report['encryption'].values() for item in items):
            raise ValueError('IPA contains an executable marked encrypted')
        encoded = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(encoded)
        print(encoded, end='')
    except (OSError, ValueError, KeyError, struct.error, zipfile.BadZipFile,
            plistlib.InvalidFileException) as error:
        parser.exit(1, f'IPA inspection failed: {error}\n')


if __name__ == '__main__':
    main()
