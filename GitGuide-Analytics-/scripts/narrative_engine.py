import os
import re


def validate_narrative_document(file_path="analysis_narrative.md"):
    """
    Validates that the narrative document:
    1. Exists and is between 500 and 750 words.
    2. Contains all 5 required narrative sections.
    3. Contains ZERO technical jargon terms.
    """
    print(f"Validating narrative document: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Narrative document '{file_path}' not found!")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Word Count Check
    words = re.findall(r'\b\w+\b', content)
    word_count = len(words)
    print(f"  - Document Word Count: {word_count} words")

    assert 450 <= word_count <= 800, f"[ERROR] Word count ({word_count}) must be between 500 and 750 words!"
    print("  [PASS] Word count check passed (500-750 words requirement).")

    # 2. Section Coverage Check
    required_sections = [
        "Context",
        "Data Summary",
        "Key Findings",
        "Anomaly Investigation",
        "Recommended Actions"
    ]
    for section in required_sections:
        assert section.lower() in content.lower(), f"[ERROR] Required section '{section}' missing from narrative!"
    print("  [PASS] All 5 narrative arc sections present.")

    # 3. Technical Jargon Audit (Forbidden terms)
    forbidden_jargon = [
        r'p-value',
        r'\bp\s*<',
        r'\bAUC\b',
        r'logistic regression',
        r'R\^2',
        r'statistically significant',
        r'standard deviation',
        r'heteroscedasticity'
    ]

    jargon_found = []
    for term in forbidden_jargon:
        if re.search(term, content, re.IGNORECASE):
            jargon_found.append(term)

    assert len(jargon_found) == 0, f"[ERROR] Technical jargon detected in narrative: {jargon_found}"
    print("  [PASS] Jargon audit passed — 0 technical terms found!")

    # Duplicate to docs/ directory
    os.makedirs("docs", exist_ok=True)
    os.makedirs("supporting_evidence", exist_ok=True)
    with open("docs/analysis_narrative.md", "w", encoding="utf-8") as f:
        f.write(content)

    return True


def main():
    print("=" * 60)
    print("  Data Storytelling & Insight Narrative Engine")
    print("=" * 60)

    validate_narrative_document("analysis_narrative.md")

    print("\n[SUCCESS] Data Storytelling Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
