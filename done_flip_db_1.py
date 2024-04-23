import os
import mysql.connector
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

app = Flask(__name__)

def get_url(search_term, page_number):
    template = 'https://www.flipkart.com/search?q={}&as=off&page={}'
    search_term = search_term.replace(' ', '+')
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
    sql = "INSERT INTO flip_products (title, price) VALUES (%s, %s)"
    cursor.execute(sql, (title, price))
    connection.commit()

@app.route('/')
def index_flip():
    return render_template('index_flip.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    max_products = 50

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get("https://www.flipkart.com")

    # Establish MySQL connection
    # Establish MySQL connection
    connection = establish_mysql_connection()

    total_products = 0
    products_found = 0
    products_missed = 0
    page_number = 1

    try:
        while products_found < max_products:
            if products_found >= max_products:
                break

            url = get_url(search_term, page_number)
            driver.get(url)

            products_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='_1AtVbE col-12-12']"))
            )

            for product_element in products_elements:
                total_products += 1
                try:
                    title = product_element.find_element(By.XPATH, ".//div[@class='_4rR01T']").text
                    price = product_element.find_element(By.XPATH, ".//div[@class='_30jeq3 _1_WHN1']").text

                    print(f"Title: {title}, Price: {price}")
                    insert_into_mysql(connection, title, price)

                    products_found += 1
                    if products_found >= max_products:
                        break

                except NoSuchElementException:
                    print("Title not found for this product element.")
                    products_missed += 1

            try:
                next_page = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@class='_1LKTO3']"))
                )
                actions = ActionChains(driver)
                actions.move_to_element(next_page).perform()
                next_page.click()

                page_number += 1

            except (TimeoutException, NoSuchElementException):
                print("Bas kar bhai")
                break

    except TimeoutException:
        print("Timeout")

    except Exception as e:
        print(f"An error {e}")

    driver.quit()
    connection.close()

    print(f"Scraping completed! Total products found: {total_products}, Products found: {products_found}, Products missed: {products_missed}")
    return f"Scraping completed! Total products found: {total_products}, Products found: {products_found}, Products missed: {products_missed}"

if __name__ == '__main__':
    app.run(debug=True)
