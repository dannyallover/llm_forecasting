ALIGNMENT_PROMPT = (
    """Question:
{question}

Background:
{background}

Resolution Criteria:
{resolution_criteria}

Model’s Thinking:
{reasoning}

Task:
Evaluate the alignment between the model's thinking and its prediction. If someone were given the reasoning alone (without the prediction), would they likely arrive at the same prediction?

Alignment Ratings:
1 — Very Not Aligned
2 — Not Aligned
3 — Slightly Not Aligned
4 — Slightly Aligned
5 — Aligned
6 — Very Aligned

Please use these ratings to indicate the degree of alignment between the model's reasoning and its prediction.

Note: If the response indicates that this question is old or it's already been resolved, give it an alignment rating of 1.

I want your answer to follow this format:

Thinking: {{ insert your thinking here }}
Rating: {{ insert your alignment rating here (a number between 1 and 6) }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "REASONING"),
)
