# Local application/library specific imports
from config.keys import keys
from prompts.prompts import PROMPT_DICT
from utils import db_utils

OAI_SOURCE = "OAI"
ANTHROPIC_SOURCE = "ANTHROPIC"
TOGETHER_AI_SOURCE = "TOGETHER"
GOOGLE_SOURCE = "GOOGLE"
HUGGINGFACE_SOURCE = "HUGGINGFACE"

DEFAULT_RETRIEVAL_CONFIG = {
    "NUM_SEARCH_QUERY_KEYWORDS": 3,
    "MAX_WORDS_NEWSCATCHER": 5,
    "MAX_WORDS_GNEWS": 8,
    "SEARCH_QUERY_MODEL_NAME": "gpt-4-1106-preview",
    "SEARCH_QUERY_TEMPERATURE": 0.0,
    "SEARCH_QUERY_PROMPT_TEMPLATES": [
        PROMPT_DICT["search_query"]["0"],
        PROMPT_DICT["search_query"]["1"],
    ],
    "NUM_ARTICLES_PER_QUERY": 5,
    "SUMMARIZATION_MODEL_NAME": "gpt-3.5-turbo-1106",
    "SUMMARIZATION_TEMPERATURE": 0.2,
    "SUMMARIZATION_PROMPT_TEMPLATE": PROMPT_DICT["summarization"]["9"],
    "NUM_SUMMARIES_THRESHOLD": 10,
    "PRE_FILTER_WITH_EMBEDDING": True,
    "PRE_FILTER_WITH_EMBEDDING_THRESHOLD": 0.32,
    "RANKING_MODEL_NAME": "gpt-3.5-turbo-1106",
    "RANKING_TEMPERATURE": 0.0,
    "RANKING_PROMPT_TEMPLATE": PROMPT_DICT["ranking"]["0"],
    "RANKING_RELEVANCE_THRESHOLD": 4,
    "RANKING_COSINE_SIMILARITY_THRESHOLD": 0.5,
    "SORT_BY": "date",
    "RANKING_METHOD": "llm-rating",
    "RANKING_METHOD_LLM": "title_250_tokens",
    "NUM_SUMMARIES_THRESHOLD": 20,
    "EXTRACT_BACKGROUND_URLS": True,
}

DEFAULT_REASONING_CONFIG = {
    "BASE_REASONING_MODEL_NAMES": ["gpt-4-1106-preview"],
    "BASE_REASONING_TEMPERATURE": 1.0,
    "BASE_REASONING_PROMPT_TEMPLATES": [
        [
            PROMPT_DICT["binary"]["scratch_pad"]["1"],
            PROMPT_DICT["binary"]["scratch_pad"]["2"],
        ],
    ],
    "ALIGNMENT_MODEL_NAME": "gpt-3.5-turbo-1106",
    "ALIGNMENT_TEMPERATURE": 0,
    "ALIGNMENT_PROMPT": PROMPT_DICT["alignment"]["0"],
    "AGGREGATION_METHOD": "meta",
    "AGGREGATION_PROMPT_TEMPLATE": PROMPT_DICT["meta_reasoning"]["0"],
    "AGGREGATION_TEMPERATURE": 0.2,
    "AGGREGATION_MODEL_NAME": "gpt-4",
    "AGGREGATION_WEIGTHTS": None,
}

CHARS_PER_TOKEN = 4

S3 = db_utils.initialize_s3_client(keys["AWS_ACCESS_KEY"], keys["AWS_SECRET_KEY"])
S3_BUCKET_NAME = "my-forecasting-bucket"

MODEL_TOKEN_LIMITS = {
    "claude-2.1": 200000,
    "claude-2": 100000,
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "gpt-4": 8000,
    "gpt-3.5-turbo-1106": 16000,
    "gpt-3.5-turbo-16k": 16000,
    "gpt-3.5-turbo": 8000,
    "gpt-4-1106-preview": 128000,
    "gemini-pro": 30720,
    "togethercomputer/llama-2-7b-chat": 4096,
    "togethercomputer/llama-2-13b-chat": 4096,
    "togethercomputer/llama-2-70b-chat": 4096,
    "togethercomputer/StripedHyena-Hessian-7B": 32768,
    "togethercomputer/LLaMA-2-7B-32K": 32768,
    "mistralai/Mistral-7B-Instruct-v0.2": 32768,
    "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
    "zero-one-ai/Yi-34B-Chat": 4096,
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO": 32768,
    "NousResearch/Nous-Hermes-2-Yi-34B": 32768,
}

