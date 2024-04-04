SEARCH_QUERY_PROMPT_0 = (
    """I will provide you with a forecasting question and the background information for the question. I will then ask you to generate short search queries (up to {max_words} words each) that I'll use to find articles on Google News to help answer the question.

Question:
{question}

Question Background:
{background}

Today's date: {date_begin}
Question close date: {date_end}

You must generate this exact amount of queries: {num_keywords}

Start off by writing down sub-questions. Then use your sub-questions to help steer the search queries you produce.

Your response should take the following structure:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

SEARCH_QUERY_PROMPT_1 = (
    """I will provide you with a forecasting question and the background information for the question.

Question:
{question}

Question Background:
{background}

Today's date: {date_begin}
Question close date: {date_end}

Task:
- Generate brief search queries (up to {max_words} words each) to gather information on Google that could influence the forecast.

You must generate this exact amount of queries: {num_keywords}

Your response should take the following structure:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

SEARCH_QUERY_PROMPT_2 = (
    """In this task, I will present a forecasting question along with relevant background information. Your goal is to create {num_keywords} concise search queries (up to {max_words} words each) to gather information that could influence the forecast. Consider different angles and aspects that might impact the outcome.

Question:
{question}

Question Background:
{background}

Today's date: {date_begin}
Question close date: {date_end}

Now, generate {num_keywords} short search queries to search for information on Google News.
You must generate this exact amount of queries: {num_keywords}.
When formulating your search queries, think about various factors that could affect the forecast, such as recent trends, historical data, or external influences.

Your response should take the following structure:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

SEARCH_QUERY_PROMPT_3 = (
    """I will provide you with a forecasting question and the background information for the question. I will then ask you to generate {num_keywords} short search queries (up to {max_words} words each) that I'll use to find articles on Google News to help answer the question.

Question:
{question}

Question Background:
{background}

Today's date: {date_begin}
Question close date: {date_end}

You must generate this exact amount of queries: {num_keywords}

Your response should take the following structure:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

SEARCH_QUERY_PROMPT_4 = (
    """Generate short search queries (up to {max_words} words) for the forecasting question below.

I will use them to query Google News for articles. These search queries should result in articles that help me make an informed prediction.

Question:
{question}

Question Background:
{background}

Today's date: {date_begin}
Question close date: {date_end}

You must generate this exact amount of queries: {num_keywords}.

Your response should take the following structure:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

SEARCH_QUERY_PROMPT_5 = (
    """
Please provide {num_keywords} search queries to input into Google to help me research this forecasting question:

Question: {question}

Background: {background}

Today's Date: {date_begin}
Close Date: {date_end}

Guidelines:
- Include terms related to influential factors that could sway the outcome.
- Use different keyword approaches to get balanced perspectives.
- Each search query should be up to {max_words} words.

You must generate this exact amount of queries: {num_keywords}.

Your response should take the following structure:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

SEARCH_QUERY_PROMPT_6 = (
    """
In this task, you will receive a forecasting question along with its background information. Your objective is to create {num_keywords} targeted search queries, each not exceeding {max_words} words, to unearth information that could shape the forecast.

Question:
{question}

Background:
{background}

Current Date:
{date_begin}
Question Close Date:
{date_end}

Your job is to formulate {num_keywords} distinct and concise search queries. These queries will be used to query Google News to capture diverse perspectives and relevant data from various sources. Think about different elements that could influence the outcome.

Structure your response as follows:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

SEARCH_QUERY_PROMPT_7 = (
    """
In this task, I will present a forecasting question along with relevant background information. Your goal is to create {num_keywords} concise search queries (up to {max_words} words each) to gather information on Google that could influence the forecast.

Question:
{question}

Question Background:
{background}

Today's date: {date_begin}
Question close date: {date_end}

Now, generate {num_keywords} short search queries to search for information on Google News.
Begin by formulating sub-questions related to the main question. Use these sub-questions to guide the creation of your search queries.

Your response should take the following structure:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

SEARCH_QUERY_PROMPT_8 = (
    """In this task, I will present a forecasting question along with relevant background information. Your goal is to create {num_keywords} concise search queries (up to {max_words} words each) to gather information that could influence the forecast. Consider different angles and aspects that might impact the outcome.

Question:
{question}

Question Background:
{background}

Today's date: {date_begin}
Question close date: {date_end}

Now, generate {num_keywords} short search queries to search for information on Google News.

Your response should take the following structure:
Thoughts:
{{ Insert your thinking here. }}
Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "DATES",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)

# To be evaluated
SEARCH_QUERY_PROMPT_NO_DATE_0 = (
    """Generate {num_keywords} search queries (up to {max_words} words each) for the forecasting question below.

I will use them to query Google News for articles. These search queries should result in articles that help me make an informed prediction.

---
Question:
{question}
---

---
Question Background:
{background}
---

Your response should take the following structure:

Thoughts:
{{ insert your thinking here }}

Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)


# To be evaluated
SEARCH_QUERY_PROMPT_NO_DATE_1 = (
    """I will give you a forecasting question and its background information.

Your goal is to generate {num_keywords} search queries (up to {max_words} words each).
The search queries wil be used to query Google News for articles.
They should result in articles that help me make an informed prediction.

---
Question:
{question}
---

---
Question Background:
{background}
---

Your response should take the following structure:

Thoughts:
{{ insert your thinking here }}

Search Queries:
{{ Insert the queries here. Use semicolons to separate the queries. }}""",
    (
        "QUESTION",
        "BACKGROUND",
        "NUM_KEYWORDS",
        "MAX_WORDS",
    ),
)
