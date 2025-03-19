from bs4 import BeautifulSoup


def get_data(content):
    soup = BeautifulSoup(content.text, "lxml")
    data = {}

    h1_tag = soup.h1.string if soup.h1 else None
    title_tag = soup.title.string if soup.title else None
    description_tag = soup.find('meta', {'name': 'description'}).get('content')

    data['h1'] = h1_tag
    data['title'] = title_tag
    data['description'] = description_tag if description_tag else None

    return data