MODEL_NAME_TO_SOURCE = {
    "claude-2.1": ANTHROPIC_SOURCE,
    "claude-2": ANTHROPIC_SOURCE,
    "claude-3-opus-20240229": ANTHROPIC_SOURCE,
    "claude-3-sonnet-20240229": ANTHROPIC_SOURCE,
    "gpt-4": OAI_SOURCE,
    "gpt-3.5-turbo-1106": OAI_SOURCE,
    "gpt-3.5-turbo-16k": OAI_SOURCE,
    "gpt-3.5-turbo": OAI_SOURCE,
    "gpt-4-1106-preview": OAI_SOURCE,
    "gemini-pro": GOOGLE_SOURCE,
    "togethercomputer/llama-2-7b-chat": TOGETHER_AI_SOURCE,
    "togethercomputer/llama-2-13b-chat": TOGETHER_AI_SOURCE,
    "togethercomputer/llama-2-70b-chat": TOGETHER_AI_SOURCE,
    "togethercomputer/LLaMA-2-7B-32K": TOGETHER_AI_SOURCE,
    "togethercomputer/StripedHyena-Hessian-7B": TOGETHER_AI_SOURCE,
    "mistralai/Mistral-7B-Instruct-v0.2": TOGETHER_AI_SOURCE,
    "mistralai/Mixtral-8x7B-Instruct-v0.1": TOGETHER_AI_SOURCE,
    "zero-one-ai/Yi-34B-Chat": TOGETHER_AI_SOURCE,
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO": TOGETHER_AI_SOURCE,
    "NousResearch/Nous-Hermes-2-Yi-34B": TOGETHER_AI_SOURCE,
}

ANTHROPIC_RATE_LIMIT = 5

IRRETRIEVABLE_SITES = [
    "wsj.com",
    "english.alarabiya.net",
    "consilium.europa.eu",
    "abc.net.au",
    "thehill.com",
    "democracynow.org",
    "fifa.com",
    "si.com",
    "aa.com.tr",
    "thestreet.com",
    "newsweek.com",
    "spokesman.com",
    "aninews.in",
    "commonslibrary.parliament.uk",
    "cybernews.com",
    "lineups.com",
    "expressnews.com",
    "news-herald.com",
    "c-span.org/video",
    "investors.com",
    "finance.yahoo.com",  # This site has a “read more” button.
    "metaculus.com",  # newspaper4k cannot parse metaculus pages well
    "houstonchronicle.com",
    "unrwa.org",
    "njspotlightnews.org",
    "crisisgroup.org",
    "vanguardngr.com",  # protected by Cloudflare
    "ahram.org.eg",  # protected by Cloudflare
    "reuters.com",  # blocked by Javascript and CAPTCHA
    "carnegieendowment.org",
    "casino.org",
    "legalsportsreport.com",
    "thehockeynews.com",
    "yna.co.kr",
    "carrefour.com",
    "carnegieeurope.eu",
    "arabianbusiness.com",
    "inc.com",
    "joburg.org.za",
    "timesofindia.indiatimes.com",
    "seekingalpha.com",
    "producer.com",  # protected by Cloudflare
    "oecd.org",
    "almayadeen.net",  # protected by Cloudflare
    "manifold.markets",  # prevent data contamination
    "goodjudgment.com",  # prevent data contamination
    "infer-pub.com",  # prevent data contamination
    "www.gjopen.com",  # prevent data contamination
    "polymarket.com",  # prevent data contamination
    "betting.betfair.com",  # protected by Cloudflare
    "news.com.au",  # blocks crawler
    "predictit.org",  # prevent data contamination
    "atozsports.com",
    "barrons.com",
    "forex.com",
    "www.cnbc.com/quotes",  # stock market data: prevent data contamination
    "montrealgazette.com",
    "bangkokpost.com",
    "editorandpublisher.com",
    "realcleardefense.com",
    "axios.com",
    "mensjournal.com",
    "warriormaven.com",
    "tapinto.net",
    "indianexpress.com",
    "science.org",
    "businessdesk.co.nz",
    "mmanews.com",
    "jdpower.com",
    "hrexchangenetwork.com",
    "arabnews.com",
    "nationalpost.com",
    "bizjournals.com",
    "thejakartapost.com",
]

QUESTION_CATEGORIES = [
    "Science & Tech",
    "Healthcare & Biology",
    "Economics & Business",
    "Environment & Energy",
    "Politics & Governance",
    "Education & Research",
    "Arts & Recreation",
    "Security & Defense",
    "Social Sciences",
    "Sports",
    "Other",
]

(
    METACULUS_PLATFORM,
    CSET_PLATFORM,
    GJOPEN_PLATFORM,
    MANIFOLD_PLATFORM,
    POLYMARKET_PLATFORM,
) = ("metaculus", "cset", "gjopen", "manifold", "polymarket")

ALL_PLATFORMS = [
    METACULUS_PLATFORM,
    CSET_PLATFORM,
    GJOPEN_PLATFORM,
    MANIFOLD_PLATFORM,
    POLYMARKET_PLATFORM,
]

END_WORDS_TO_PROBS_6 = {
    "No": 0.05,
    "Very Unlikely": 0.15,
    "Unlikely": 0.35,
    "Likely": 0.55,
    "Very Likely": 0.75,
    "Yes": 0.95,
}

END_WORDS_TO_PROBS_10 = {
    "No": 0.05,
    "Extremely Unlikely": 0.15,
    "Very Unlikely": 0.25,
    "Unlikely": 0.35,
    "Slightly Unlikely": 0.45,
    "Slightly Likely": 0.55,
    "Likely": 0.65,
    "Very Likely": 0.75,
    "Extremely Likely": 0.85,
    "Yes": 0.95,
}

TOKENS_TO_PROBS_DICT = {
    "six_options": END_WORDS_TO_PROBS_6,
    "ten_options": END_WORDS_TO_PROBS_10,
}