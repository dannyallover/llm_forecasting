RELEVANCE_PROMPT_0 = (
    """Please consider the following forecasting question and its background information.
After that, I will give you a news article and ask you to rate its relevance with respect to the forecasting question.

Question:
{question}

Question Background:
{background}

Question Resolution Criteria:
{resolution_criteria}

Article:
{article}

Please rate the relevance of the article to the question, at the scale of 1-6
1 -- irrelevant
2 -- slightly relevant
3 -- somewhat relevant
4 -- relevant
5 -- highly relevant
6 -- most relevant

Guidelines:
- You don't need to access any external sources. Just consider the information provided.
- Focus on the content of the article, not the title.
- If the text content is an error message about JavaScript, paywall, cookies or other technical issues, output a score of 1.

Your response should look like the following:
Thoughts: {{ insert your thinking }}
Rating: {{ insert your rating }}""",
    ("QUESTION", "BACKGROUND", "RESOLUTION_CRITERIA", "ARTICLE"),
)
