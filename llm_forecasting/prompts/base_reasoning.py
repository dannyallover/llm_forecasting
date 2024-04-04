BINARY_SCRATCH_PAD_PROMPT_0 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Provide at least 3 reasons why the answer might be no.
{{ Insert your thoughts }}

2. Provide at least 3 reasons why the answer might be yes.
{{ Insert your thoughts }}

3. Rate the strength of each of the reasons given in the last two responses. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your rating of the strength of each reason }}

4. Aggregate your considerations.
{{ Insert your aggregated considerations }}

5. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)


BINARY_SCRATCH_PAD_PROMPT_1 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Write down any additional relevant information that is not included above. This should be specific facts that you already know the answer to, rather than information that needs to be looked up.
{{ Insert additional information }}

2. Provide at least 3 reasons why the answer might be no.
{{ Insert your thoughts }}

3. Provide at least 3 reasons why the answer might be yes.
{{ Insert your thoughts }}

4. Rate the strength of each of the reasons given in the last two responses. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your rating of the strength of each reason }}

5. Aggregate your considerations.
{{ Insert your aggregated considerations }}

6. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_2 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Think step by step: {{ Insert your step by step consideration }}
Aggregating considerations: {{ Aggregate your considerations }}
Answer: {{ Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_2_TOKENS = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}

Think step by step: {{ Insert your step by step consideration }}
Aggregating considerations: {{ Aggregate your considerations }}
Answer: {{ Output one of these: "No", "Extremely Unlikely", Very Unlikely", "Unlikely", "Slightly Unlikely", "Slightly Likely", "Likely", "Very Likely", "Extremely Likely", "Yes" }}

Note: Here are how the words map to probabilities
No (0%-10%)
Extremely Unlikely (10%-20%)
Very Unlikely  (20%-30%)
Unlikely (30%-40%)
Slightly Unlikely (40%-50%)
Slightly Likely (50%-60%)
Likely (60%-70%)
Very Likely (70%-80%)
Extremely Likely (80%-90%)
Yes (90%-100%)""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_3 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Provide reasons why the answer might be no.
{{ Insert your thoughts }}

2. Provide reasons why the answer might be yes.
{{ Insert your thoughts }}

3. Aggregate your considerations.
{{ Insert your aggregated considerations }}

4. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_NEW_0 = (
    """Question: {question}

Today's date: {date_begin}
Question close date: {date_end}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Provide a few reasons why the answer might be no. Rate the strength of each reason.
{{ Insert your thoughts }}

3. Provide a few reasons why the answer might be yes. Rate the strength of each reason.
{{ Insert your thoughts }}

4. Aggregate your considerations. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your aggregated considerations }}

5. Output an initial probability (prediction) given steps 1-4.
{{ Insert initial probability. }}

6. Evaluate whether your calculated probability is excessively confident or not confident enough. Also, consider anything else that might affect the forecast that you did not before consider.
{{ Insert your thoughts }}

7. Output your final prediction (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)


BINARY_SCRATCH_PAD_PROMPT_NEW_1 = (
    """Question: {question}

Today's date: {date_begin}
Question close date: {date_end}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Provide a few reasons why the answer might be "yes" or "no". Rate the strength of each reason.
{{ Insert your thoughts }}

3. Consider anything else that might affect the forecast that you did not before consider.
{{ Insert your thoughts }}

4. Aggregate your considerations. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your aggregated considerations }}

5. Output an initial probability (prediction) given steps 1-4.
{{ Insert initial probability. }}

6. Evaluate whether your calculated probability is excessively confident or not confident enough.
{{ Insert your thoughts }}

7. Output your final prediction (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_NEW_2 = (
    """Question: {question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Using your knowledge of the world and topic, as well as the information provided, provide a few reasons why the answer might be no. Rate the strength of each reason.
{{ Insert your thoughts }}

3. Using your knowledge of the world and topic, as well as the information provided, provide a few reasons why the answer might be yes. Rate the strength of each reason.
{{ Insert your thoughts }}

4. Aggregate your considerations. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your aggregated considerations }}

5. Output an initial probability (prediction) given steps 1-4.
{{ Insert initial probability. }}

6. Evaluate whether your calculated probability is excessively confident or not confident enough. Also, consider anything else that might affect the forecast that you did not before consider (e.g. base rate of the event).
{{ Insert your thoughts }}

7. Output your final prediction (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_NEW_3 = (
    """Question: {question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Provide a few reasons why the answer might be no. Rate the strength of each reason.
{{ Insert your thoughts }}

3. Provide a few reasons why the answer might be yes. Rate the strength of each reason.
{{ Insert your thoughts }}

4. Aggregate your considerations. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your aggregated considerations }}

5. Output an initial probability (prediction) given steps 1-4.
{{ Insert initial probability. }}

6. Feel free to adjust your probability now. Here is a non-exhaustive list of some things you'll want to check:
- Is your calculated probability excessively confident or not confident enough?
- Is there anything else that might affect the forecast that you did not before consider (e.g. base rate of the event)?
- Use your intuition and feel for the question.
{{ Insert your thoughts }}

7. Output your final answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_NEW_4 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Using your knowledge of the world and topic, as well as the information provided, provide a few reasons why the answer might be no. Rate the strength of each reason.
{{ Insert your thoughts }}

3. Using your knowledge of the world and topic, as well as the information provided, provide a few reasons why the answer might be yes. Rate the strength of each reason.
{{ Insert your thoughts }}

4. Aggregate your considerations. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your aggregated considerations }}

5. Output an initial probability (prediction) given steps 1-4.
{{ Insert initial probability. }}

6. Feel free to adjust your probability now. Here is a non-exhaustive list of some things you'll want to check:
- Is your calculated probability excessively confident or not confident enough?
- Is there anything else that might affect the forecast that you did not before consider?
- Are there any potential unforeseen factors or developments that you'll want to consider?
- Are there any potential biases in the available information?
- Use your intuition and feel for the question.
{{ Insert your thoughts }}

7. Output your final answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_NEW_5 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Using your knowledge of the world and topic, as well as the information provided, provide a few reasons why the answer might be no. Rate the strength of each reason.
{{ Insert your thoughts }}

3. Using your knowledge of the world and topic, as well as the information provided, provide a few reasons why the answer might be yes. Rate the strength of each reason.
{{ Insert your thoughts }}

4. Aggregate your considerations.
{{ Insert your aggregated considerations }}

5. Output an initial probability (prediction) given steps 1-4.
{{ Insert initial probability. }}

6. Feel free to adjust your probability now. Here is a non-exhaustive list of some things you'll want to check:
- Is your calculated probability is excessively confident or not confident enough.
- Is there anything else that might affect the forecast that you did not before consider.
- Use your intuition and feel for the question.
{{ Insert your thoughts }}

7. Output your final answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_NEW_6 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Develop a decision tree outlining possible paths to both 'Yes' and 'No' outcomes.
{{ Insert decision tree outline }}

3. Analyze the probability of each branch of the decision tree based on current information.
{{ Insert branch probability analysis }}

4. Discuss any potential game-changers or wildcard events. Use your knowledge of the topic as well as the information provided.
{{ Insert discussion on wildcards }}

5. Output an initial probability (prediction) given steps 1-4.
{{ Insert initial probability. }}

6. Feel free to adjust your probability now. Here is a non-exhaustive list of some things you'll want to check:
- Is your calculated probability is excessively confident or not confident enough.
- Is there anything else that might affect the forecast that you did not before consider.
- Use your intuition and feel for the question.
{{ Insert your thoughts }}

7. Output your final answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)

