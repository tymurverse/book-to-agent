"""Tests for ground.py (grounding + fidelity). Offline. Run: python -m pytest test_ground.py -q"""
import ground as g

SRC = ("Chapter One. All warfare is based on deception. If you know the enemy and know yourself "
       "you need not fear a hundred battles. Supreme excellence is winning without fighting.")

def test_grounds_real_frameworks_and_flags_fakes():
    fws = [
        {"name": "Deception", "anchors": ["warfare is based on deception"]},
        {"name": "Know yourself", "anchors": ["know the enemy and know yourself", "hundred battles"]},
        {"name": "Invented thing", "anchors": ["blockchain", "quarterly OKRs"]},
    ]
    d = g.score(SRC, fws)
    byn = {r["name"]: r for r in d["frameworks"]}
    assert byn["Deception"]["grounded"] is True
    assert byn["Know yourself"]["grounded"] is True and byn["Know yourself"]["coverage"] == 1.0
    assert byn["Invented thing"]["grounded"] is False          # hallucination caught
    assert "Invented thing" in d["flagged"]
    assert d["fidelity_score"] == 67                            # 2 of 3 grounded

def test_partial_coverage_below_threshold_is_flagged():
    d = g.score(SRC, [{"name": "Half", "anchors": ["hundred battles", "not in the text at all"]}])
    assert d["frameworks"][0]["coverage"] == 0.5 and d["frameworks"][0]["grounded"] is False

def test_evidence_is_returned_for_grounded():
    d = g.score(SRC, [{"name": "D", "anchors": ["warfare is based on deception"]}])
    assert "deception" in d["frameworks"][0]["evidence"].lower()
