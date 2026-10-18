"""Check the actual font selected by Windows GDI without changing application state."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys

from fontTools.ttLib import TTFont


def selected_font_data(family):
    if sys.platform != 'win32':
        raise RuntimeError('Windows is required for the native GDI check')
    gdi = ctypes.WinDLL('gdi32', use_last_error=True)
    gdi.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi.CreateCompatibleDC.restype = wintypes.HDC
    gdi.CreateFontW.argtypes = [ctypes.c_int] * 5 + [wintypes.DWORD] * 8 + [wintypes.LPCWSTR]
    gdi.CreateFontW.restype = wintypes.HFONT
    gdi.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi.SelectObject.restype = wintypes.HGDIOBJ
    gdi.GetFontData.argtypes = [wintypes.HDC, wintypes.DWORD, wintypes.DWORD,
                              ctypes.c_void_p, wintypes.DWORD]
    gdi.GetFontData.restype = wintypes.DWORD
    gdi.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi.DeleteDC.argtypes = [wintypes.HDC]
    dc = gdi.CreateCompatibleDC(None)
    if not dc:
        raise RuntimeError('Cannot create a Windows font device context')
    font = gdi.CreateFontW(48, 0, 0, 0, 400, 0, 0, 0, 1, 0, 0, 0, 0, family)
    if not font:
        gdi.DeleteDC(dc)
        raise RuntimeError('Cannot request the Windows font')
    previous = gdi.SelectObject(dc, font)
    try:
        size = gdi.GetFontData(dc, 0, 0, None, 0)
        if size == 0xffffffff or size == 0:
            raise RuntimeError('Selected Windows font data unavailable')
        payload = ctypes.create_string_buffer(size)
        if gdi.GetFontData(dc, 0, 0, payload, size) != size:
            raise RuntimeError('Selected Windows font data incomplete')
        return payload.raw
    finally:
        gdi.SelectObject(dc, previous)
        gdi.DeleteObject(font)
        gdi.DeleteDC(dc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', default='Leonardus')
    parser.add_argument('--font', type=Path, default=Path('fonts/Leonardus-Regular.ttf'))
    parser.add_argument('--out', type=Path, default=Path('build/office-1.100/windows-font-selection.json'))
    args = parser.parse_args()
    raw = selected_font_data(args.family)
    expected = args.font.read_bytes()
    with TTFont(BytesIO(raw)) as font:
        result = {'requested_family': args.family, 'selected_family': font['name'].getDebugName(1),
                  'selected_version': font['name'].getDebugName(5),
                  'selected_font_sha256': hashlib.sha256(raw).hexdigest(),
                  'expected_font_sha256': hashlib.sha256(expected).hexdigest(),
                  'font_bytes_match': raw == expected,
                  'scope': 'Windows GDI selection only; does not certify Word or PowerPoint rendering'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))
    return 0 if result['font_bytes_match'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
