import os
import sys
import time  # Import time module for sleep
import mysql.connector
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

app = Flask(__name__)

def get_url(search_term, page_number):
    template = 'https://www.reliancedigital.in/{}/c/S101210?searchQuery=:relevance:availability:Exclude%20out%20of%20Stock&page={}'
    search_term = search_term.replace(' ', '%20')
    return template.format(search_term, page_number)

# Function to establish MySQL connection
def establish_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="chocolate",
        database="PRODUCTS"
    )

# Function to insert data into MySQL database
def insert_into_mysql(connection, title, price):
    cursor = connection.cursor()
    sql = "INSERT INTO rel_products (title, price) VALUES (%s, %s)"
    cursor.execute(sql, (title, price))
    connection.commit()

@app.route('/')
def index_croma():
    return render_template('index_rel.html')


@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    max_products = 50

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get("https://www.reliancedigital.in")

    # Establish MySQL connection
    connection = establish_mysql_connection()

    total_products = 0
    products_found = 0
    products_missed = 0
    page_number = 0

    try:

        while products_found < max_products:
            if products_found >= max_products:
                break

            url = get_url(search_term, page_number)
            driver.get(url)

            products_elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//li[@class='grid pl__container__sp blk__lg__3 blk__md__4 blk__sm__6 blk__xs__6']"))
            )

            for product_element in products_elements:
                total_products += 1
                try:
                    title = product_element.find_element(By.XPATH, ".//p[@class='sp__name']").text
                    price = product_element.find_element(By.XPATH,
                                                         ".//span[@class='TextWeb__Text-sc-1cyx778-0 gimCrs']").text

                    # Modify print statements to handle Unicode characters
                    print(f"Title: {title}, Price: {price}")
                    insert_into_mysql(connection, title, price)

                    products_found += 1
                    if products_found >= max_products:
                        break

                except NoSuchElementException:
                    print("Title or price not found for this product element.")
                    products_missed += 1

            try:
                # Scroll to the element
                next_page = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//i[@class='fa fa-angle-right']"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_page)
                time.sleep(1)  # Wait for a second after scrolling

                # Attempt to click using JavaScript
                driver.execute_script("arguments[0].click();", next_page)

                page_number += 1

            except (TimeoutException, NoSuchElementException):
                print("Bas kar bhai")
                break

    except TimeoutException:
        print("Timeout")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()
        if connection:
            connection.close()

    print(
        f"Scraping completed! Total products found: {total_products}, Products found: {products_found}, Products missed: {products_missed}")
    return f"Scraping completed! Total products found: {total_products}, Products found: {products_found}, Products missed: {products_missed}"


if __name__ == '__main__':
    app.run(debug=True)
