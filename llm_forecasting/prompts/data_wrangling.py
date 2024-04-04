ASSIGN_CATEGORY_PROMPT = (
    """Question: {question}

Background: {background}

Options:
['Science & Tech',
'Healthcare & Biology',
'Economics & Business',
'Environment & Energy',
'Politics & Governance',
'Education & Research',
'Arts & Recreation',
'Security & Defense',
'Social Sciences',
'Sports',
'Other']

Instruction: Assign a category for the given question.

Rules:
1. Make sure you only return one of the options from the option list.
2. Only output the category, and do not output any other words in your response.
3. You have to pick a string from the above categories.

Answer:""",
    ("QUESTION", "BACKGROUND"),
)

IS_BAD_TITLE_PROMPT = (
    """I'm trying to assess the quality of an old forecasting dataset.

Here is a forecasting question from the dataset: {question}.

Please flag questions that don't sound like binary forecasting questions by outputting "flag". If it sounds like a reasonable question, output "ok".

Examples of strings that should be flagged:
"Will I finish my homework tonight?"
"Metaculus party 2023"
"Will Hell freeze over?"
"Heads or tails"
"Will this video reach 100k views by the EOD?"
Examples of strings that should not be flagged:
"Will Megan Markle and Prince Harry have a baby by the end of the year?"
"Will the Brain Preservation Foundation's Large Mammal preservation prize be won by Feb 9th, 2017?"
"Will there be more novel new drugs approved by the FDA in 2016 than in 2015?"

If a question is already resolved, that doesn't mean it should be flagged. When in doubt, mark it as "ok".

Your response should take the following structure:
Insert thinking:
{{ insert your concise thoughts here }}
Classification:
{{ insert "flag" or "ok"}}""",
    ("QUESTION", "BACKGROUND"),
)

REFORMAT_PROMPT = (
    """I have questions that need to be transformed for clarity.

Here are some examples:
Example 1:
Before: Who will win the 2022-2023 Premier League? (Leicester City)
After: *Will Leicester City win the 2022-2023 Premier League?*

Example 2:
Before: What coalition will govern Berlin after the 2023 repeat state election? (SPD+Greens)
After: *Will SPD+Greens govern Berlin after the 2023 repeat state election?*

Example 3:
Before: If Republicans win control of the House of Representatives in the 2022 election, who will be the next Majority Whip of the U.S. House of Representatives? (Rep. Jim Banks)
After: *If Republicans win control of the House of Representatives in the 2022 election, will Jim Banks be the next Majority Whip of the U.S. House of Representatives?*

Example 4:
Before: Economic Trouble: Will a country’s currency depreciate 15% or more in the second half of 2022? (Thai Baht ฿)
After: *Economic Trouble: Will the Thai Baht ฿ currency depreciate 15% or more in the second half of 2022?*

Example 5:
Before: How many of the claims from study 3 of "Behavioral nudges reduce failure to appear for court" (Science, 2020) replicate? After: *Will exactly 2 claims from study 3 of "Behavioral nudges reduce failure to appear for court" (Science, 2020) replicate?*

Can you now transform this question for clarity: {question}

Please place stars around the transformed question.

Your output should take the following structure:
Before: {insert the original question}
After: *{insert the transformed question}*""",
    ("QUESTION",),
)
