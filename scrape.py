import re
import requests
import argparse
import datetime

"""This scraper can only retrieve sites that does not rely on javascript to show the products.
This will not work for the following stores:

Ica, CityGross, Lidl, Coop

But it will work for the following stores:

Hemköp, Willys

"""

stores = {
    # Tuesday December 06, 2022
    "Hemköp": {
        "url": "https://www.hemkop.se/sok?q=",
        "headers": {"Accept-Language": "sv-se"},

        # The search results
        "products": r'data-testid="product-container".+?(?=data-testid="product-container")',

        # Each product
        "title": r'title="(.+?(?="))',
        "brand": r'data-testid="display-manufacturer".+?(?=>)>(.+?(?=<\/span))',
        "amount": r'data-testid="display-volume">(.+?(?=<\/span))',
        "compare_price": r'compare-price">(.+?)(?=<)',
        "promotion_compare_price": r'promotion-compare-price">(.+?)(?=<)',
        "price": r'testid="price".*>(\d*,\d*)<span',
    },

    # Tuesday December 06, 2022
    "Willys": {
        "url": "https://www.willys.se/sok?q=",
        "headers": {"Accept-Language": "sv-se"},

        # The search results
        "products": r'data-testid="product".+?(?=data-testid="product")',

        # Each product
        "title": r'Productstyles__StyledProductName.+?(?=>)>(.+?(?=<))',
        "brand": r'Productstyles__StyledProductManufacturerBrand.+?(?=>)>(.+?(?=<))',
        "amount": r'class="Productstyles__StyledProductDisplayVolume-.+?(?=>)>(\d+.+?(?=<))',
        "compare_price": r'class="Productstyles__StyledProductComparePrice-.+?(?=>)>(.+?(?=<))',
        "promotion_compare_price": r'class="Productstyles__StyledProductPromotionPriceInfo-.+?(?=>)>(.+?(?=<))',
        "price": r'itemProp="price" content="(\d*,\d*)',
    },

    # "CityGross": {
    #     "url": "https://www.citygross.se/sok?Q=",
    #     "headers": {"Accept-Language": "sv",
    #         "content": "initial-scale=1,width=device-width,shrink-to-fit=no,height=device-height,user-scalable=0,minimum-scale=1,maximum-scale=1,viewport-fit=cover"},

    #     "products": r'class="l-column-30_xs-30_sm-20_md-15_lg-12_xlg-10-mobileGutter".+?(?=class="l-column-30_xs-30_sm-20_md-15_lg-12_xlg-10-mobileGutter")',
    # }

    # "Ica": {
    #     "url": "https://www.ica.se/handla/sok/",
    #     "headers": {"Accept-Language": "sv-se"},


    # }
}

def get_args():
    """Retrieve arguments from terminal"""

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("groceries", type=str,
                        help="You need to specify which file to read from, i.e groceries.txt")

    parser.add_argument('--from-history', type=str, default=False)
    parser.add_argument('--cheapest-any-brand', action='store_true')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    return args


def regexget(regex, text):
    """Return None if match is not found"""
    return (re.findall(regex, text) or [None])[-1]


def get_num(string):
    """Retrieve number from a string"""
    if string is None:
        return None

    if isinstance(string, float):
        return string
    
    result = re.findall(r'\d+,?\d+', string)

    if any(result):
        return float(result[0].replace(",", "."))

    else:
        return None


args = get_args()


def scrape(query):
    """Scrape the websites and use Regex to find the information"""

    result = {}

    for store_name in stores:
        store = stores[store_name]

        response = requests.get(store["url"]+query, headers=store["headers"])

        content = response.text

        store_products = []

        for item in re.findall(store["products"], content):
            product = {}
            for key in store:
                if key in ("url", "headers", "products"):
                    continue

                product[key] = regexget(store[key], item)

            store_products.append(product)

        result[store_name] = store_products

    return result


def process(results_file):

    with open(results_file, "r") as file:
        results = eval("".join(file.readlines()))
        file.close()

    tmp = {}

    for query in results:
        if query == "meta":
            continue

        cheapest = []

        for shop in results[query]:

            for result in results[query][shop]:

                if not args.cheapest_any_brand:
                    if query not in (result["title"] or " ")+(result["brand"] or " "):
                            continue

                tmp_cheapest = result

                tmp_cheapest["store"] = shop

                values = ("price", "compare_price", "promotion_compare_price")

                for i in values:
                    tmp_cheapest[i] = get_num(result[i])

                cheapest.append(tmp_cheapest)

        if any(cheapest):

            tmp[query] = cheapest[0]

            for item in cheapest[1:]:
                if min(item["promotion_compare_price"] or 1e3, item["compare_price"] or 1e3) <= min(tmp[query]["promotion_compare_price"] or 1e3, tmp[query]["compare_price"] or 1e3):
                    tmp[query] = item

        else:
            print(f"Not found: {query}")

    al = []

    for i in tmp:
        al.append(tmp[i])

    a = {}

    for item in al:

        if not item["store"] in a:
            a[item["store"]] = []
        a[item["store"]].append(item)

    sup_total = 0

    receipt = f"\nReceipt:\n{results_file}\n"

    for store in a:
        total = 0
        receipt += "\n===========================================\n"
        receipt += store + "\n\n"
        for k in a[store]:
            total += k["price"]
            receipt += f'{k["title"]}: {k["price"]}kr {k["amount"] or " "}\n'

        receipt += "\n-------------------------------------------\n"  \
            + f"Total {store}: {round(total, 2)}kr" \
            + "\n-------------------------------------------\n\n"

        sup_total += total

    receipt += f"\nTotal all: {round(sup_total, 2)}kr"

    print(receipt)


def main():
    try:
        with open(args.groceries, "r") as file:
            products = [i.replace("\n", "") for i in file.readlines()]
            file.close()
    except FileNotFoundError:
        print("You must specify a valid shopping list file!")
        exit(1)

    results = {}

    for i, product in enumerate(products):
        results[product] = scrape(product)

        d = int((i+1)/len(products)*20)
        print(f"Searching [{d*'='}{(20-d)*' '}] {int((i+1)/len(products)*100)}%", end="\r")

    history_file = f'receipt-{datetime.datetime.now()}.txt'

    with open(history_file,'w') as data:
        data.write(str(results))
        print(f"Search results saved to:                      \n{history_file}")
        data.close()

    return history_file


if not args.from_history:
    args.from_history = main()

process(args.from_history)