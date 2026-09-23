"""Tests for extract.py (clean + skeleton). Offline. Run:
   python -m pytest test_extract.py -q"""
import extract as ex


def test_clean_fixes_artifacts_and_dehyphenates():
    raw = "The ﬁrst “Grand—Slam” oppor-\ntunity is ‘tight’."
    out = ex.clean(raw)
    assert "first" in out                       # ligature fixed
    assert '"Grand-Slam"' in out                # smart quotes + em dash normalised
    assert "opportunity" in out                 # word split across a line break rejoined
    assert "'tight'" in out


def test_skeleton_finds_real_headers_and_skips_prose():
    text = (
        "Section II: Pricing\n"
        "3. Pricing: The Commodity Problem\n"
        "THE VALUE EQUATION\n"
        "this is an ordinary sentence of body prose that should not be treated as a header at all\n"
        "How To Charge More\n"
        "4. Finding The Right Market\n"
    )
    sk = ex.skeleton(text)
    joined = " | ".join(sk)
    assert "Section II: Pricing" in sk
    assert "3. Pricing: The Commodity Problem" in sk
    assert "THE VALUE EQUATION" in sk
    assert "4. Finding The Right Market" in sk
    assert not any("ordinary sentence" in h for h in sk)   # prose excluded


def test_skeleton_dedupes():
    text = "GRAND SLAM OFFERS\nGRAND SLAM OFFERS\nGrand Slam Offers\n"
    assert len(ex.skeleton(text)) == 1
