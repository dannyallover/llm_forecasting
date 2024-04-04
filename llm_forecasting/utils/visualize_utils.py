# Standard library imports
import datetime

# Related third-party imports
from IPython.core.display import HTML
import markdown2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import logistic
from utils import utils


def visualize_articles(articles, tag="All"):
    """
    Create an HTML table from a list of articles.

    Example usage:
        >> from IPython.display import HTML
        >> display(HTML(visualize_articles(articles)))

    Args:
    - articles (list of dict or obj): List of article objects. Each article
    object should have the following fields:
        - title (str): Title of the article.
        - publish_date (datetime): Date of the article.
        - relevance_rating (float): Relevance rating of the article.
        - relevance_rating_reasoning (str): Model's reasoning for the relevance rating.
        - search_term (str): Search term that retrieved the article.
        - meta_site_name (str): Publisher of the article.
        - text_cleaned (str): Full text of the article.
    - tag (str, optional): Tag to distinguish between different tables.
    Defaults to "All".

    Returns:
    - str: HTML table of the articles.
    """
    rows = ""
    for i, article in enumerate(articles):
        if article.publish_date is None:  # default to now
            article.publish_date = datetime.datetime.now()
        if article.relevance_rating is None:
            article.relevance_rating = "None"
        if article.relevance_rating_reasoning == "":
            article.relevance_rating_reasoning = "N/A"
        rows += f"""
            <tr>
                <td><a href='{article.canonical_link}' target='_blank'>{article.title}</a></td>
                <td>{article.publish_date.date()}</td>
                <td>{article.relevance_rating}</td>
                <td><a href='javascript:void(0);' onclick='event.preventDefault(); toggleText("rating_reason{i}-{tag}")'>...</a><div id='rating_reason{i}-{tag}' style='display:none;'>{article.relevance_rating_reasoning}</div></td>
                <td>{article.search_term}</td>
                <td>{article.meta_site_name}</td>
                <td><a href='javascript:void(0);' onclick='event.preventDefault(); toggleText("fulltext{i}-{tag}")'>...</a><div id='fulltext{i}-{tag}' style='display:none;'>{article.text_cleaned}</div></td>
                <td><a href='javascript:void(0);' onclick='event.preventDefault(); toggleText("summary{i}-{tag}")'>...</a><div id='summary{i}-{tag}' style='display:none;'>{article.summary}</div></td>
            </tr>
        """
    return f"""
        <table>
            <tr>
                <th>Title</th>
                <th>Date</th>
                <th>Relevance Rating</th>
                <th>Relevance Rating Reason</th>
                <th>Search Term</th>
                <th>Publisher</th>
                <th>Full Text</th>
                <th>Summary</th>
            </tr>
            {rows}
        </table>
        <script>
        function toggleText(id) {{
            var x = document.getElementById(id);
            if (x.style.display === "none") {{
                x.style.display = "block";
            }} else {{
                x.style.display = "none";
            }}
        }}
        </script>
    """


def visualize_articles_by_question(articles_by_question):
    """
    Create an HTML table from a dictionary containing questions and the
    relevant articles.

    Example usage:
        >> from IPython.display import HTML
        >> display(HTML(visualize_articles_by_question(articles_by_question)))

    Args:
    - articles_by_question (dict): Dictionary where each index is a question.
    Within each value, there is a list of article objects. Each article object
    should have the following fields:
        - title (str): Title of the article.
        - publish_date (datetime): Date of the article.
        - relevance_rating (float): Relevance rating of the article.
        - search_term (str): Search term that retrieved the article.
        - meta_site_name (str): Publisher of the article.
        - text_cleaned (str): Full text of the article.

    Returns:
    - str: HTML table of the articles.
    """
    rows = ""
    for question in articles_by_question:
        articles = articles_by_question[question]
        for i, article in enumerate(articles):
            rows += f"""
                <tr>
                    <td>{question}</td>
                    <td><a href='{article.canonical_link}' target='_blank'>{article.title}</a></td>
                    <td>{article.publish_date.date()}</td>
                    <td>{article.relevance_rating}</td>
                    <td>{article.search_term}</td>
                    <td>{article.meta_site_name}</td>
                    <td><a href='javascript:void(0);' onclick='event.preventDefault(); toggleText("fulltext{i}")'>...</a><div id='fulltext{i}' style='display:none;'>{article.text_cleaned}</div></td>
                    <td><a href='javascript:void(0);' onclick='event.preventDefault(); toggleText("summary{i}")'>...</a><div id='summary{i}' style='display:none;'>{article.summary}</div></td>
                </tr>
            """
    return f"""
        <table>
            <tr>
                <th>Question</th>
                <th>Title</th>
                <th>Date</th>
                <th>Relevance Rating</th>
                <th>Search Term</th>
                <th>Publisher</th>
                <th>Full Text</th>
                <th>Summary</th>
            </tr>
            {rows}
        </table>
        <script>
        function toggleText(id) {{
            var x = document.getElementById(id);
            if (x.style.display === "none") {{
                x.style.display = "block";
            }} else {{
                x.style.display = "none";
            }}
        }}
        </script>
    """


