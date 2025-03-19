from bs4 import BeautifulSoup


def get_data(response):
    soup = BeautifulSoup(response.text, "lxml")
    data = {}

    h1_tag = soup.h1.string if soup.h1 else None
    title_tag = soup.title.string if soup.title else None
    description_tag = soup.find('meta', {'name': 'description'})

    data['h1'] = h1_tag
    data['title'] = title_tag
    data['description'] = description_tag.get('content') if description_tag else None #noqa

    return data
