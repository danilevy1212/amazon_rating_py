from typing import FrozenSet, NewType, TypedDict

## Types
# URI path
Uri = NewType("Uri", str)

# ASIN Identifier
Asin = NewType("Asin", str)


class ItemRatingStatistics(TypedDict):
    genre: str
    name: str
    asin: str
    n_ratings: int
    top_n: int
    one_star: int
    two_star: int
    three_star: int
    four_star: int
    five_star: int


class ItemReview(TypedDict):
    genre: str
    book_name: str
    asin: str
    star_value: int
    text: str
    n_helpful: int


STAR_NAME_TO_STAR_TYPE = {
    "5 star": "five_star",
    "4 star": "four_star",
    "3 star": "three_star",
    "2 star": "two_star",
    "1 star": "one_star",
}

DEFAULT_COUNT = {
    "five_star": 0,
    "four_star": 0,
    "three_star": 0,
    "two_star": 0,
    "one_star": 0,
}

## Constants
# Amazon main URL, of which each request is going to be made of.
BASE_URL = "https://www.amazon.com"

# URI for the list of best sellers.
BEST_SELLERS = Uri("/Best-Sellers/zgbs/")

# URI for a product review. Contains a slot for the product `asin`.
PRODUCT_REVIEWS = Uri("/product-reviews/{asin}/ref=dp_cr_pr_redirect")

# Header contents of the requests
HEADERS = {
    "authority": "www.amazon.com",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-dest": "document",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
}

# Rate in ms before being allowed to make another request.
THROTTLE_RATE = 200

# ID for the list of departments.
TREE_ID = "zg_browseRoot"

# Books category name
BOOKS_DEPARTMENTS_NAME = "Books"

# ID for the list of items.
ITEM_LIST_ID = "zg-ordered-list"

# CSS for an item.
ITEM_CSS = "a-list-item"

# CSS for the rank of a item.
ITEM_RANK_CSS = "zg-badge-text"

# Categories BlackList
BOOKS_CATEGORIES_BLACKLIST = frozenset(
    [
        "Arts & Photography",
        "Books on CD",
        "Calendars",
        "Cookbooks, Food & Wine",
        "Crafts, Hobbies & Home",
        "Deals in Books",
        "Libros en español",
        "Literature & Fiction",
        "Test Preparation",
        "Reference",
    ]
)

# Categories BlackList
BOOKS_CATEGORIES_WHITELIST = frozenset(
    [
        "Comics & Graphic Novels",
        "Children's Books",
        "Law",
        "Christian Books & Bibles",
        "Teens",
        "History",
        "Lesbian, Gay, Bisexual & Transgender Books",
        "Romance",
        "Engineering & Transportation",
        "Mystery, Thriller & Suspense",
    ]
)

# CSS class of link to product review
ITEM_PRODUCT_REVIEW_CSS = "a-size-small a-link-normal"

# Item limit per category
ITEM_LIMIT = 50

# Review Product Info ID
PRODUCT_REVIEW_INFO_ID = "cm_cr-product_info"

# Reviews Average Star CSS class
PRODUCT_REVIEW_AVERAGE_STAR_CSS = "a-size-medium a-color-base"

# Rating numbers CSS
PRODUCT_REVIEW_NUMBER_RATINGS_CSS = "a-size-base a-color-secondary"

# Title Header CSS
PRODUCT_REVIEW_HEADER_CSS = "a-size-large a-text-ellipsis"

# ID of the comments container
PRODUCT_COMMENTS_CONTAINER_ID = "cm_cr-review_list"

# Product comment CSS class
PRODUCT_COMMENT_CSS = "a-section review aok-relative"

# Comment star CSS class
COMMENT_STAR_SPAN_CSS = "a-icon-alt"

# Comment text CSS class
COMMENT_TEXT_SPAN_CSS = "a-size-base review-text review-text-content"

# Comment helpful CSS class
COMMENT_HELPFUL_SPAN_CSS = "a-size-base a-color-tertiary cr-vote-text"
