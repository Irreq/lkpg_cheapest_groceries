import argparse
import re
import time

from stores import *

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

def get_num(string):
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


def process(results):

    tmp = {}

    for query in results:
        if query == "meta":
            continue

        cheapest = []

        for shop in results[query]:

            for result in results[query][shop]:

                if not args.cheapest_any_brand:

                    try:
                        if query not in result["title"]+result["brand"]:
                            continue
                    except:
                        continue

                tmp_cheapest = result

                tmp_cheapest["store"] = shop

                values = ("original_price", "compare_price", "promo_compare_price")

                for i in values:
                    tmp_cheapest[i] = get_num(result[i])

                cheapest.append(tmp_cheapest)

        if any(cheapest):

            tmp[query] = cheapest[0]

            for item in cheapest[1:]:
                if min(item["promo_compare_price"] or 1e3, item["compare_price"] or 1e3) <= min(tmp[query]["promo_compare_price"] or 1e3, tmp[query]["compare_price"] or 1e3):
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
    receipt = f'{results["meta"]["date"]}'
    # receipt = ""
    # print(results)
    for store in a:
        total = 0
        receipt += "\n===========================================\n"
        receipt += store + "\n\n"
        for k in a[store]:
            total += k["original_price"]
            receipt += f'{k["title"]}: {k["original_price"]}kr\n'

        receipt += "\n-------------------------------------------\n"  \
            + f"Total {store}: {round(total, 2)}kr" \
            + "\n-------------------------------------------\n\n"

        sup_total += total

    receipt += f"\nTotal all: {round(sup_total, 2)}kr"

    print(receipt)


if args.from_history:
    with open(args.from_history, "r") as file:
        results = eval("".join(file.readlines()))
        file.close()
    process(results)

else:

    with open(args.groceries, "r") as file:
        products = [i.replace("\n", "") for i in file.readlines()]
        file.close()


    results = {}

    for i, product in enumerate(products):

        results[product] = {}

        for shop in shops:
            results[product][shop.__name__] = shop(product)

            if args.cheapest_any_brand:

                ps = results[product][shop.__name__]

                tmp_ps = []

                for item in ps:
                    tmp = item

                    values = ("original_price", "compare_price", "promo_compare_price")

                    for t in values:
                        tmp[t] = get_num(item[t])

                    tmp_ps.append(tmp)

                results[product][shop.__name__] = tmp_ps

        print(f"Searching {int((i+1)/len(products)*100)}%", end="\r")

    results["meta"] = {"date": time.time()} 

    process(results)

    with open('history.txt','w') as data:
        data.write(str(results))