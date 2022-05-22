import logging
import csv
from itertools import chain
from urllib import parse
from soup_parser import (
    get_best_sellers_tree,
    get_child_uri,
    get_childrens_name_uris,
    get_item_review_statistics,
    get_item_reviews,
    get_items,
    remove_childs,
    remove_childs_whitelist,
)
from engine import run_request
from typing import List, Optional, Tuple, Dict
from constants import (
    BEST_SELLERS,
    BOOKS_DEPARTMENTS_NAME,
    ItemRatingStatistics,
    ItemReview,
    Uri,
)


def get_book_department_uri() -> Optional[Uri]:
    """Get the URI for the `Books` department."""
    best_sellers_soup = run_request(BEST_SELLERS)

    if best_sellers_soup is None:
        logging.error(f"Could not extract soup from {BEST_SELLERS}.")
        return None

    department_tree = get_best_sellers_tree(best_sellers_soup)

    if department_tree is None:
        logging.error(f"Could not find the departments in soup.")
        return None

    departments_uri = get_childrens_name_uris(department_tree)

    if departments_uri is None:
        logging.error(f"Could not get the departments list.")
        return None

    return get_child_uri(departments_uri, BOOKS_DEPARTMENTS_NAME)


def get_books_categories_uri(use_blacklist=False) -> Optional[List[Tuple[str, Uri]]]:
    """Get a list of books categories and their `Uri`."""
    books_uri = get_book_department_uri()

    if books_uri is None:
        logging.error(f"The {BOOKS_DEPARTMENTS_NAME} couldn't be found.")
        return None

    best_sellers_books = run_request(books_uri)

    if best_sellers_books is None:
        logging.error(f"The uri {books_uri} did not fetch the books soup.")
        return None

    department_tree = get_best_sellers_tree(best_sellers_books)

    if department_tree is None:
        logging.error(f"Could not find the departments in soup.")
        return None

    categories = get_childrens_name_uris(department_tree)

    if categories is None:
        logging.error(f"Could not find the categories of the books department.")
        return None

    if use_blacklist:
        return remove_childs(categories)

    return remove_childs_whitelist(categories)


def uri_items(category_uri: Uri) -> Optional[List[Tuple[int, Uri]]]:
    items_soup = run_request(category_uri)

    if items_soup is None:
        logging.error(f"Could not fetch {category_uri}.")
        return None

    return get_items(items_soup)


def uri_review_statistics(
    review_uri: Uri, genre: str, top_n: int
) -> Optional[ItemRatingStatistics]:

    review_soup = run_request(review_uri)

    if review_soup is None:
        logging.error(f"Could not fetch {review_soup}.")
        return None

    return get_item_review_statistics(
        review_soup, review_uri.split("/")[2], genre, top_n
    )


def get_category_ratings(
    category_name: str, category_uri: Uri
) -> Optional[List[ItemRatingStatistics]]:
    items = uri_items(category_uri)

    if items is None:
        logging.error(f"Could not get items for category {category_name}")
        return None

    items_ratings = []

    for top_n, item_uri in items:
        print(top_n, item_uri)

        item_rating = uri_review_statistics(item_uri, category_name, top_n)

        print(item_rating)

        if item_rating is None:
            logging.error(f"Could not get statistics for {item_uri}")
            continue

        items_ratings.append(item_rating)

    return items_ratings


def get_categories_ratings():
    categories_uri = get_books_categories_uri()

    if categories_uri is None:
        return

    categories_ratings = []

    for category_name, category_uri in categories_uri:
        category_rating = get_category_ratings(category_name, category_uri)

        if category_rating is None or len(category_rating) <= 0:
            logging.error(f"Could not get items of {category_rating}")
            continue

        categories_ratings.extend(category_rating)

    return categories_ratings


def product_review_uri(asin: str) -> Uri:
    return Uri(f"/product-reviews/{asin}")


def uri_add_params(product_uri: Uri, params: Dict[str, str]) -> Uri:
    return Uri(f"{product_uri}/?{parse.urlencode(params)}")


def asin_to_uris(asin: str, genre: str) -> List[Tuple[Uri, str, str]]:
    review_uri = product_review_uri(asin)

    return [
        (uri_add_params(review_uri, dict(filterByStar="critical")), asin, genre),
        (uri_add_params(review_uri, dict(filterByStar="positive")), asin, genre),
    ]


def uris_from_asin(asins: List[Tuple[str, str]]) -> List[Tuple[Uri, str, str]]:
    return list(
        chain.from_iterable(list(map(lambda x: asin_to_uris(x[0], x[1]), asins)))
    )


def item_review_from_triple(
    uri_asin_genre: Tuple[Uri, str, str]
) -> Optional[List[ItemReview]]:
    item_soup = run_request(uri_asin_genre[0])

    if item_soup is None:
        return None

    return get_item_reviews(item_soup, uri_asin_genre[1], uri_asin_genre[2])


def dump_categories_to_csv(categories_ratings):
    with open("books.csv", "w", newline="") as ratings_file:
        dict_writer = csv.DictWriter(ratings_file, categories_ratings[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(categories_ratings)
