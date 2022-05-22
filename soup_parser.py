import math
import re
from typing import FrozenSet, List, Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from constants import (
    BOOKS_CATEGORIES_BLACKLIST,
    BOOKS_CATEGORIES_WHITELIST,
    COMMENT_HELPFUL_SPAN_CSS,
    COMMENT_STAR_SPAN_CSS,
    COMMENT_TEXT_SPAN_CSS,
    DEFAULT_COUNT,
    ITEM_CSS,
    ITEM_LIMIT,
    ITEM_LIST_ID,
    ITEM_PRODUCT_REVIEW_CSS,
    ITEM_RANK_CSS,
    PRODUCT_COMMENT_CSS,
    PRODUCT_COMMENTS_CONTAINER_ID,
    PRODUCT_REVIEW_AVERAGE_STAR_CSS,
    PRODUCT_REVIEW_HEADER_CSS,
    PRODUCT_REVIEW_INFO_ID,
    PRODUCT_REVIEW_NUMBER_RATINGS_CSS,
    STAR_NAME_TO_STAR_TYPE,
    TREE_ID,
    ItemRatingStatistics,
    ItemReview,
    Uri,
)


def get_best_sellers_tree(
    best_sellers_page: BeautifulSoup, departments_list_id: str = TREE_ID
) -> Optional[BeautifulSoup]:
    """Get the `Departments Best Sellers` tree soup from the best_sellers_page soup."""
    return best_sellers_page.find(id=departments_list_id)


def get_childrens_name_uris(
    root: BeautifulSoup, current_level: int = 0
) -> Optional[List[Tuple[str, Uri]]]:
    """Get a tuple list of child_names and URI from a best_sellers node.

    `current_level` refers to the level of the `root` node of the
    Departments Best Sellers tree.

    At level 0, the default value, the root is assumed to be `Any Departments`.
    """

    categories_node = root

    # Look for the list of children directly bellow root level.
    for _ in range(current_level + 1):
        categories_node = categories_node.find("ul")

        if categories_node is None:
            return None

    return [
        (a.text, Uri(urlparse(a["href"]).path)) for a in categories_node.findAll("a")
    ]


def get_child_uri(children: List[Tuple[str, Uri]], name) -> Optional[Uri]:
    """Get the Uri of a child with a specific name."""
    return next((x[1] for x in children if x[0] == name), None)


def remove_childs(
    childs: List[Tuple[str, Uri]], black_list: FrozenSet = BOOKS_CATEGORIES_BLACKLIST
) -> List[Tuple[str, Uri]]:
    """Remove childs of name and uris which names are contained in the `black_list`.

    By default, `black_list` is a FrozenSet fo `BOOKS_CATEGORIES_BLACKLIST`.
    """
    return [it for it in childs if it[0] not in black_list]


def remove_childs_whitelist(
    childs: List[Tuple[str, Uri]], white_list: FrozenSet = BOOKS_CATEGORIES_WHITELIST
) -> List[Tuple[str, Uri]]:
    """Remove childs of name and uris which names are not contained in the `white_list`.

    By default, `white_list` is a FrozenSet fo `BOOKS_CATEGORIES_WHITELIST`.
    """
    return [it for it in childs if it[0] in white_list]


def get_items(
    items_page: BeautifulSoup,
    item_list_id: str = ITEM_LIST_ID,
    link_class=ITEM_PRODUCT_REVIEW_CSS,
    limit=ITEM_LIMIT,
) -> Optional[List[Tuple[int, Uri]]]:
    """Get a list of ASIN and top position from a best_sellers_page soup.

    The `best_sellers_page` must be of at least a `department` level, or level
    1 in the `Departments Best Sellers` tree.
    """
    root = items_page.find(id=item_list_id)

    if root is None:
        return None

    items_spans = root.findAll("span", class_=ITEM_CSS)

    if items_spans is None:
        return None

    items_list = (
        *filter(lambda x: x is not None, [get_item_info(item) for item in items_spans]),
    )

    return [*dict([(t[1], (t[0], t[2])) for t in reversed(items_list)]).values()]


def get_items_next_page(best_seller_page: BeautifulSoup) -> Optional[Uri]:
    """Get the URI corresponding to next page of items.

    The `best_sellers_page` must be of at least a `department` level, or level
    1 in the `Departments Best Sellers` tree.
    """
    # TODO Not needed now, but It may in the future.
    return None