def visualize_question(data):
    """
    Generate a HTML template to display the information of a single question.

    - data (dict): Dictionary containing the question information. Should have
    the following fields:
        - title (str): Title of the question.
        - description (str): Description of the question (background info, in Markdown format).
        - page_url (str): URL of the question page.
        - publish_time (str): Date (YYYY-MM-DD) the question was published.
        - resolve_time (str): Date the question was resolved.
    """
    # Convert Markdown to HTML
    description_html = markdown2.markdown(data["background"])

    # HTML template
    html = f"""
    <div class="question-container">
        <a href="https://www.metaculus.com{data['url']}" class="question-title">{data['question']}</a>
        <div class="question-details">
            <p><strong>Publish Time:</strong> {data['date_begin'].split('T')[0]}</p>
            <p><strong>Resolve Time:</strong> {data['date_resolve_at'].split('T')[0]}</p>
            <p><strong>Resolution:</strong> {data['resolution']}</p>
        </div>
        <div class="question-description">{description_html}</div>
    </div>
    """

    return html


def visualize_forecasts(
    model_names, prompt_templates, full_prompts, reasonings, predictions, brier_scores
):
    """
    Generate an HTML table to display the forecasts and reasonings of a list of
    models.
    """
    rows = ""
    for i, model_name in enumerate(model_names):
        for j in range(len(reasonings[i])):
            prompt_template = prompt_templates[i][j]
            prompt = full_prompts[i][j]
            reasoning = reasonings[i][j]
            prediction = predictions[i][j]
            brier_score = brier_scores[i][j]

            cleaned_prompt_template = prompt_template[0].replace("\n", "<br>")
            cleaned_prompt = prompt.replace("\n", "<br>")
            cleaned_reasoning = reasoning.replace("\n", "<br>")
            rows += f"""
                <tr>
                    <td>{model_name}</td>
                    <td><a href='javascript:void(0);' onclick='event.preventDefault(); toggleText("full_prompt{i}-{j}")'>...</a><div id='full_prompt{i}-{j}' style='display:none;'>{cleaned_prompt}</div></td>
                    <td><a href='javascript:void(0);' onclick='event.preventDefault(); toggleText("prompt_tempalate{i}-{j}")'>...</a><div id='prompt_tempalate{i}-{j}' style='display:none;'>{cleaned_prompt_template}</div></td>
                    <td><a href='javascript:void(0);' onclick='event.preventDefault(); toggleText("reasoning{i}-{j}")'>...</a><div id='reasoning{i}-{j}' style='display:none;'>{cleaned_reasoning}</div></td>
                    <td>{prediction}</td>
                    <td>{brier_score}</td>
                </tr>
            """
    return f"""
        <table>
            <tr>
                <th>Model</th>
                <th>Full Prompt</th>
                <th>Prompt Template</th>
                <th>Reasoning</th>
                <th>Prediction</th>
                <th>Brier Score</th>
            </tr>
            {rows}
        </table>
        <script>
        function toggleText(id) {{
            var x = document.getElementById(id);
            if (x.style.display === "none") {{
                x.style.display = "block";
            }} else {{
                x.style.display = "none";
            }}
        }}
        </script>
    """


