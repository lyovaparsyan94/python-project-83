from bs4 import BeautifulSoup


def get_data(response):
    parsed_content = BeautifulSoup(response.text, "lxml")
    result = {}

    heading = parsed_content.h1.string if parsed_content.h1 else None
    page_title = parsed_content.title.string if parsed_content.title else None
    meta_description = parsed_content.find('meta', {'name': 'description'})

    result['h1'] = heading
    result['title'] = page_title
    result['description'] = meta_description.get('content') \
        if meta_description else None

    return result