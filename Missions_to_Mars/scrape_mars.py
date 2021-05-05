from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store in dictionary.
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }
    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Get first list item and wait half a second if not immediately present
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    try:
       sidebar = soup.find('ul', class_='item_list')
       categories = sidebar.find_all('li', class_='slide')
       title = categories[0].find('div', class_='content_title').text
       paragraph = categories[0].find('div', class_='article_teaser_body').text
    except AttributeError:
        return None, None
    return title, paragraph


def featured_image(browser):
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)
    # Click into the FULL IMAGE button on the page
    full_image_button = browser.find_by_tag("button")[1]
    full_image_button.click()
    # Parse HTML object with Beautiful Soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')
    # Find the tag and class that contains this specific image info-partitial url
    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None
    # Use the base url to create an absolute url
    featured_image_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return featured_image_url


def hemispheres(browser):
    # Visit hemispheres website through splinter module 
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    # HTML Object
    html_hemispheres = browser.html
    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html_hemispheres, 'html.parser')
    # Retreive all items that contain mars hemispheres information
    items = soup.find_all('div', class_='item')
    # Create empty list for hemisphere urls 
    hemisphere_image_urls = []
    # Store the main_ul 
    hemispheres_main_url = 'https://astrogeology.usgs.gov'
    # Loop through the items previously stored
    for i in items: 
        # Store title
        title = i.find('h3').text
        # Store link that leads to full image website
        partial_img_url = i.find('a', class_='itemLink product-item')['href']
        # Visit the link that contains the full image website 
        browser.visit(hemispheres_main_url + partial_img_url)
        # HTML Object of individual hemisphere information website 
        partial_img_html = browser.html
        # Parse HTML with Beautiful Soup for every individual hemisphere information website 
        soup = BeautifulSoup( partial_img_html, 'html.parser')
        # Retrieve full image source 
        img_url = hemispheres_main_url + soup.find('img', class_='wide-image')['src']
        # Append the retreived information into a list of dictionaries 
        hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
    return hemisphere_image_urls


def mars_facts():
    try:
        url = 'https://space-facts.com/mars/'
        df = pd.read_html(url)[0]
    except BaseException:
        return None
    df.columns = ["Description", "Value"]
    df.set_index("Description", inplace=True)
    # Add some bootstrap styling to <table>
    # print(df)
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
    # print(mars_facts())