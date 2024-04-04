KNOWLEDGE_PROMPT = (
    """Question: {question}

The question was posed on {date_begin} and closed on {date_end}.
Instructions: 
- Please output "1" if the answer is Yes", "0" if the answer is No or "IDK" if you don't know the answer. Do not return anything else.
- Do not guess.
Answer: {{ Insert answer here }}""",
    ("QUESTION", "DATES"),
)

GEMINI_KNOLWEDGE_PROMPT = (
    """Here was a forecasting question posed in {date_begin} and resolved in {date_end}.
Question: {question} (Only Output: 1 (Yes), 0 (No), or IDK if you don't know the answer.)
Answer: {{ Insert answer here }} """,
    ("QUESTION", "DATES"),
)

ZERO_SHOT_PROMPT = (
    """You are an expert superforecaster, familiar with the work of Tetlock and others. Make a prediction of the probability that the question will be resolved as true. You MUST give a probability estimate between 0 and 1 UNDER ALL CIRCUMSTANCES. If for some reason you can't answer, pick the base rate, but return a number between 0 and 1.

Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal. Do not output anything else.
Answer: {{ Insert answer here }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES"),
)

BINARY_SCRATCH_PAD_PROMPT = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}


Instructions:
1. Provide reasons why the answer might be no.
{{ Insert your thoughts }}

2. Provide reasons why the answer might be yes.
{{ Insert your thoughts }}

3. Aggregate your considerations.
{{ Insert your aggregated considerations }}

4. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES"),
)

GEMINI_BINARY_SCRATCH_PAD_PROMPT = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

Output why the answer might be no, why the answer might be yes, aggredate your considerations, and then your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES"),
)
