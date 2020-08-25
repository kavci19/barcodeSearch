import os
import csv
import urllib.request
import json
import pprint
import requests

unmatched_products = []
barcodeNameMap = []

SAVE_FOLDER = 'Product_Images'
PRODUCT_DATA = 'Product_Data'
ALL_IMAGES = 'All_Images'
key = ''  # copy and paste API key in between these quotes


def main():
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)

    if not os.path.exists(ALL_IMAGES):
        os.mkdir(ALL_IMAGES)

    scan_barcodes()


def scan_barcodes():
    with open('Barcodes.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            print()

            if line_count == 0:
                line_count += 1
                continue

            elif line_count > 100:
                break

            else:

                progress = (line_count / 1791) * 100

                print(str(round(progress, 2)) + '% done')

                barcode = fixBarcode(row[0].strip())

                find_product(barcode, row[1])

            line_count += 1

        print('Processed ' + str(line_count) + ' lines')
        print('Done')

        print()

        writeUnmatchedProducts()
        writeProductData()

        print(unmatched_products)


def find_product(barcode, name):
    print(barcode)

    try:
        url = "https://api.barcodelookup.com/v2/products?barcode=" + barcode + "&formatted=y&key=" + key
        print(url)
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())

        barcode = data["products"][0]["barcode_number"]

        brand = data["products"][0]["brand"]

        name = data["products"][0]["product_name"]

        category = data["products"][0]["category"]

        description = data["products"][0]["description"]

        image = data["products"][0]["images"][0]

        manufacturer = data["products"][0]["manufacturer"]

        weight = data["products"][0]["weight"]

        print("Entire Response:")
        pprint.pprint(data)

        mapping = [barcode, name, brand, category, manufacturer, image, weight, description]
        barcodeNameMap.append(mapping)

        split_categories = category.split('>')
        categories = []
        for i in split_categories:
            categories.append(i.strip())

        buildPath(categories, barcode, image)

        print(categories)

    except:

        unmatched_products.append([barcode, name])

    return


def writeUnmatchedProducts():
    with open('Unmatched_Products.csv', mode='w') as unmatched:
        writer = csv.writer(unmatched, quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for product in unmatched_products:
            writer.writerow(product)


def writeProductData():
    with open('Product_Data.csv', mode='w') as data:
        writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for product in barcodeNameMap:
            writer.writerow(product)


def buildPath(categories, barcode, image):
    path = './Product_Images'

    if image is None or len(image) == 0:
        return

    img_data = requests.get(image).content

    for folder in categories:
        path = path + '/' + folder
        if not os.path.exists(path):
            os.mkdir(path)

    path = path + '/' + barcode + '.jpg'

    print('Path: ' + path)
    with open(path, 'wb') as handler:
        handler.write(img_data)

    path = './All_Images/' + barcode + '.jpg'
    with open(path, 'wb') as handler:
        handler.write(img_data)


def fixBarcode(barcode):
    difference = 12 - len(barcode)

    for i in range(difference):
        barcode = '0' + barcode

    return barcode


if __name__ == '__main__':
    main()
