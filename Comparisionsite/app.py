from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import pandas as pd

app = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
}

def get_flipkart_data(name):
    try:
        name1 = name.replace(" ", "+")
        url = f'https://www.flipkart.com/search?q={name1}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off'
        res = requests.get(url, headers=headers)

        print("\nSearching in Flipkart....")
        soup = BeautifulSoup(res.text, 'html.parser')

        product_data = {}

        if soup.select('._4rR01T'):
            flipkart_name = soup.select('._4rR01T')[0].getText().strip().upper()
            if name.upper() in flipkart_name:
                flipkart_price = soup.select('._30jeq3')[0].getText().strip()
                flipkart_rating = soup.select('._3LWZlK')[0].getText().strip()
                description_element = soup.find("ul", class_="_1xgFaf")
                flipkart_description = description_element.text.strip() if description_element else ""
                product_data["Name"] = flipkart_name
                product_data["Price"] = flipkart_price
                product_data["Rating"] = flipkart_rating
                product_data["Description"] = flipkart_description
                print("Flipkart:")
                print(f"Name: {flipkart_name}")
                print(f"Price: {flipkart_price}")
                print(f"Rating: {flipkart_rating}")
                print(f"Description: {flipkart_description}")
                print("---------------------------------")
                return product_data

        elif soup.select('.s1Q9rs'):
            flipkart_name = soup.select('.s1Q9rs')[0].getText().strip().upper()
            if name.upper() in flipkart_name:
                flipkart_price = soup.select('._30jeq3')[0].getText().strip()
                description_element = soup.find("ul", class_="_1xgFaf")
                flipkart_description = description_element.text.strip() if description_element else ""
                product_data["Name"] = flipkart_name
                product_data["Price"] = flipkart_price
                product_data["Description"] = flipkart_description
                print("Flipkart:")
                print(f"Name: {flipkart_name}")
                print(f"Price: {flipkart_price}")
                print(f"Description: {flipkart_description}")
                print("---------------------------------")
                return product_data
        else:
            print("Flipkart: No product found!")
            print("---------------------------------")
            return None

    except Exception as e:
        print(f"Error: {e}")
        print("Flipkart: No product found!")
        print("---------------------------------")
        return None

def convert_price(a):
    try:
        b = a.replace(" ", '')
        c = b.replace("INR", '')
        d = c.replace(",", '')
        f = d.replace("₹", '')
        g = float(f)
        return g
    except ValueError:
        return 0.0

def filter_and_display_similar_products(product_type, reference_price):
    all_data = []
    page = 1

    while True:
        url = f"https://www.flipkart.com/search?q={product_type}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off&page={page}"

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        boxes = soup.find_all("div", class_="_1AtVbE")

        if not boxes:
            # No more pages, exit the loop
            break

        for box in boxes:
            data = {}

            name_element = box.find("div", class_="_4rR01T")
            price_element = box.find("div", class_="_30jeq3 _1_WHN1")
            desc_element = box.find("ul", class_="_1xgFaf")
            review_element = box.find("div", class_="_3LWZlK")
            assured_element = box.find("div", class_="_13J9qT")  # Check for assured class

            data["Product Name"] = name_element.text.strip() if name_element else ""
            data["Prices"] = price_element.text.strip() if price_element else ""
            data["Description"] = desc_element.text.strip() if desc_element else ""
            data["Reviews"] = review_element.text.strip() if review_element else ""
            data["Assured"] = "Yes" if assured_element else "No"  # Add assured information

            all_data.append(data)

        # Check for the presence of the "Next" button
        next_button = soup.find("a", class_="_1LKTO3")

        if not next_button:
            # No more pages, exit the loop
            break

        # Move to the next page
        page += 1

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_data)

    # Filter products based on the reference price
    df["Prices"] = df["Prices"].apply(convert_price)
    filtered_products = df[(df["Prices"] >= reference_price - 10000) & (df["Prices"] <= reference_price + 10000)]

    # Display filtered products
    print(f"\nPhones in the same price range as {product_type} ({reference_price}):")
    print(filtered_products[["Product Name", "Prices", "Description", "Assured"]])

    return filtered_products  # Return the filtered products DataFrame

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        flipkart_data = get_flipkart_data(product_name)

        if flipkart_data:
            flipkart_price = convert_price(flipkart_data["Price"])
            filtered_products = filter_and_display_similar_products(product_type, flipkart_price)

            return render_template('index.html', flipkart_data=flipkart_data, filtered_products=filtered_products.to_html())
    
    return render_template('index.html', flipkart_data=None, filtered_products=None)

if __name__ == '__main__':
    app.run(port=1000)  # You can change the port as needed
