import unicodedata
from rapidfuzz import fuzz, process, utils
from app.models.wiki import WikiPosts


def normalize(text: str) -> str:
    text = text.lower().replace(" ", "_").strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def search_by_title(
    title: str, wiki_posts: list[WikiPosts], amount: int
) -> list[WikiPosts]:
    wiki_titles = [wiki.title for wiki in wiki_posts]
    matches = process.extract(
        title, wiki_titles, limit=amount, processor=utils.default_process
    )

    wiki_post_list = [wiki_posts[index] for _, _, index in matches]

    return wiki_post_list
