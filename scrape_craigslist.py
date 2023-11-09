from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import time 
import re
import random

# Variables
wages = []

# Function to open a URL in a browser window using Selenium
def open_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    return driver

# Function to parse HTML using BeautifulSoup and find all meta divs
def parse_html_meta(driver):
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup.find_all('div', {'class': 'meta'})

# Function to find and print the meta divs with a dollar sign
def extract_wages_from_page(meta_divs):
    # Loop through all meta divs
    for div in meta_divs:
        if div.find('span', {'class': 'separator'}):
            text_content = div.get_text()
            text_content = text_content.lower()

            # Differentiate between hourly, weekly, monthly, and yearly wages
            if '$' in text_content:
                text_content = re.sub(r'^.*?\$', '$', text_content)
                listing_wage = find_numbers_after_dollar_sign(text_content)
                if listing_wage is None:
                    continue
                if "hr" in text_content or "hour" in text_content:
                    # print("Hourly wage found in : ", text_content)
                    wages.append(listing_wage * 8)
                elif "week" in text_content:
                    # print("Weekly wage found in : ", text_content)
                    wages.append(listing_wage / 5)
                elif "month" in text_content:
                    # print("Monthly wage found in : ", text_content)
                    wages.append(listing_wage / 30)
                elif "year" in text_content:
                    # print("Yearly wage found in : ", text_content)
                    wages.append(listing_wage / 365)
                else:
                    # print("Dollar sign found in : ", text_content)
                    if isinstance(listing_wage, int) and listing_wage > 500:
                        # print("Wage is too high, skipping...")
                        continue
                    else:
                        wages.append(find_numbers_after_dollar_sign(text_content)) 
                    
# Function to find numbers after a dollar sign in a string
def find_numbers_after_dollar_sign(string):
    string = string.replace(",", "")
    pattern = "\$(\d+)"
    match = re.search(pattern, string)
    return int(match.group(1)) if match else None

# Scroll page randomizer
def scroll_page_randomizer(total_height, driver):
    # Scroll the page in increments of 5 pixels until 40% of the page 
    # has been scrolled
    for i in range(1, total_height, int(random.uniform(5, 10))):
        if i / total_height <= 0.95:
            driver.execute_script("window.scrollTo(0, {});".format(i))
            
            time.sleep(random.uniform(0.005, 0.008))


def non_human_parsing(driver):
    # Parse the HTML and find meta divs
    meta_divs = parse_html_meta(driver)

    # Find and print the meta divs with a dollar sign
    extract_wages_from_page(meta_divs)

def human_parsing_succeed(driver):
    # Scroll the page randomly
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    scroll_page_randomizer(total_height, driver)
    time.sleep(random.uniform(1, 2))

    # Parse the HTML and find meta divs
    meta_divs = parse_html_meta(driver)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find and print the meta divs with a dollar sign
    extract_wages_from_page(meta_divs)

    time.sleep(random.uniform(1, 2)) 
            

def human_parsing_error(driver):
    # Parse the HTML and find meta divs
    meta_divs = parse_html_meta(driver)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find and print the meta divs with a dollar sign
    extract_wages_from_page(meta_divs)

    # Get all links and extracts hrefs
    links = soup.find_all(class_="posting-title")
    hrefs = [link.get('href') for link in links]

    # Shuffle links and pick 2
    random.shuffle(hrefs)
    if len(hrefs) > 2:
        random_links = random.sample(hrefs, 2)

        # Scroll randomly through the page
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        scroll_page_randomizer(total_height, driver)

        for link in random_links:
            #Go to specific random listing
            driver.get(link)
            
            total_height = int(driver.execute_script("return document.body.scrollHeight"))
            
            scroll_page_randomizer(total_height, driver)
            # Wait between 3-6 seconds, and then return to the previous page (listings)
            time.sleep(random.uniform(3, 6))
        
            driver.execute_script("window.history.go(-1)")

            total_height = int(driver.execute_script("return document.body.scrollHeight"))
            scroll_page_randomizer(total_height, driver)

            time.sleep(random.uniform(3, 5))
    else:
        return

def main():
    control = 1
    # Set the URL to the gigs section of Craigslist Boston
    url = "https://boston.craigslist.org/search/ggg#search=1~thumb~0~2"

    # Open the URL in a browser window
    driver = open_url(url)

    while control < 2:
        
        # Test to see if the page is pulling properly
        # non_human_parsing(driver)
        human_parsing_succeed(driver)

        # Check next pages
        next_buttons = driver.find_elements(By.CLASS_NAME, 'cl-next-page')

        if len(next_buttons) > 0:
            last_button = next_buttons[-1] # Gets the last element in the button list
            actions = ActionChains(driver)
            actions.move_to_element(last_button).perform() # Move to the last button

            if 'bd-disabled' not in last_button.get_attribute("class").split():
                actions.click(last_button).perform()  # Click the last button if it's not disabled
            else:
                # Breaks out of the loop, done
                control = 2
        else:
            # Breaks out of the loop, done
            control = 2

    print("This is the total amount of money you could make: $", round(sum(wages), 2))

if __name__ == "__main__":
    main()
