import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def scrape_bhoot_fm(year_url, scraped_links=None):
    if scraped_links is None:
        scraped_links = set()
    
    response = requests.get(year_url)
    
    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        
        month_content_divs = soup.find_all('div', {'class': 'box-month-content'})
        
        for div in month_content_divs:
            a_tags = div.find_all('a')
            for a_tag in a_tags:
                href = a_tag.get('href')
                if href:
                    if not bool(urlparse(href).netloc):
                        href = urljoin('https://bhoot-fm.com', href)
                    if href not in scraped_links:
                        scraped_links.add(href)
                        pagination_links = soup.find_all('a', {'class': 'page-numbers'})
                        for link in pagination_links:
                            href = link.get('href')
                            if href:
                                if not bool(urlparse(href).netloc):
                                    href = urljoin('https://bhoot-fm.com', href)
                                scrape_bhoot_fm(href, scraped_links)

def scrape_download_links(scraped_links):
    mediafire_links = []
    bhoot_fm_links = []
    
    for link in scraped_links:
        response = requests.get(link)
        
        if response.status_code == 200:
            page_content = response.content
            soup = BeautifulSoup(page_content, 'html.parser')
            
            a_tags = soup.find_all('a', {'class': 'btn btn-lg btn-primary btn-block'})
            
            for a_tag in a_tags:
                href = a_tag.get('href')
                if href:
                    if not bool(urlparse(href).netloc):
                        href = urljoin('https://bhoot-fm.com', href)
                    if 'mediafire' in href:
                        mediafire_links.append(href)
                    elif 'dl.bhoot-fm.com' in href:
                        bhoot_fm_links.append(href)
    
    return mediafire_links + bhoot_fm_links

if __name__ == "__main__":
    scraped_links = set()
    for year in range(2010, 2019):
        year_url = f'https://bhoot-fm.com/archives.php#year-{year}'
        scrape_bhoot_fm(year_url, scraped_links)
    
    download_links = scrape_download_links(list(scraped_links))
    
    with open('bhootfm-archives.txt', 'w') as file:
        for link in download_links:
            file.write('%s\n' % link)
    
    print("scraping done.")