BINARY_SCRATCH_PAD_PROMPT_NEW_7 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Develop a decision tree outlining possible paths to both 'Yes' and 'No' outcomes.
{{ Insert decision tree outline }}

3. Analyze the probability of each branch of the decision tree based on current information.
{{ Insert branch probability analysis }}

4. Incorporate your knowledge of the topic as well as the information provided, and output an initial probability (prediction) given steps 1-3.
{{ Insert discussion on wildcards }}

5. Feel free to adjust your probability now. Here is a non-exhaustive list of some things you'll want to check:
- Is your calculated probability is excessively confident or not confident enough.
- Is there anything else that might affect the forecast that you did not before consider.
- Use your intuition and feel for the question.
{{ Insert your thoughts }}

6. Output your final answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)


RAR_PROMPT_0 = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}

Instructions:
1. Rephrase and expand the question, and respond.

2. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)


BINARY_SCRATCH_PAD_PROMPT_1_RAR = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Think step by step: {{ Insert your step by step consideration }}

3. Aggregating considerations: {{ Aggregate your considerations }}

4. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)


BINARY_SCRATCH_PAD_PROMPT_2_RAR = (
    """Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Given the above question, rephrase and expand it to help you do better answering. Maintain all information in the original question.
{{ Insert rephrased and expanded question.}}

2. Provide at least 3 reasons why the answer might be no.
{{ Insert your thoughts }}

3. Provide at least 3 reasons why the answer might be yes.
{{ Insert your thoughts }}

4. Rate the strength of each of the reasons given in the last two responses. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your rating of the strength of each reason }}

5. Aggregate your considerations.
{{ Insert your aggregated considerations }}

6. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)


EMOTION_PROMPT_0 = (
    """Help me make a forecast for the following question.

This is very important to my career.

Question:
{question}

Question Background:
{background}

Resolution Criteria:
{resolution_criteria}

Today's date: {date_begin}
Question close date: {date_end}

We have retrieved the following information for this question:
{retrieved_info}


Instructions:
1. Write down any additional relevant information that is not included above. This should be specific facts that you already know the answer to, rather than information that needs to be looked up.
{{ Insert additional information }}

2. Provide at least 3 reasons why the answer might be no.
{{ Insert your thoughts }}

3. Provide at least 3 reasons why the answer might be yes.
{{ Insert your thoughts }}

4. Rate the strength of each of the reasons given in the last two responses. Think like a superforecaster (e.g. Nate Silver).
{{ Insert your rating of the strength of each reason }}

5. Aggregate your considerations.
{{ Insert your aggregated considerations }}

6. Output your answer (a number between 0 and 1) with an asterisk at the beginning and end of the decimal.
{{ Insert your answer }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "DATES", "RETRIEVED_INFO"),
)
