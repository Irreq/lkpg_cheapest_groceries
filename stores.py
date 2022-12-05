from bs4 import BeautifulSoup
import requests
import re


def hemkop(product, sanitize=True, hard_pass=True):
    response = requests.get("https://www.hemkop.se/sok?q=" + product)

    soup = BeautifulSoup(response.content, "html.parser")

    results = []

    # Get all results in search
    for item in soup.select('[data-testid="product-container"]'):

        # Title happens to be last element
        title = item.select("[title]")[-1].get_text().strip()

        result = {}

        result["title"] = title

        try:
            result["brand"] = item.select('[data-testid="display-manufacturer"]')[0].get_text().strip()
        except:
            result["brand"] = None

        try:
            result["amount"] = item.select('[data-testid="display-volume"]')[0].get_text().strip()
        except:
            result["amount"] = None
        prices = item.select('[data-testid="price"]')

        if len(prices) == 2: # Has promo
            tags = ("promo_price", "original_price")

            for tag, val in zip(tags, prices):
                result[tag] = val.get_text().strip()

        else:
            result["original_price"] = item.select('[data-testid="price"]')[0].get_text().strip()


        try:
            cp_raw = item.select('[data-testid="compare-price"]')[0].get_text().strip()
        except:
            cp_raw = None

        # compare_price = float(cp_raw[len("Jmf pris "):-len(" kr/kg")].replace(",", "."))
        compare_price = cp_raw

        result["compare_price"] = compare_price

        try:
            promo_cp_raw = item.select('[data-testid="promotion-compare-price"]')[0].get_text().strip()

            # promo_compare_price = float(promo_cp_raw[len("Jmf pris "):-len(" kr/kg")].replace(",", "."))
            promo_compare_price = promo_cp_raw

            result["promo_compare_price"] = promo_compare_price

        except:     # No promotion for this product
            result["promo_compare_price"] = None

        results.append(result)

    return results

def willys(product, sanitize=True, hard_pass=True):
    response = requests.get("https://www.willys.se/sok?q=" + product)

    soup = BeautifulSoup(response.content, "html.parser")

    results = []
    
    for item in soup.select('[data-testid="product"]'):

        result = {}

        content = str(item)
        
        # Must create title this way as title is not retrieved at each step
        for name in item.select('[itemprop="name"]'):
            title = name.get_text().strip()
            result["title"] = title

        try:
            amount = re.findall(r'class="Productstyles__StyledProductDisplayVolume-.+?(?=>)>(\d+.+?(?=<))', content)[0]
        except:
            amount = None

        result["amount"] = amount

        cp = re.findall(r'class="Productstyles__StyledProductComparePrice-.+?(?=>)>(.+?(?=<))', content)

        result["compare_price"] = cp[0]

        promo_cp = re.findall(r'class="Productstyles__StyledProductPromotionPriceInfo-.+?(?=>)>(.+?(?=<))', content)

        promo_cp_raw = None
        if any(promo_cp):
            promo_cp_raw = promo_cp[0]

        result["promo_compare_price"] = promo_cp_raw

        result["original_price"] = item.select('[itemprop="price"]')[0].get("content")

        if result["title"] == None:
            continue

        try:
            result["brand"] = item.select('[itemprop="brand"]')[0].get_text().strip()
            results.append(result)
        except:
            pass

    return results


shops = [hemkop, willys]