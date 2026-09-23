"""Tests for export.py. Offline. Run: python -m pytest test_export.py -q"""
import export as ex

SKILL = "---\nname: the-strategist\ndescription: A strategy advisor.\n---\n# The Strategist\nYou advise calmly.\n\n## PERSONA\nCalm."

def test_parse_skill_splits_frontmatter():
    s = ex.parse_skill(SKILL)
    assert s["name"] == "the-strategist" and s["description"] == "A strategy advisor."
    assert s["body"].startswith("# The Strategist")

def test_system_prompt_has_no_frontmatter_and_names_advisor():
    p = ex.to_system_prompt(ex.parse_skill(SKILL))
    assert "You are The Strategist" in p
    assert "name: the-strategist" not in p and "---" not in p
    assert "You advise calmly." in p

def test_card_json_has_instructions():
    c = ex.to_card(ex.parse_skill(SKILL))
    assert c["name"] == "the-strategist" and "You advise calmly." in c["instructions"]
