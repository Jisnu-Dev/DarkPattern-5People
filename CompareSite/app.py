from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'}


def get_flipkart_price(name):
    try:
        name1 = name.replace(" ", "+")
        url = f'https://www.flipkart.com/search?q={name1}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        if soup.select('._4rR01T'):
            flipkart_name = soup.select('._4rR01T')[0].getText().strip().upper()
            if name.upper() in flipkart_name:
                flipkart_price = soup.select('._30jeq3')[0].getText().strip()
                return flipkart_price
        elif soup.select('.s1Q9rs'):
            flipkart_name = soup.select('.s1Q9rs')[0].getText().strip().upper()
            if name.upper() in flipkart_name:
                flipkart_price = soup.select('._30jeq3')[0].getText().strip()
                return flipkart_price
        else:
            return '0'
    except:
        return '0'


def get_amazon_price(name):
    try:
        name1 = name.replace(" ", "-")
        name2 = name.replace(" ", "+")
        url = f'https://www.amazon.in/{name1}/s?k={name2}'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        amazon_page = soup.select('.a-color-base.a-text-normal')
        amazon_page_length = int(len(amazon_page))

        for i in range(0, amazon_page_length):
            name = name.upper()
            amazon_name = soup.select('.a-color-base.a-text-normal')[i].getText().strip().upper()
            if name in amazon_name:
                amazon_price = soup.select('.a-price-whole')[i].getText().strip().upper()
                return amazon_price
                break
            else:
                i += 1
                i = int(i)
                if i == amazon_page_length:
                    return '0'
                    break
    except:
        return '0'


def convert_price(a):
    b = a.replace(" ", '')
    c = b.replace("INR", '')
    d = c.replace(",", '')
    f = d.replace("₹", '')
    g = int(float(f))
    return g


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_name = request.form['product_name']
        flipkart_price = get_flipkart_price(product_name)
        amazon_price = get_amazon_price(product_name)

        if flipkart_price == '0':
            flipkart_price = int(flipkart_price)
        else:
            flipkart_price = convert_price(flipkart_price)

        if amazon_price == '0':
            amazon_price = int(amazon_price)
        else:
            amazon_price = convert_price(amazon_price)

        min_price = min(flipkart_price, amazon_price)

        if min_price == 0:
            result_message = "No relative product found on both websites...."
        else:
            result_message = f"Minimum Price: ₹ {min_price}"

        price_urls = {
            f'{amazon_price}': f'https://www.amazon.in/{product_name.replace(" ", "-")}/s?k={product_name.replace(" ", "+")}',
            f'{flipkart_price}': f'https://www.flipkart.com/search?q={product_name.replace(" ", "+")}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off',
        }

        return render_template('result.html', result_message=result_message, price_urls=price_urls)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2000)
