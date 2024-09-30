import requests
from bs4 import BeautifulSoup

base_url = 'https://www.deccanchronicle.com/southern-states/telangana'

def extract_headlines_from_page(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    headlines_list = []

    news_divs = soup.find_all('div', class_='col-lg-3 col-sm-6 grid-margin mb-5 mb-sm-2')

    for news_div in news_divs:
        h5_tag = news_div.find('h5')
        p_tag = news_div.find('p')
        if h5_tag and p_tag:
            link_tag = h5_tag.find('a')
            description = p_tag.get_text(strip=True).strip(".,")
            if link_tag:
                headline_text = link_tag.get_text(strip=True).strip(".")
                article_url = link_tag['href']
                if article_url.startswith('/'):
                    article_url = 'https://www.deccanchronicle.com' + article_url
                headlines_list.append((headline_text, article_url, description))

    return headlines_list

def extract_headlines_from_multiple_pages(num_pages):
    all_headlines = []

    for page_num in range(1, num_pages + 1):
        if page_num == 1:
            url = base_url
        else:
            url = f'{base_url}/{page_num}'

        print(f"Extracting headlines from: {url}")
        headlines = extract_headlines_from_page(url)

        all_headlines.extend(headlines)

    return all_headlines

def filter_headlines_by_keywords(headlines_data, keywords):
    filtered_headlines = []

    for headline, url, desc in headlines_data:
        if any(keyword.lower() in headline.lower() for keyword in keywords) or any(keyword.lower() in desc.lower() for keyword in keywords):
            filtered_headlines.append((headline, url, desc))

    return filtered_headlines

def filter_headlines_by_all_keywords(headlines_data, keywords):
    filtered_headlines = []

    for headline, url, desc in headlines_data:
        all_keywords_in_headline = all(keyword.lower() in headline.lower() for keyword in keywords)
        all_keywords_in_desc = all(keyword.lower() in desc.lower() for keyword in keywords)
        if all_keywords_in_headline or all_keywords_in_desc:
            filtered_headlines.append((headline, url, desc))

    return filtered_headlines

def is_substring(new_text, text_list):
    for existing_text in text_list:
        if new_text in existing_text or existing_text in new_text:
            return True
    return False

def extract_information_from_headlines(headlines):
    text_content = []

    for (headline, url, desc) in headlines:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_content = soup.find('div', class_='entry-main-content dropcap')

        # List of potential containers for text (paragraphs, divs, etc.)
        containers = main_content.find_all(['p', 'div'])

        for container in containers:
            text = container.get_text(separator='\n').strip()
            # Only append non-empty and non-overlapping text
            if text and not is_substring(text, text_content):
                text_content.append(text)

        unwanted_prefix = "Download the all new Deccan Chronicle app"

        text_content = [text for text in text_content if not text.startswith(unwanted_prefix)]
    
    return text_content

num_pages_to_scrape = 10
headlines_data = extract_headlines_from_multiple_pages(num_pages_to_scrape)

keywords_list = ['BJP', 'Warangal']

filtered_headlines = filter_headlines_by_keywords(headlines_data, keywords_list)

print(f"\nExtracted {len(filtered_headlines)} filtered headlines based on keywords:\n")
for idx, (headline, url, desc) in enumerate(filtered_headlines, 1):
    print(f"{idx}. {headline}")
    print(f"   URL: {url}")
    print(f"   Description: {desc}\n")

text_content = extract_information_from_headlines(filtered_headlines)

for text in text_content:
    print(text)
    print('-' * 100)
