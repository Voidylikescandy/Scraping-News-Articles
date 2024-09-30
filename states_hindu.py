import requests
from bs4 import BeautifulSoup

base_url = 'https://www.thehindu.com/news/national/telangana'

def extract_headlines_from_page(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    headlines_list = []

    news_divs = soup.find_all('div', class_='right-content')

    for news_div in news_divs:
        h3_tag = news_div.find('h3')
        if h3_tag:
            link_tag = h3_tag.find('a')
            if link_tag:
                headline_text = link_tag.get_text(strip=True)
                article_url = link_tag['href']
                headlines_list.append((headline_text, article_url))

    return headlines_list

def extract_headlines_from_multiple_pages(num_pages):
    all_headlines = []

    for page_num in range(1, num_pages + 1):
        if page_num == 1:
            url = base_url
        else:
            url = f'{base_url}/?page={page_num}'

        print(f"Extracting headlines from: {url}")
        headlines = extract_headlines_from_page(url)

        all_headlines.extend(headlines)

    return all_headlines

def filter_headlines_by_keywords(headlines_data, keywords):
    filtered_headlines = []

    for headline, url in headlines_data:
        if any(keyword.lower() in headline.lower() for keyword in keywords):
            filtered_headlines.append((headline, url))

    return filtered_headlines

def filter_headlines_by_all_keywords(headlines_data, keywords):
    filtered_headlines = []

    for headline, url in headlines_data:
        all_keywords_in_headline = all(keyword.lower() in headline.lower() for keyword in keywords)
        if all_keywords_in_headline:
            filtered_headlines.append((headline, url))

    return filtered_headlines

def extract_information_from_headlines(headlines):
    text_content = []

    for (headline, url) in headlines:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        article_body = soup.find('div', class_='articlebodycontent')

        for element in article_body.children:
            if element.name == 'p':
                text_content.append(element.get_text(strip=True))

            if element.name == 'div' and 'articleblock-container' in element.get('class', []):
                break
    
    return text_content

num_pages_to_scrape = 9
headlines_data = extract_headlines_from_multiple_pages(num_pages_to_scrape)

keywords_list = ['BJP', 'Warangal']

filtered_headlines = filter_headlines_by_keywords(headlines_data, keywords_list)

print(f"\nExtracted {len(filtered_headlines)} filtered headlines based on keywords:\n")
for idx, (headline, url) in enumerate(filtered_headlines, 1):
    print(f"{idx}. {headline}")
    print(f"   URL: {url}\n")

text_content = extract_information_from_headlines(filtered_headlines)

for text in text_content:
    print(text)
    print('-' * 100)