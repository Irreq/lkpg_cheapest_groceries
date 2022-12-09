# lkpg_cheapest_groceries
Scrape common grocery stores in Linköping for cheapest prices.
This script is in early development and currently only supports the following stores:

* Willys
* Hemköp

Output of the program could look like:

    user@pc ~/$ python3 scrape.py groceries.txt

    Search results saved to:
    receipt-2022-12-09 20:53:38.647578.txt

    Receipt:
    receipt-2022-12-09 20:53:38.647578.txt

    ===========================================
    Willys

    Vetemjöl: 41.9kr 5kg
    Köttbullar Fryst: 43.9kr 1kg

    -------------------------------------------
    Total Willys: 85.8kr
    -------------------------------------------


    ===========================================
    Hemköp

    Yoghurt Naturell: 27.5kr 1,5kg
    Spaghetti Pasta: 33.5kr 1.8kg

    -------------------------------------------
    Total Hemköp: 61.0kr
    -------------------------------------------


    Total all: 146.8kr


## Prerequisites

Create a grocery list like `groceries.txt` that can look like:

    Pasta
    Yoghurt
    Vetebullar
    Broccoli

Capital letters might be necessary, an easy fix is to go to one of the websites and copy-paste the correct name for the item into the text file.

## Usage

Simply have the script use your grocery list like `python3 scrape.py <LIST>` which in practice could look like:

    python3 scrape.py groceries.txt
