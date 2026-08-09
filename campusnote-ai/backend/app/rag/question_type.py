"""
Question Type Detection
========================
Lightweight keyword-based classifier (Section 10). This is intentionally
rule-based rather than an extra LLM call, so classification is fast, free,
and deterministic -- it only decides which answer template/instructions to
hand to the LLM, not the content of the answer itself.
"""
import re

QUESTION_TYPES = [
    "difference",
    "advantages_disadvantages",
    "algorithm",
    "programming",
    "numerical",
    "diagram",
    "compare",
    "short_note",
    "definition",
    "explain",
    "describe",
]

PATTERNS = {
    "difference": [r"\bdifference\b", r"\bdistinguish\b", r"\bvs\.?\b", r"\bcompare\b.*\bcontrast\b"],
    "advantages_disadvantages": [r"advantages?\s*(and|&)?\s*disadvantages?", r"\bpros\b.*\bcons\b", r"\bmerits\b.*\bdemerits\b"],
    "algorithm": [r"\balgorithm\b", r"\bpseudocode\b", r"\bsteps? (of|to|for)\b"],
    "programming": [r"\bwrite (a|the) program\b", r"\bcode\b", r"\bimplement\b.*\bprogram\b", r"\bfunction\b.*\bwrite\b"],
    "numerical": [r"\bcalculate\b", r"\bsolve\b", r"\bnumerical\b", r"\bcompute\b", r"\bgiven\b.*\bfind\b"],
    "diagram": [r"\bdiagram\b", r"\bdraw\b", r"\bwith (a )?neat diagram\b", r"\bblock diagram\b"],
    "compare": [r"\bcompare\b"],
    "short_note": [r"\bshort note\b", r"\bwrite (a )?short\b", r"\bbrief(ly)?\b"],
    "definition": [r"\bdefine\b", r"\bwhat is\b", r"\bwhat are\b", r"\bmeaning of\b"],
    "explain": [r"\bexplain\b", r"\belaborate\b", r"\bdiscuss\b"],
    "describe": [r"\bdescribe\b"],
}


def detect_question_type(question: str) -> str:
    q = question.lower().strip()
    for qtype, patterns in PATTERNS.items():
        for pat in patterns:
            if re.search(pat, q):
                return qtype
    return "explain"  # sensible default for open-ended exam questions
