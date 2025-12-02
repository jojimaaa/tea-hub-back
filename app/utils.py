import unicodedata
from rapidfuzz import process, fuzz, utils


def normalize(text: str) -> str:
    text = text.lower().replace(" ", "_").strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def search_by_title(title: str, posts: list) -> list:
    titles = [post.title for post in posts]
    matches = process.extract(
        title, titles, scorer=fuzz.WRatio,score_cutoff=60, processor=utils.default_process
    )

    post_list = [posts[index] for _, _, index in matches]

    for matched_title, score, index in matches:
        print({
            "score": score,
            "title": matched_title
        })

    return post_list
