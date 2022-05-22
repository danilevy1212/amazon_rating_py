import logging
import time
import random
from constants import BASE_URL, HEADERS, THROTTLE_RATE, Uri
from typing import Dict, Optional
from bs4 import BeautifulSoup
from requests import get

log = logging.getLogger('urllib3')
log.setLevel(logging.DEBUG)

def run_request(uri: Uri,
                params: Dict[str, str] = {},
                headers: Dict[str, str] = HEADERS,
                base_url: str = BASE_URL) -> Optional[BeautifulSoup]:
   """Make a request to Amazon and return the soupified html.
   """
   time.sleep(random.randrange(THROTTLE_RATE, 400) / 1000)

   raw_response = get(base_url + uri, params=params, headers=headers)

   return BeautifulSoup(raw_response.text, 'lxml')
