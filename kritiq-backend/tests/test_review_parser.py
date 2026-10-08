from ai_agent.review_parser import parse_raw_review


def test_parse_structured_json():
    raw = '''{"summary":"One issue found.","issues":[{"title":"Unused Variable","line":2,"severity":"medium","explanation":"`debug_mode` is assigned but never used.","suggested_fix":"Remove `debug_mode`."}]}'''
    summary, issues = parse_raw_review(raw)
    assert summary == "One issue found."
    assert issues == [{
        "title": "Unused Variable",
        "line": 2,
        "severity": "medium",
        "explanation": "`debug_mode` is assigned but never used.",
        "suggested_fix": "Remove `debug_mode`.",
    }]


def test_parse_fenced_json():
    raw = '''```json\n{"summary":"Clean","issues":[]}\n```'''
    summary, issues = parse_raw_review(raw)
    assert summary == "Clean"
    assert issues == []


def test_parse_multiple_issues_and_null_line():
    raw = '''{"summary":"Several issues.","issues":[{"title":"Unused Variable","line":2,"severity":"medium","explanation":"unused","suggested_fix":"remove"},{"title":"Design Smell","line":null,"severity":"low","explanation":"smell","suggested_fix":null},{"title":"Injection","line":9,"severity":"high","explanation":"unsafe","suggested_fix":"validate"}]}'''
    _, issues = parse_raw_review(raw)
    assert len(issues) == 3
    assert issues[1]["line"] is None
    assert issues[2]["severity"] == "high"


def test_legacy_malformed_markdown_is_not_concatenated_into_title():
    raw = '''Summary: One issue.\nIssues:\n1. **Unused Variable**debug_mode***Line:** line 2 **Explanation:** The variable `debug_mode` is declared and assigned but never referenced. **Suggested Fix:** Remove the variable.'''
    _, issues = parse_raw_review(raw)
    assert len(issues) == 1
    assert issues[0]["title"] == "Unused Variable"
    assert issues[0]["line"] == 2
    assert issues[0]["severity"] == "medium"
    assert "debug_mode" in issues[0]["explanation"]
    assert issues[0]["suggested_fix"] == "Remove the variable."


def test_invalid_json_uses_legacy_fallback():
    raw = '''Summary: One issue.\nIssues:\n1. Unused Variable - line 2. The variable is unused.'''
    summary, issues = parse_raw_review(raw)
    assert summary == "One issue."
    assert issues[0]["title"] == "Unused Variable"
    assert issues[0]["line"] == 2
