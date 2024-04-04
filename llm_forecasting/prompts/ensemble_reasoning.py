ENSEMBLE_PROMPT_0 = (
    """I need your assistance with making a forecast. Here is the question and its metadata.
Question: {question}

Background: {background}

Resolution criteria: {resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

I have retrieved the following information about this question.
Retrieved Info:
{retrieved_info}

In addition, I have generated a collection of other responses and reasonings from other forecasters:
{base_reasonings}

Your goal is to aggregate the information and make a final prediction.

Instructions:
1. Provide reasons why the answer might be no.
{{ Insert your thoughts here }}

2. Provide reasons why the answer might be yes.
{{ Insert your thoughts here }}

3. Aggregate your considerations.
{{ Insert your aggregated considerations here }}

4. Output your prediction (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert the probability here }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "RESOLUTION_CRITERIA",
        "RETRIEVED_INFO",
        "DATES",
        "BASE_REASONINGS",
    ),
)


ENSEMBLE_PROMPT_1 = (
    """I need your assistance with making a forecast. Here is the question and its metadata.
Question: {question}

Background: {background}

Resolution criteria: {resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

I have retrieved the following information about this question.
Retrieved Info:
{retrieved_info}

In addition, I have generated a collection of other responses and reasonings from other forecasters:
{base_reasonings}

Your goal is to aggregate the information and make a final prediction.

Instructions:
1. Think step by step: {{ Insert your step by step consideration }}

2. Aggregate your considerations: {{ Aggregate your considerations }}

3. Output your prediction (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert the probability here }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "RESOLUTION_CRITERIA",
        "RETRIEVED_INFO",
        "DATES",
        "BASE_REASONINGS",
    ),
)
