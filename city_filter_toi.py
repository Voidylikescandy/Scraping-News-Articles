import requests
from bs4 import BeautifulSoup

base_url = 'https://timesofindia.indiatimes.com/city/hyderabad'

# Extract headlines from a given page
def extract_headlines_from_page(url, page_num):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    headlines_list = []

    if page_num <= 20:
        # Find all divs with class starting with 'col_l_4'
        news_divs = soup.find_all('div', class_=lambda class_: class_ and class_.startswith('col_l_4'))

        for news_div in news_divs:
            link_tag = news_div.find('a')
            if link_tag:
                # Different logic for Page 1 vs Page 2 onwards
                if page_num == 1:
                    # Page 1 logic: Headline is inside a <span> inside the <a>
                    headline_span = link_tag.find('span')
                    if headline_span:
                        headline_text = headline_span.get_text(strip=True)
                        article_url = link_tag['href']
                        if article_url.startswith('/'):
                            article_url = 'https://timesofindia.indiatimes.com' + article_url
                        headlines_list.append((headline_text, article_url))
                else:
                    # Page 2-20 logic: Headline is inside the 4th div (index 3 in the list of divs)
                    inner_divs = link_tag.find_all('div')
                    if len(inner_divs) > 3:
                        headline_div = inner_divs[3]  # The 4th div contains the headline
                        headline_text = headline_div.get_text(strip=True)
                        article_url = link_tag['href']
                        if article_url.startswith('/'):
                            article_url = 'https://timesofindia.indiatimes.com' + article_url
                        headlines_list.append((headline_text, article_url))
    elif page_num > 20:
        # Page 21 onwards: First find <ul> with class 'list5 clearfix'
        ul_tag = soup.find('ul', class_='list5 clearfix')
        if ul_tag:
            # Extract all <li> elements inside this <ul>
            news_list_items = ul_tag.find_all('li')
            for news_item in news_list_items:
                span_tag = news_item.find('span', class_='w_tle')
                if span_tag:
                    link_tag = span_tag.find('a')
                    if link_tag:
                        headline_text = link_tag.get_text(strip=True)
                        article_url = link_tag['href']
                        if article_url.startswith('/'):
                            article_url = 'https://timesofindia.indiatimes.com' + article_url
                        headlines_list.append((headline_text, article_url))

    return headlines_list

# Extract headlines from multiple pages
def extract_headlines_from_multiple_pages(num_pages):
    all_headlines = []

    for page_num in range(1, num_pages + 1):
        if page_num == 1:
            url = base_url
        else:
            url = f'{base_url}/{page_num}'

        print(f"Extracting headlines from: {url}")
        headlines = extract_headlines_from_page(url, page_num)

        all_headlines.extend(headlines)

    return all_headlines

# Helper function to filter headlines based on keywords
def filter_headlines_by_keywords(headlines_data, keywords):
    filtered_headlines = []

    for headline, url in headlines_data:
        if any(keyword.lower() in headline.lower() for keyword in keywords):
            filtered_headlines.append((headline, url))

    return filtered_headlines

# Specify the number of pages you want to scrape
num_pages_to_scrape = 30
headlines_data = extract_headlines_from_multiple_pages(num_pages_to_scrape)

keywords_list = ['congress', 'govt', 'government']

filtered_headlines = filter_headlines_by_keywords(headlines_data, keywords_list)

print(f"\nExtracted {len(filtered_headlines)} filtered headlines based on keywords:\n")
for idx, (headline, url) in enumerate(filtered_headlines, 1):
    print(f"{idx}. {headline}")
    print(f"   URL: {url}\n")