def get_item_info(
    item_span: BeautifulSoup,
    link_class=ITEM_PRODUCT_REVIEW_CSS,
    rank_class=ITEM_RANK_CSS,
) -> Optional[Tuple[int, str, Uri]]:
    """Get info from an item span."""
    review_uri = item_span.find("a", class_=link_class)
    rank = item_span.find("span", class_=rank_class)
    title = item_span.find("img")

    if any(map(lambda x: x is None, [rank, review_uri, title])):
        return None

    return (
        int(re.sub("[^0-9]", "", rank.text)),
        title["alt"],
        review_uri["href"],
    )


def get_item_title(item_review_soup: BeautifulSoup) -> Optional[str]:
    header_title_soup = item_review_soup.find("h1", class_=PRODUCT_REVIEW_HEADER_CSS)

    if header_title_soup is None:
        return None

    title_link_soup = header_title_soup.find("a")

    if title_link_soup is None:
        return None

    return title_link_soup.text


def get_item_review_statistics(
    item_review_soup: BeautifulSoup, asin: str, genre: str, top_n: int
) -> Optional[ItemRatingStatistics]:
    "From a item_review_soup, get `ItemReviewsStatistics`"

    stars_info_soup = item_review_soup.find(id=PRODUCT_REVIEW_INFO_ID)

    if stars_info_soup is None:
        return None

    average_stars_soup = stars_info_soup.find(class_=PRODUCT_REVIEW_AVERAGE_STAR_CSS)

    if average_stars_soup is None:
        return None

    n_ratings_soup = stars_info_soup.find(class_=PRODUCT_REVIEW_NUMBER_RATINGS_CSS)

    if n_ratings_soup is None:
        return None

    n_ratings = int(re.sub(r"\D", "", n_ratings_soup.text))

    if n_ratings <= 0:
        return None

    title = get_item_title(item_review_soup)

    if title is None:
        return None

    stars_rating_table_soup = stars_info_soup.find("table")

    if stars_rating_table_soup is None:
        return None

    star_list = [
        link.text.strip()
        for link in stars_rating_table_soup.findAll("a")
        if link.text.strip() != ""
    ]

    star_numbers = {
        **DEFAULT_COUNT,
        **dict(
            [
                (
                    STAR_NAME_TO_STAR_TYPE[star_name],
                    math.floor(int(re.sub(r"\D", "", percent)) * n_ratings / 100),
                )
                for star_name, percent in zip(star_list[::2], star_list[1::2])
            ]
        ),
    }

    return {
        "name": title,
        "genre": genre,
        "asin": asin,
        "n_ratings": n_ratings,
        "top_n": top_n,
        **star_numbers,
    }


def get_item_reviews(
    item_soup: BeautifulSoup,
    genre: str,
    asin: str,
) -> Optional[List[ItemReview]]:

    title = get_item_title(item_soup)

    if title is None:
        return None

    comments_table_soup = item_soup.find(id=PRODUCT_COMMENTS_CONTAINER_ID)

    if comments_table_soup is None:
        return None

    comments_divs = comments_table_soup.findAll(class_=PRODUCT_COMMENT_CSS)

    comments_info = (
        *map(
            lambda soup: get_comment_info(
                soup, asin=asin, genre=genre, book_name=title
            ),
            comments_divs,
        ),
    )

    return list(filter(lambda info: info is not None, comments_info))


def get_comment_helpful_n(comment_soup) -> int:
    helpful_soup = comment_soup.find("span", class_=COMMENT_HELPFUL_SPAN_CSS)

    if helpful_soup is None:
        return 0

    helpful_str = helpful_soup.text.split()[0].lower()

    return 1 if helpful_str == "one" else int(re.sub("\D", "", helpful_str))


def get_comment_info(
    comment_soup: BeautifulSoup,
    genre: str,
    book_name: str,
    asin: str,
) -> Optional[ItemReview]:

    text_soup = comment_soup.find("span", class_=COMMENT_TEXT_SPAN_CSS)

    if text_soup is None:
        return None

    text = text_soup.span.text.strip()

    star_soup = comment_soup.find("span", class_=COMMENT_STAR_SPAN_CSS)

    if star_soup is None:
        return None

    star = int(star_soup.text.split(".")[0])

    helpful_n = get_comment_helpful_n(comment_soup)

    return {
        "star": star,
        "helpful_n": helpful_n,
        "text": text,
        "genre": genre,
        "asin": asin,
        "book_name": book_name,
    }
