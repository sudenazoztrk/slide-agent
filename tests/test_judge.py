from src.evaluation.judge import build_context


def test_build_context_only_slides():
    result = {
        "retrieved_slides": [
            {"slide_number": 5, "text": "Lazy learning açıklaması"},
        ],
        "web_results": ""
    }

    context = build_context(result)

    assert "[Slayt 5]" in context
    assert "Lazy learning açıklaması" in context
    assert "Web Kaynakları" not in context


def test_build_context_with_web():
    result = {
        "retrieved_slides": [
            {"slide_number": 5, "text": "Lazy learning açıklaması"},
        ],
        "web_results": "Transformer nedir açıklaması"
    }

    context = build_context(result)

    assert "[Slayt 5]" in context
    assert "[Web Kaynakları]" in context
    assert "Transformer nedir açıklaması" in context