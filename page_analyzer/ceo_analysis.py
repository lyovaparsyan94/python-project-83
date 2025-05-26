from bs4 import BeautifulSoup


def get_ceo(response_text):
    soup = BeautifulSoup(response_text, 'html.parser') 
    title = str(soup.title.string) if soup.title else ''

    h1 = str(soup.h1.string) if soup.h1 else ''

    meta_tag = soup.find('meta', attrs={'name': 'description'})
    desc = str(meta_tag.get('content')) if meta_tag else ''

    return h1, title, desc