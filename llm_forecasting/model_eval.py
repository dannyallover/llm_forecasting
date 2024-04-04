# Standard library imports
import asyncio
import logging
import time

# Related third-party imports
import openai
import together
import anthropic
import google.generativeai as google_ai

# Local application/library-specific imports
from config.constants import (
    OAI_SOURCE,
    ANTHROPIC_SOURCE,
    TOGETHER_AI_SOURCE,
    GOOGLE_SOURCE,
)
from config.keys import (
    ANTHROPIC_KEY,
    OPENAI_KEY,
    TOGETHER_KEY,
    GOOGLE_AI_KEY,
)
from utils import model_utils, string_utils

# Setup code
if ANTHROPIC_KEY:
    anthropic_console = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    anthropic_async_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_KEY)

if OPENAI_KEY:
    oai_async_client = openai.AsyncOpenAI(api_key=OPENAI_KEY)
    oai = openai.OpenAI(api_key=OPENAI_KEY)

if TOGETHER_KEY:
    together.api_key = TOGETHER_KEY
    client = openai.OpenAI(
        api_key=TOGETHER_KEY,
        base_url="https://api.together.xyz/v1",
    )
    
if GOOGLE_AI_KEY:
    google_ai.configure(api_key=GOOGLE_AI_KEY)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_response_with_retry(api_call, wait_time, error_msg):
    """
    Make an API call and retry on failure after a specified wait time.

    Args:
        api_call (function): API call to make.
        wait_time (int): Time to wait before retrying, in seconds.
        error_msg (str): Error message to print on failure.
    """
    while True:
        try:
            return api_call()
        except Exception as e:
            logger.info(f"{error_msg}: {e}")
            logger.info(f"Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)


def get_response_from_oai_model(
    model_name, prompt, system_prompt, max_tokens, temperature, wait_time
):
    """
    Make an API call to the OpenAI API and retry on failure after a specified
    wait time.

    Args:
        model_name (str): Name of the model to use (such as "gpt-4").
        prompt (str): Fully specififed prompt to use for the API call.
        system_prompt (str): Prompt to use for system prompt.
        max_tokens (int): Maximum number of tokens to sample.
        temperature (float): Sampling temperature.
        wait_time (int): Time to wait before retrying, in seconds.

    Returns:
        str: Response string from the API call.
    """

    def api_call():
        """
        Make an API call to the OpenAI API, without retrying on failure.

        Returns:
            str: Response string from the API call.
        """
        model_input = (
            [{"role": "system", "content": system_prompt}] if system_prompt else []
        )
        model_input.append({"role": "user", "content": prompt})
        response = oai.chat.completions.create(
            model=model_name,
            messages=model_input,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # logger.info(f"full prompt: {prompt}")
        return response.choices[0].message.content

    return get_response_with_retry(
        api_call, wait_time, "OpenAI API request exceeded rate limit."
    )


def get_response_from_anthropic_model(
    model_name, prompt, max_tokens, temperature, wait_time
):
    """
    Make an API call to the Anthropic API and retry on failure after a
    specified wait time.

    Args:
        model_name (str): Name of the model to use (such as "claude-2").
        prompt (str): Fully specififed prompt to use for the API call.
        max_tokens (int): Maximum number of tokens to sample.
        temperature (float): Sampling temperature.
        wait_time (int): Time to wait before retrying, in seconds.

    Returns:
        str: Response string from the API call.
    """
    if max_tokens > 4096:
        max_tokens = 4096

    def api_call():
        completion = anthropic_console.messages.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return completion.content[0].text

    return get_response_with_retry(
        api_call, wait_time, "Anthropic API request exceeded rate limit."
    )


def get_response_from_together_ai_model(
    model_name, prompt, max_tokens, temperature, wait_time
):
    """
    Make an API call to the Together AI API and retry on failure after a
    specified wait time.

    Args:
        model_name (str): Name of the model to use (such as "togethercomputer/
        llama-2-13b-chat").
        prompt (str): Fully specififed prompt to use for the API call.
        max_tokens (int): Maximum number of tokens to sample.
        temperature (float): Sampling temperature.
        wait_time (int): Time to wait before retrying, in seconds.

    Returns:
        str: Response string from the API call.
    """

    def api_call():
        chat_completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response = chat_completion.choices[0].message.content

        return response

    return get_response_with_retry(
        api_call, wait_time, "Together AI API request exceeded rate limit."
    )


def get_response_from_google_model(
    model_name, prompt, max_tokens, temperature, wait_time
):
    """
    Make an API call to the Together AI API and retry on failure after a specified wait time.

    Args:
        model (str): Name of the model to use (such as "gemini-pro").
        prompt (str): Initial prompt for the API call.
        max_tokens (int): Maximum number of tokens to sample.
        temperature (float): Sampling temperature.
        wait_time (int): Time to wait before retrying, in seconds.

    Returns:
        str: Response string from the API call.
    """
    model = google_ai.GenerativeModel(model_name)

    response = model.generate_content(
        prompt,
        generation_config=google_ai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=max_tokens,
            temperature=temperature,
        ),
    )
    return response.text


def get_response_from_model(
    model_name,
    prompt,
    system_prompt="",
    max_tokens=2000,
    temperature=0.8,
    wait_time=30,
):
    """
    Make an API call to the specified model and retry on failure after a
    specified wait time.

    Args:
        model_name (str): Name of the model to use (such as "gpt-4").
        prompt (str): Fully specififed prompt to use for the API call.
        system_prompt (str, optional): Prompt to use for system prompt.
        max_tokens (int, optional): Maximum number of tokens to generate.
        temperature (float, optional): Sampling temperature.
        wait_time (int, optional): Time to wait before retrying, in seconds.
    """
    model_source = model_utils.infer_model_source(model_name)
    if model_source == OAI_SOURCE:
        return get_response_from_oai_model(
            model_name, prompt, system_prompt, max_tokens, temperature, wait_time
        )
    elif model_source == ANTHROPIC_SOURCE:
        return get_response_from_anthropic_model(
            model_name, prompt, max_tokens, temperature, wait_time
        )
    elif model_source == TOGETHER_AI_SOURCE:
        return get_response_from_together_ai_model(
            model_name, prompt, max_tokens, temperature, wait_time
        )
    elif model_source == GOOGLE_SOURCE:
        return get_response_from_google_model(
            model_name, prompt, max_tokens, temperature, wait_time
        )
    else:
        return "Not a valid model source."


async def get_async_response(
    prompt,
    model_name="gpt-3.5-turbo-1106",
    temperature=0.0,
    max_tokens=8000,
):
    """
    Asynchronously get a response from the OpenAI API.

    Args:
        prompt (str): Fully specififed prompt to use for the API call.
        model_name (str, optional): Name of the model to use (such as "gpt-3.5-turbo").
        temperature (float, optional): Sampling temperature.
        max_tokens (int, optional): Maximum number of tokens to sample.

    Returns:
        str: Response string from the API call (not the dictionary).
    """
    model_source = model_utils.infer_model_source(model_name)
    while True:
        try:
            if model_source == OAI_SOURCE:
                response = await oai_async_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                )
                return response.choices[0].message.content
            elif model_source == ANTHROPIC_SOURCE:
                response = await anthropic_async_client.messages.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=4096,
                )
                return response.content[0].text
            elif model_source == GOOGLE_SOURCE:
                model = google_ai.GenerativeModel(model_name)
                response = await model.generate_content_async(
                    prompt,
                    generation_config=google_ai.types.GenerationConfig(
                        candidate_count=1,
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                    ),
                )
                return response.text
            elif model_source == TOGETHER_AI_SOURCE:
                chat_completion = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=model_name,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return chat_completion.choices[0].message.content
            else:
                logger.debug("Not a valid model source: {model_source}")
                return ""
        except (Exception, BaseException) as e:
            logger.info(f"Exception, erorr message: {e}")
            logger.info("Waiting for 30 seconds before retrying...")
            time.sleep(30)
            continue


