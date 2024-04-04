from prompts.relevance import *
from prompts.base_reasoning import *
from prompts.search_query import *
from prompts.summarization import *
from prompts.ensemble_reasoning import *
from prompts.alignment import *
from prompts.system import *
from prompts.data_wrangling import *
from prompts.base_eval import *

PROMPT_DICT = {
    "binary": {
        "scratch_pad": {
            "0": BINARY_SCRATCH_PAD_PROMPT_0,
            "1": BINARY_SCRATCH_PAD_PROMPT_1,
            "2": BINARY_SCRATCH_PAD_PROMPT_2,
            "2_tok": BINARY_SCRATCH_PAD_PROMPT_2_TOKENS,
            "3": BINARY_SCRATCH_PAD_PROMPT_3,
            "new_0": BINARY_SCRATCH_PAD_PROMPT_NEW_0,
            "new_1": BINARY_SCRATCH_PAD_PROMPT_NEW_1,
            "new_2": BINARY_SCRATCH_PAD_PROMPT_NEW_2,
            "new_3": BINARY_SCRATCH_PAD_PROMPT_NEW_3,
            "new_4": BINARY_SCRATCH_PAD_PROMPT_NEW_4,
            "new_5": BINARY_SCRATCH_PAD_PROMPT_NEW_5,
            "new_6": BINARY_SCRATCH_PAD_PROMPT_NEW_6,
            "new_7": BINARY_SCRATCH_PAD_PROMPT_NEW_7,
        },
        "rar": {
            "0": RAR_PROMPT_0,
            "1": BINARY_SCRATCH_PAD_PROMPT_1_RAR,
            "2": BINARY_SCRATCH_PAD_PROMPT_2_RAR,
        },
        "emotion": {
            "0": EMOTION_PROMPT_0,
        },
    },
    "ranking": {
        "0": RELEVANCE_PROMPT_0,
    },
    "alignment": {
        "0": ALIGNMENT_PROMPT,
    },
    "search_query": {
        "0": SEARCH_QUERY_PROMPT_0,
        "1": SEARCH_QUERY_PROMPT_1,
        "2": SEARCH_QUERY_PROMPT_2,
        "3": SEARCH_QUERY_PROMPT_3,
        "4": SEARCH_QUERY_PROMPT_4,
        "5": SEARCH_QUERY_PROMPT_5,
        "6": SEARCH_QUERY_PROMPT_6,
        "7": SEARCH_QUERY_PROMPT_7,
        "8": SEARCH_QUERY_PROMPT_8,
    },
    "summarization": {
        "0": SUMMARIZATION_PROMPT_0,
        "1": SUMMARIZATION_PROMPT_1,
        "2": SUMMARIZATION_PROMPT_2,
        "3": SUMMARIZATION_PROMPT_3,
        "4": SUMMARIZATION_PROMPT_4,
        "5": SUMMARIZATION_PROMPT_5,
        "6": SUMMARIZATION_PROMPT_6,
        "7": SUMMARIZATION_PROMPT_7,
        "8": SUMMARIZATION_PROMPT_8,
        "9": SUMMARIZATION_PROMPT_9,
        "10": SUMMARIZATION_PROMPT_10,
        "11": SUMMARIZATION_PROMPT_11,
    },
    "meta_reasoning": {
        "0": ENSEMBLE_PROMPT_0,
        "1": ENSEMBLE_PROMPT_1,
    },
    "system": {
        "0": SYSTEM_SUPERFORECASTER_0,
    },
    "data_wrangling": {
        "is_bad_title": IS_BAD_TITLE_PROMPT,
        "reformat": REFORMAT_PROMPT,
        "assign_category": ASSIGN_CATEGORY_PROMPT,
    },
    "base_eval": {
        "knowledge": KNOWLEDGE_PROMPT,
        "gemini_knowledge": GEMINI_KNOLWEDGE_PROMPT,
        "zero_shot": ZERO_SHOT_PROMPT,
        "scratch_pad": BINARY_SCRATCH_PAD_PROMPT,
        "gemini_scratch_pad": GEMINI_BINARY_SCRATCH_PAD_PROMPT,
    },
}
