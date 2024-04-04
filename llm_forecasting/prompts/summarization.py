SUMMARIZATION_PROMPT_0 = (
    """Summarize the article below, ensuring to include details pertinent to the subsequent question.

Question: {question}
Question Background: {background}

Article:
---
{article}
---""",
    ("QUESTION", "BACKGROUND"),
)

SUMMARIZATION_PROMPT_1 = (
    """I will present a forecasting question and a related article.

Question: {question}
Question Background: {background}

Article:
---
{article}
---

A forecaster prefers a list of bullet points containing facts, observations, details, analysis, etc., over reading a full article.

Your task is to distill the article as a list of bullet points that would help a forecaster in his deliberation.""",
    ("QUESTION", "BACKGROUND"),
)

SUMMARIZATION_PROMPT_2 = (
    """I want to make the following article shorter (condense it to no more than 500 words).

Article:
---
{article}
---

When doing this task for me, please do not remove any details that would be helpful for making considerations about the following forecasting question.

Forecasting Question: {question}
Question Background: {background}""",
    ("QUESTION", "BACKGROUND"),
)

SUMMARIZATION_PROMPT_3 = (
    """I will present a forecasting question and a related article.

Forecasting Question: {question}
Question Background: {background}

Article:
---
{article}
---

Use the article to write a list of bullet points that help a forecaster in their deliberation.

Guidelines:
- Ensure each bullet point contains specific, detailed information.
- Avoid vague statements; instead, focus on summarizing key observations, data, predictions, or analysis presented in the article.
- Also, extract points that directly or indirectly contribute to a better understanding or prediction of the specified question.""",
    ("QUESTION", "BACKGROUND"),
)


SUMMARIZATION_PROMPT_4 = (
    """Summarize the below article.

Article:
---
{article}
---""",
    ("",),
)


SUMMARIZATION_PROMPT_5 = (
    """I will present a forecasting question and a related article.

Question: {question}
Question Background: {background}

Article:
---
{article}
---

I want to shorten the following article (condense it to no more than 500 words). When doing this task for me, please do not remove any details that would be helpful for making considerations about the forecasting question.""",
    ("QUESTION", "BACKGROUND"),
)


SUMMARIZATION_PROMPT_6 = (
    """Create a summary of the following article that assists in making a prediction for the following question.

Forecasting Question: {question}
Question Background: {background}

Article:
---
{article}
---

Guidelines for Summary:
- Include bullet points that extract key facts, observations, and analyses directly relevant to the forecasting question.
- Then include analysis that connects the article's content to the forecasting question.
- Strive for a balance between brevity and completeness, aiming for a summary that is informative yet efficient for a forecaster's analysis.""",
    ("QUESTION", "BACKGROUND"),
)


SUMMARIZATION_PROMPT_7 = (
    """Create a summary of the following article that assists in making a prediction for the following question.

Prediction Question: {question}
Question Background: {background}

Article:
---
{article}
---

Guidelines for Summary:
- Include bullet points that extract key facts, observations, and analyses directly relevant to the forecasting question.
- Where applicable, highlight direct or indirect connections between the article's content and the forecasting question.
- Strive for a balance between brevity and completeness, aiming for a summary that is informative yet efficient for a forecaster's analysis.""",
    ("QUESTION", "BACKGROUND"),
)


SUMMARIZATION_PROMPT_8 = (
    """I want to make the following article shorter (condense it to no more than 100 words).

Article:
---
{article}
---

When doing this task for me, please do not remove any details that would be helpful for making considerations about the following forecasting question.

Forecasting Question: {question}
Question Background: {background}""",
    ("QUESTION", "BACKGROUND"),
)

SUMMARIZATION_PROMPT_9 = (
    """I want to make the following article shorter (condense it to no more than 100 words).

Article:
---
{article}
---

When doing this task for me, please do not remove any details that would be helpful for making considerations about the following forecasting question.

Forecasting Question: {question}
Question Background: {background}""",
    ("QUESTION", "BACKGROUND"),
)

SUMMARIZATION_PROMPT_10 = (
    """I will present a forecasting question and a related article.

Forecasting Question: {question}
Question Background: {background}

Article:
---
{article}
---

Use the article to write a list of bullet points that help a forecaster in their deliberation.

Guidelines:
- Ensure each bullet point contains specific, detailed information.
- Avoid vague statements; instead, focus on summarizing key observations, data, predictions, or analysis presented in the article.
- Your list should never exceed 5 bullet points.""",
    ("QUESTION", "BACKGROUND"),
)


SUMMARIZATION_PROMPT_11 = (
    """I will present a forecasting question and a related article.

Question: {question}
Question Background: {background}

Article:
---
{article}
---

A forecaster prefers a list of bullet points containing facts, observations, details, analysis, etc., over reading a full article.

Your task is to distill the article as a list of bullet points that would help a forecaster in his deliberation. Ensure, that you make your list as concise and short as possible without removing critical information.""",
    ("QUESTION", "BACKGROUND"),
)