def visualize_all(
    question_data,
    retrieval_dates,
    search_queries_gnews,
    search_queries_nc,
    all_articles,
    ranked_articles,
    all_summaries,
    model_names,
    base_reasoning_prompt_templates,
    base_reasoning_full_prompts,
    base_reasonings,
    base_predictions,
    base_brier_scores,
):
    """
    Given a question and the results from news retrieval, prompt the reasoning
    model to answer the question. Display the question, the relevant articles,
    their summaries, and the final reasoning. Generate an HTML page to display
    the information.

    Args:
    - question_data (dict): Dictionary containing the question information. Should have the following fields:
        - title (str): Title of the question.
        - description (str): Description of the question (background info, in Markdown format).
        - page_url (str): URL of the question page.
        - publish_time (str): Date (YYYY-MM-DD) the question was published.
        - resolve_time (str): Date the question was resolved.
    - retrieval_dates (list of str): List containing the start and end dates of the retrieval period. Should have two elements, formatted as strings in YYYY-MM-DD format.
    - search_queries (list of str): List of search queries used to retrieve the articles.
    - all_articles (list of dict or obj): List of article objects. Retrieved from newscatcher, without relevance rating.
    - ranked_articles (list of dict or obj): List of article objects, containing relevance rating. See visualize_articles() for more details.
    - all_summaries (str): Summaries of all articles retrieved, concatenated together.
    - model_names (list of str): List of model names used to generate the base forecasts.
    - base_reasoning_full_prompts (list of lists of str): The full prompts used for reasoning, including question and article summaries.
    - base_reasonings (list of lists of str): The reasonings and forecasts generated.
    - base_predictions (list of lists of str or float): The final predictions made by model.
    - base_brier_scores (list of lists of float): The Brier scores of the predictions.
    """
    vis_question = HTML(visualize_question(question_data))
    vis_all_articles = HTML(visualize_articles(all_articles, tag="All"))
    vis_ranked = HTML(visualize_articles(ranked_articles, tag="Ranked"))
    vis_forecasts = HTML(
        visualize_forecasts(
            model_names,
            base_reasoning_prompt_templates,
            base_reasoning_full_prompts,
            base_reasonings,
            base_predictions,
            base_brier_scores,
        )
    )
    # Generate the HTML page
    html = "<h2>1. Question and background</h2>" + vis_question.data
    html += (
        "<h2>2. News Retrieval </h2>"
        + "<h3>Retrieval date range:</h3>"
        + "Retrieval begin date: "
        + retrieval_dates[0]
        + "<br>"
        + "Retrieval end date: "
        + retrieval_dates[1]
        + "<br>"
        + "<h3>Search terms used for Gnews:</h3>"
        + ("<br/>".join(search_queries_gnews))
        + "<h3>Search terms used for Newscatcher:</h3>"
        + ("<br/>".join(search_queries_nc))
        + "<h3>All articles retrieved</h3>"
        + vis_all_articles.data
        + "<h3>Relevant articles (ranked) </h3>"
        + vis_ranked.data
    )
    html += "<h2>3. Summaries </h2>" + all_summaries.replace("\n", "<br>")
    html += (
        "<h2>4. Forecasts (Models, Prompts, Reasonings, Predictions)  </h2>"
        + vis_forecasts.data
    )
    return html


def visualize_all_ensemble(
    question_data,
    ranked_articles,
    all_articles,
    search_queries_gnews,
    search_queries_nc,
    retrieval_dates,
    meta_full_prompt,
    meta_reasoning,
    meta_prediction,
):
    """
    Given a question and the results from news retrieval, prompt the reasoning
    model to answer the question. Visualize the question, the relevant
    articles, their summaries, and the final resoning. Generate an HTML page to
    display the information.

    Args:
    - question_data (dict): Dictionary containing the question information.
    Should have the following fields:
        - title (str): Title of the question.
        - description (str): Description of the question (background info, in
        Markdown format).
        - page_url (str): URL of the question page.
        - publish_time (str): Date (YYYY-MM-DD) the question was published.
        - resolve_time (str): Date the question was resolved.
    - ranked_articles (list of dict or obj): List of article objects, containing relevance rating. See visualize_articles() for more details.
    - all_articles (list of dict or obj): List of article objects. Retrieved from newscatcher, without relevance rating.
    - search_queries (list of str): List of keywords extracted from the question.
    - retrieval_dates (list of str): List of date ranges (of length 2) used for news retrieval.
    """
    vis_all_articles = HTML(visualize_articles(all_articles, tag="All"))
    vis_ranked = HTML(visualize_articles(ranked_articles, tag="Ranked"))
    vis_question = HTML(visualize_question(question_data))

    # Generate the HTML page
    html = "<h2>1. Question and background</h2>" + vis_question.data
    html += (
        "<h2>2. News Retrieval </h2>"
        + "<h3>Retrieval date ranges:</h3>"
        + ("<br/>".join(retrieval_dates))
        + "<h3>Search terms used for Gnews:</h3>"
        + ("<br/>".join(search_queries_gnews))
        + "<h3>Search terms used for Newscatcher:</h3>"
        + ("<br/>".join(search_queries_nc))
        + "<h3>All articles retrieved</h3>"
        + vis_all_articles.data
        + "<h3>Relevant articles (ranked) </h3>"
        + vis_ranked.data
    )
    html += (
        "<h2>3. Full prompt to meta reasoning model (including all summaries and base reasonings)</h2>"
        + meta_full_prompt.replace("\n", "<br>")
    )
    html += "<h2>4. Meta reasoning</h2>" + meta_reasoning.replace("\n", "<br>")
    html += "<h2>5. Final prediction</h2>" + str(meta_prediction)

    return html