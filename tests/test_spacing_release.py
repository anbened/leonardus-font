"""Preserve chosen shapes while making only the authorized p/q metric changes."""
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import pytest
import uharfbuzz as hb

from leonardus.metrics import MANIFEST, build_spacing, validate_spacing

ROOT = Path(__file__).resolve().parents[1]


def test_spacing_is_reproducible_and_preserves_every_outline_shape(tmp_path):
    first, second = tmp_path/'one.ttf', tmp_path/'two.ttf'
    build_spacing(first, ROOT)
    build_spacing(second, ROOT)
    assert first.read_bytes() == second.read_bytes() == (ROOT/'fonts/Leonardus-1211-Regular.ttf').read_bytes()
    document = validate_spacing(ROOT)
    with TTFont(first) as font, TTFont(ROOT/document['base_font']) as base:
        assert font.getBestCmap() == base.getBestCmap()
        assert len(font.getBestCmap()) == 119 and len(font.getGlyphOrder()) == 121
        for name in font.getGlyphOrder():
            g, previous = font['glyf'][name], base['glyf'][name]
            char = next((c for c in 'pq' if font.getBestCmap()[ord(c)] == name), None)
            if char:
                dx = document['adjustments'][char]['translation_x']
                assert [(x-dx,y) for x,y in g.coordinates] == list(previous.coordinates)
                assert list(g.flags) == list(previous.flags)
                assert g.endPtsOfContours == previous.endPtsOfContours
                assert (g.yMin,g.yMax) == (previous.yMin,previous.yMax)
                assert font['hmtx'][name] == (document['adjustments'][char]['after']['advance'],g.xMin)
            else:
                assert g.compile(font['glyf']) == previous.compile(base['glyf'])
                assert font['hmtx'][name] == base['hmtx'][name]
        cmap=font.getBestCmap()
        assert font['hmtx'][cmap[ord('p')]][0]-font['glyf'][cmap[ord('p')]].xMax+font['glyf'][cmap[ord('q')]].xMin == 115
        shaper=hb.Font(hb.Face(first.read_bytes()));shaper.scale=(1000,1000);hb.ot_font_set_funcs(shaper)
        for char in 'pq':
            buf=hb.Buffer();buf.add_str(char+'\u0301');buf.guess_segment_properties();hb.shape(shaper,buf)
            assert len(buf.glyph_infos)==2 and all(i.codepoint for i in buf.glyph_infos)
            g=font['glyf'][cmap[ord(char)]];pos=buf.glyph_positions[1]
            assert font['hmtx'][cmap[ord(char)]][0]+pos.x_offset == round((g.xMin+g.xMax)/2+35)
            assert pos.y_offset==g.yMax+60 and pos.x_advance==0
        assert font['name'].getDebugName(1)=='Leonardus 1211' and font['OS/2'].fsType==0
    with pytest.raises(ValueError,match='Cannot overwrite'):
        build_spacing(ROOT/'fonts/Leonardus-1210-Regular.ttf',ROOT)


@pytest.mark.parametrize('mutation',['shape','scope','base','metric'])
def test_spacing_rejects_changes_outside_the_declared_scope(tmp_path,mutation):
    doc=validate_spacing(ROOT)
    for relative in [MANIFEST,doc['base_font']]:
        dest=tmp_path/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,dest)
    if mutation=='shape':doc['outline_shape_changes']=True
    elif mutation=='scope':doc['adjustments']['r']=doc['adjustments']['p']
    elif mutation=='base':doc['base_font_sha256']='0'*64
    else:doc['adjustments']['q']['after']['left']=-1
    (tmp_path/MANIFEST).write_text(json.dumps(doc),encoding='utf-8')
    with pytest.raises(ValueError):validate_spacing(tmp_path)
