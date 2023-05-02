import os
import json
import time
from tqdm import tqdm
from requests import get
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

USER_AGENT = \
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.37"


def scrape_review_page(review_url):
    # Takes a URL pointing to a review page, and returns the text content of that review as a string

    # Keep iterating until we get a successful GET response. Could be unsuccessful because either:
    # (i) get a status code that is not 200, most likely 403
    # (ii) get an apparently successful 200 status code, but still get sent a zero-sized content
    successful_response = False
    while not successful_response:

        response = get(review_url, headers={'User-Agent': USER_AGENT})  # User-Agent might help avoid getting blocked

        if response.status_code == 200:
            if response.text == "0":
                # Even though successful status code, invalid request response
                print("Get request returned zero-sized content. Sleeping 30 seconds and trying again...")
                time.sleep(30)
            else:
                successful_response = True
        else:
            print("Get request blocked (%s). Sleeping 30 seconds and trying again..." % str(response.status_code))
            time.sleep(30)

    # Sleep a little to avoid getting blocked
    time.sleep(10)

    html_soup = BeautifulSoup(response.text, 'html.parser')

    review_div = html_soup.find('div', class_='reviewContent')

    return review_div.text


def scrape_band_page(band_name):
    # Takes a band name e.g. 'Slayer' (with optional unique identifier number e.g. 'Slayer/72') and returns:
    # (i) basic information about the band, and (ii) all the reviews of all the bands' releases as a list of strings

    # Using `requests.get` will not get the dynamic information we need about reviews
    # Need to use Selenium to dynamically click on 'Reviews' button, and then extract page source for parsing

    band_url = 'https://www.metal-archives.com/bands/%s' % band_name

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    driver.get(band_url)

    # Find 'REVIEWS' tab element and dynamically click it
    # Sleep a couple times to make sure (i) element is click-able, and (ii) reviews loaded
    # If there is no reviews tab, it will click another tab (the 3rd in the list), e.g. 'Similar Artists',
    # so we need to do the check for no reviews later on
    reviews_element = driver.find_element(By.XPATH, '//*[@id="band_tabs"]/ul/li[3]')
    time.sleep(5)
    reviews_element.click()
    time.sleep(5)

    # Extract dynamic page source then parse into BeautifulSoup
    page_source = driver.page_source
    html_soup = BeautifulSoup(page_source, 'html.parser')

    # Create a dictionary storing basic information about the band, e.g. 'Genre' -> 'Death/Groove Metal'
    band_info = {}

    for description_list in html_soup.find_all('dl'):
        for description_term, description_value in zip(description_list.find_all('dt'), description_list.find_all('dd')):
            band_info[description_term.text] = description_value.text

    # Create a list of strings, each a review about anything the band released
    band_reviews = []

    # Find if there are reviews
    has_reviews = html_soup.find('div', id='band_reviews') is not None

    # Only do _all_ of the following if there were reviews found
    if has_reviews:

        band_reviews_table = html_soup.find('div', id='band_reviews').tbody
        band_reviews_table_rows = band_reviews_table.find_all('tr')
        for review_row_index in tqdm(range(len(band_reviews_table_rows))):
            band_review = band_reviews_table_rows[review_row_index]
            band_reviews.append(scrape_review_page(band_review.a['href']))

        # If reviews are split over multiple pages, keep clicking through dynamically and parsing like above,
        # appending reviews to the same `band_reviews` list

        # Find the next review page click-able arrow button, an <a> tag:
        # - if `class` of <a> tag is exactly 'next paginate_button', it is click-able,
        # - otherwise it will exactly be `next paginate_button paginate_button_disabled`, and not click-able.
        # Therefore if `next_reviews_button` is not None, reviews split over multiple click-able tabs to iterate over
        next_reviews_button = html_soup.find('a', class_='next paginate_button')
        if next_reviews_button is not None:

            # Keep looping until the next review page button is no longer click-able
            while next_reviews_button is not None:

                # Click the next review page button in driver
                next_review_page_element = driver.find_element(By.XPATH, '//*[@id="reviewList_next"]')
                time.sleep(5)
                next_review_page_element.click()
                time.sleep(5)

                # Get the latest dynamically generated page source and parse
                page_source = driver.page_source
                html_soup = BeautifulSoup(page_source, 'html.parser')

                # Copy of code above, to parse the reviews for this new page source
                band_reviews_table = html_soup.find('div', id='band_reviews').tbody
                band_reviews_table_rows = band_reviews_table.find_all('tr')
                for review_row_index in tqdm(range(len(band_reviews_table_rows))):
                    band_review = band_reviews_table_rows[review_row_index]
                    band_reviews.append(scrape_review_page(band_review.a['href']))

                next_reviews_button = html_soup.find('a', class_='next paginate_button')
    else:
        print("%s has no reviews" % band_name)

    # Quit browser before returning from function
    driver.quit()

    band_info['Number of Reviews'] = len(band_reviews)

    return {
        'Band Information': band_info,
        'Band Reviews': band_reviews
    }


def scrape_specific_bands(list_of_bands):
    # `list_of_bands` is a list of pairs: (band ID for url, band name for saving to a json file)
    # e.g. one element could be ('Slayer/72', 'slayer')

    for band_id, band_name in list_of_bands:

        if os.path.exists('band_data/%s.json' % band_name):
            print("%s ALREADY EXISTS - SKIPPING" % band_name.upper())
            continue

        band_data = scrape_band_page(band_id)

        with open('band_data/%s.json' % band_name, 'w') as open_f:
            json.dump(band_data, open_f, indent=4)

        print("%s PROCESSED" % band_name.upper())
        time.sleep(1000)


if __name__ == '__main__':

    # TODO: OUTDATED - CURRENTLY UN-EXECUTABLE BECAUSE CHROME/SELENIUM VERSION MISMATCH!!!

    scrape_specific_bands([
        ('1914/3540396156', '1914')
    ])
