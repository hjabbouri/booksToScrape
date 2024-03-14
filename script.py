import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://books.toscrape.com'

# TODO: 518 out of 1000, next pages book


def get_books(categories) -> dict:
    books_dict = {}
    for row in categories.findAll('li'):
        if row.a.text.strip() != 'books':
            book = {}
            book[row.a.text.strip()] = row.a['href']
            books_dict[row.a.text.strip()] = row.a['href']
    return books_dict


def get_book_info(url):
    req = requests.get(url)
    sub_soup = BeautifulSoup(req.content, 'html5lib')\
        .find('article', attrs={'class': 'product_page'})
    info = {}
    row = sub_soup.find('div', attrs={'class': 'col-sm-6 product_main'})
    info['Name'] = row.find('h1').text.replace(',', ' ')
    info['Price'] = row.find('p', attrs={'class': 'price_color'}).text[1:]
    text = row.find('p', attrs={'class': 'instock availability'})\
        .text.strip().split()
    info['Availability'] = (' '.join(text[0:2])).title()
    info['Quantity'] = text[2][1:].strip()
    # info['Description'] = sub_soup.find_all('p', recursive=False)[0]\
    # .text[:-8].strip() # ' "
    for table in sub_soup.findAll('tr'):
        if table.th.text.strip() != 'Availability':
            info[table.th.text.strip()] = table.td.text.strip()
    return info


req = requests.get(BASE_URL)

soup = BeautifulSoup(req.content, 'html5lib')

categories = soup.find('div', attrs={'class': 'side_categories'})

books_dict = get_books(categories)

header = 'Name,Category,Availability,Quantity,UPC,Price (excl. tax),\
Price (incl. tax),Tax,Number of reviews,URL\n'  # ,Description\n'

books_dict.pop('Books')

with open('data.csv', 'w+') as file:
    file.write(header)
    for key, val in books_dict.items():
        req = requests.get(BASE_URL + '/' + val)
        soup = BeautifulSoup(req.content, 'html5lib')
        for row in soup.findAll('article', attrs={'class': 'product_pod'}):
            book_url = BASE_URL + '/' + val + '/../' +\
                                row.h3.a['href']

            book_info = get_book_info(book_url)
            book_info['URL'] = book_url
            file.write(f'''{book_info['Name']},{key},{book_info['Availability']},\
{int(book_info['Quantity'])},{book_info['UPC']},\
{float(book_info['Price (excl. tax)'][1:])},\
{float(book_info['Price (incl. tax)'][1:])},\
{float(book_info['Tax'][1:])},\
{int(book_info['Number of reviews'])},{book_info['URL']},\
\n''')
# {book_info['Description']}
