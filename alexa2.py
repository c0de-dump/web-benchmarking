from bs4 import BeautifulSoup
import requests


def _elicit_website_from_response(res: str):
    output = []
    parsed_res = BeautifulSoup(res, "html.parser")
    tables = parsed_res.find_all('table')
    main_table = tables[0]
    table_body = main_table.find('tbody')
    for tr in table_body.find_all('tr'):
        tds = tr.find_all('td')
        website = str(tds[2].find('a').contents[0]).strip()
        output.append(website)
    return output


def get_websites():
    urls = ["https://ahrefs.com/top"] + [
        f"https://ahrefs.com/top/{i}" for i in range(2, 10 + 1)
    ]

    websites = []
    for url in urls:
        res = requests.get(url)
        websites.extend(_elicit_website_from_response(res.content))

    return set(websites)


if __name__ == '__main__':
    print(get_websites())