def get_openai_embedding(texts, model="text-embedding-3-large"):
    """
    Query OpenAI's text embedding model to get the embedding of the given text.

    Args:
        texts (list of str): List of texts to embed.

    Returns:
        list of Embedding objects: List of embeddings, where embedding[i].embedding is a list of floats.
    """
    texts = [text.replace("\n", " ") for text in texts]
    while True:
        try:
            embedding = oai.embeddings.create(input=texts, model=model)
            return embedding.data
        except Exception as e:
            logger.info(f"erorr message: {e}")
            logger.info("Waiting for 30 seconds before retrying...")
            time.sleep(30)
            continue


async def async_make_forecast(
    question,
    background_info,
    resolution_criteria,
    dates,
    retrieved_info,
    reasoning_prompt_templates,
    model_name="gpt-4-1106-preview",
    temperature=1.0,
    return_prompt=False,
):
    """
    Asynchronously make forecasts using the given information.

    Args:
        question (str): Question to ask the model.
        background_info (str): Background information to provide to the model.
        resolution_criteria (str): Resolution criteria to provide to the model.
        dates (str): Dates to provide to the model.
        retrieved_info (str): Retrieved information to provide to the model.
        reasoning_prompt_templates (list of str): List of reasoning prompt templates to use.
        model_name (str, optional): Name of the model to use (such as "gpt-4-1106-preview").
        temperature (float, optional): Sampling temperature.
        return_prompt (bool, optional): Whether to return the full prompt or not.

    Returns:
        list of str: List of forecasts and reasonings from the model.
    """
    assert (
        len(reasoning_prompt_templates) > 0
    ), "No reasoning prompt templates provided."
    reasoning_full_prompts = []
    for reasoning_prompt_template in reasoning_prompt_templates:
        template, fields = reasoning_prompt_template
        reasoning_full_prompts.append(
            string_utils.get_prompt(
                template,
                fields,
                question=question,
                retrieved_info=retrieved_info,
                background=background_info,
                resolution_criteria=resolution_criteria,
                dates=dates,
            )
        )
    # Get all reasonings from the model
    reasoning_tasks = [
        get_async_response(
            prompt,
            model_name=model_name,
            temperature=temperature,
        )
        for prompt in reasoning_full_prompts
    ]
    # a list of strings
    all_reasonings = await asyncio.gather(*reasoning_tasks)
    logger.info(
        "Finished {} base reasonings generated by {}".format(
            len(reasoning_full_prompts), model_name
        )
    )
    if return_prompt:
        return all_reasonings, reasoning_full_prompts
    return all_reasonings
