"""
Grounded Prompt Builder
========================
Builds the system + user prompt sent to the LLM. This is the core of
Section 8 (Strict Grounding), Section 9 (Exam Answer Generation), and
Section 10 (Question Type Detection instructions).

The LLM only ever sees the retrieved chunks as its source of truth --
never the raw question answered from general knowledge.
"""
from typing import List, Dict

BASE_SYSTEM_PROMPT = """You are CampusNote AI, a college study assistant.

Answer the student's question using ONLY the retrieved college notes provided below.

Rules:
- Do not invent information that is not present in the retrieved notes.
- Do not pretend that information exists in the notes if it does not.
- If the retrieved material does not contain enough information to answer, say exactly:
  "This information is not available in the uploaded college notes."
- You may explain retrieved information clearly and in your own words, but do not introduce unrelated facts.
- Preserve important terminology used in the source material (exact terms, formulas, algorithm names).
- Whenever you state a fact drawn from a specific source chunk, keep it traceable to that chunk;
  the system will attach source citations (document + page) separately, so focus on grounded content.
- Never claim a fact comes from a source unless that source's retrieved text actually supports it.
"""

MARKS_INSTRUCTIONS = {
    2: "Format: 2-MARK ANSWER. Give a concise definition plus one or two key points. Keep it very short (2-4 sentences total).",
    5: "Format: 5-MARK ANSWER. Give a definition, a clear explanation, important points as bullets, an example if the notes contain one, and a short conclusion.",
    10: "Format: 10-MARK ANSWER. Structure as: Introduction, Definition, Detailed explanation with subheadings, Steps/process if applicable, Example, Advantages/Disadvantages if present in the notes, Conclusion.",
    13: "Format: 13-MARK ANSWER. Structure as: Introduction, Definition, Detailed explanation with subheadings, Steps/process if applicable, Example, Advantages/Disadvantages if present in the notes, Conclusion. Go into more depth than a 10-mark answer where the notes support it.",
    15: "Format: 15-MARK ANSWER. Structure as: Introduction, Definition, Detailed explanation with subheadings, Steps/process if applicable, Example, Diagram description if relevant and supported by notes, Advantages/Disadvantages if present in the notes, Conclusion. This should be the most comprehensive answer, still strictly grounded in the notes.",
}

QUESTION_TYPE_INSTRUCTIONS = {
    "difference": "This is a DIFFERENCE/COMPARISON question. Present the answer as a markdown table with columns for each item being compared, plus a short intro sentence.",
    "advantages_disadvantages": "This is an ADVANTAGES/DISADVANTAGES question. Use two clearly labeled bullet lists: Advantages and Disadvantages, based only on what the notes state.",
    "algorithm": "This is an ALGORITHM question. Structure as: Aim, Algorithm/Steps (numbered), Pseudocode (only if present in the notes), Time/Space Complexity (only if the notes state it), Example (if present).",
    "programming": "This is a PROGRAMMING question. Structure as: Explanation, Algorithm, Code (in a fenced code block), Sample Output (if determinable), Code Explanation. Only produce code that matches the approach described in the retrieved notes, or a standard well-known implementation if the question clearly calls for it.",
    "numerical": "This is a NUMERICAL/PROBLEM-SOLVING question. Show the given data, the formula/method (from the notes if available), step-by-step working, and the final answer.",
    "diagram": "This is a DIAGRAM-BASED question. Describe the diagram's structure and components clearly in words/steps (actual image rendering is not supported), based only on what the notes describe.",
    "compare": "This is a COMPARISON question. Use a markdown table where useful, covering the compared items based only on the notes.",
    "short_note": "This is a SHORT NOTE question. Keep the answer compact: a definition plus 3-5 key bullet points.",
    "definition": "This is a DEFINITION question. Give a precise, concise definition, optionally with one supporting sentence.",
    "explain": "This is an EXPLAIN question. Explain the concept clearly and thoroughly, using the structure implied by the requested mark value.",
    "describe": "This is a DESCRIBE question. Describe the concept/process/system clearly using the structure implied by the requested mark value.",
}


def format_retrieved_context(chunks: List[Dict]) -> str:
    """chunks: [{"document": str, "page": int, "text": str, "unit": str}]"""
    if not chunks:
        return "(No relevant chunks were retrieved from the uploaded college notes.)"
    blocks = []
    for i, c in enumerate(chunks, start=1):
        page_str = f"Page {c['page']}" if c.get("page") else "Page N/A"
        blocks.append(
            f"[Source {i}: {c['document']} — {page_str}]\n{c['text']}"
        )
    return "\n\n".join(blocks)


def build_prompt(
    question: str,
    retrieved_chunks: List[Dict],
    question_type: str,
    marks: int = None,
) -> Dict[str, str]:
    """Returns {"system": ..., "user": ...} to send to the LLM."""
    system = BASE_SYSTEM_PROMPT

    instructions = []
    if question_type in QUESTION_TYPE_INSTRUCTIONS:
        instructions.append(QUESTION_TYPE_INSTRUCTIONS[question_type])
    if marks and marks in MARKS_INSTRUCTIONS:
        instructions.append(MARKS_INSTRUCTIONS[marks])
    if instructions:
        system += "\n\nAnswer formatting instructions:\n- " + "\n- ".join(instructions)

    context = format_retrieved_context(retrieved_chunks)

    user = f"""RETRIEVED COLLEGE NOTES:
{context}

STUDENT QUESTION:
{question}

Answer strictly using the retrieved college notes above."""

    return {"system": system, "user": user}
