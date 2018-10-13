def scrape():
    # Dependencies
    import re
    import os
    from bs4 import BeautifulSoup
    import requests
    from splinter import Browser
    from splinter.exceptions import ElementDoesNotExist
    import pandas as pd
    import time

    scrape = {}

    mars_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    response = requests.get(mars_url)
    mars_soup = BeautifulSoup(response.text,'html.parser')
    #print(soup.prettify())

    mars_results = mars_soup.find_all('div',class_='slide')[0]

    news_title = mars_results.find('div', class_='content_title').text
    news_p = mars_results.find('div', class_='rollover_description_inner').text

    scrape['news_title'] = news_title
    scrape['news_p'] = news_p

    jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    #Set up splinter
    browser = Browser('chrome')
    browser.visit(jpl_url)
    html = browser.html
    jpl_soup = BeautifulSoup(html, 'html.parser')
    time.sleep(5)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(20)

    html = browser.html
    jpl_img_soup = BeautifulSoup(html, 'html.parser')
    image = jpl_img_soup.find('img', class_='fancybox-image')
    image_url = image['src']
    full_url = 'https://www.jpl.nasa.gov' + image_url

    scrape['jpl_url'] = full_url

    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    response = requests.get(twitter_url)
    tw_soup = BeautifulSoup(response.text, 'html.parser')
    mars_weather=tw_soup.find(string=re.compile("Sol"))

    scrape['weather'] = mars_weather

    facts_url = 'http://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    df = tables[0]
    df.columns = ['','Value']
    df.set_index('')
    html_table = df.to_html()

    scrape['table'] = html_table

    mars_hemis_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    mars_hemis_base_url = 'https://astrogeology.usgs.gov'
    browser.visit(mars_hemis_url)
    time.sleep(5)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    titles = soup.find_all('h3')

    mars_hemis_imgs = soup.find_all('div', class_='description')
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    titles = soup.find_all('h3')

    mars_hemis_imgs = soup.find_all('div', class_='description')

    mars_hemis_list = []
    for x in range(len(mars_hemis_imgs)):
        mars_hemis_url = mars_hemis_imgs[x].find('a').get('href')
        mars_hemis_list.append(mars_hemis_base_url + mars_hemis_url)

    image_urls = []
    for hemi_url in mars_hemis_list:
        browser.visit(hemi_url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('div', class_='downloads'):
            image_urls.append(link.find_all('a')[1].get('href'))

    hemisphere_image_urls = []
    for title, img_url in zip(titles, image_urls):
        hemisphere_image_urls.append({'title': title,
                                    'img_url': img_url})

    scrape['hemis'] = hemisphere_image_urls

    return scrape