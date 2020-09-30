import os
import csv
import time
import urllib.request
import json
import requests

#Define the global variables, or CSV files to be used. Do not include .csv in the variable values.

ALL_IMAGES_WITH_SUBDIRECTORIES = 'Product_Images' #name of main folder to save product images with a subdirectory structure according to the product's categories. Default is Product_Images

PRODUCT_DATA_OUTPUT = 'Product_Data' #name of the CSV file to write product data OUTPUT to. Rename this to match the name of the CSV file to output product data to if necessary

INPUT_BARCODES = 'Barcodes' #name of the csv file to read barcodes from and search the API for, aka the input hardware store's product barcode list. Rename this to match the name of
                            #the CSV file to read barcodes from if necessary

ALL_IMAGES_NO_SUBDIRECTORIES = 'All_Images' #name of the folder to save all product images without subdirectory structure, aka "image dump".

UNMATCHED_PRODUCTS = 'Unmatched_Products' #name of the CSV file to write the products that the API did not return information for.

key = 'vu0o8puy6jahqrepjci5trmfdy3ynu'  # copy and paste API key in between these quotes

read_barcodes = set()


def main():
    if not os.path.exists(ALL_IMAGES_WITH_SUBDIRECTORIES):
        os.mkdir(ALL_IMAGES_WITH_SUBDIRECTORIES)
    if not os.path.exists(ALL_IMAGES_NO_SUBDIRECTORIES):
        os.mkdir(ALL_IMAGES_NO_SUBDIRECTORIES)
    scan_barcodes()

def scan_barcodes():
    with open(INPUT_BARCODES + '.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            print() #printing to console
            if line_count == 0: #skip the first row of the barcodes csv file, since the first row is 'barcode, name'
                line_count+=1
                continue
            elif line_count%100 == 0: #every hundredth line
                print("Sleeping after product: " + str(line_count))
                time.sleep(120) #pause for 2 minutes
            print(line_count)
            barcode = fixBarcode(row[0].strip()) #calls fixBarcode def below on stripped barcodes
            if barcode in read_barcodes:
                continue
            read_barcodes.add(barcode)
            find_product(barcode, row[1]) #calls find_product
            line_count += 1
        print('Processed ' + str(line_count) + ' lines')
        print('Done')

def find_product(barcode, name):
    try:
        url = "https://api.barcodelookup.com/v2/products?barcode=" + barcode + "&formatted=y&key=" + key
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
        mapping = [barcode, name, brand, category, manufacturer, image, weight, description]
        print('found: ')
        print(mapping)
        print()
        mapping.reverse()
        writeProductData(mapping)
        split_categories = category.split('>')
        categories = []
        for i in split_categories:
            categories.append(i.strip())
        buildPath(categories, barcode, image)

    except:
        print('Could not find: ' + barcode + ', ' + name)
        print()
        writeUnmatchedProducts([barcode, name])
    return


def writeUnmatchedProducts(product):
    try:
        row = ""
        for item in product:
            row = item + '@' + row
        file = open(UNMATCHED_PRODUCTS + '.csv', 'a')
        file.write(row[:-2] + '\n')
        file.close()
    except:
        print('Could not write unmatched product to CSV')
        return

def writeProductData(product):
    try:
        row = ""
        for item in product:
            row = item + '@' + row
        file = open(PRODUCT_DATA_OUTPUT + '.csv', 'a')
        file.write(row[:-2] + '\n')
        file.close()
    except:
        print('Could not write product data to CSV')
        return


def buildPath(categories, barcode, image):
    try:
        path = './Product_Images'
        if image is None or len(image) == 0:
            return
        img_data = requests.get(image).content
        for folder in categories:
            path = path + '/' + folder
            if not os.path.exists(path):
                os.mkdir(path)
        path = path + '/' + barcode + '.jpg'
        with open(path, 'wb') as handler:
            handler.write(img_data)
        path = './All_Images/' + barcode + '.jpg'
        with open(path, 'wb') as handler:
            handler.write(img_data)
    except:
        print('Could not build Path')
        return

def fixBarcode(barcode):

    try:
        difference = 12 - len(barcode)
        for i in range(difference):
            barcode = '0' + barcode
        return barcode
    except:
        print('Could not read barcode')
        return

if __name__ == '__main__':
    main()
