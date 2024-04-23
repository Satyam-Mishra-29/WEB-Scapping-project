import os
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
import time

app = Flask(__name__)

def get_url(search_term):
    template = 'https://www.croma.com/searchB?q={}%3Arelevance&text={}'
    search_term = search_term.replace(' ', '%20')
    return template.format(search_term, search_term)

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
    sql = "INSERT INTO croma_products (title, price) VALUES (%s, %s)"
    cursor.execute(sql, (title, price))
    connection.commit()

@app.route('/')
def index_croma():
    return render_template('index_croma.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    max_products = 50
    products_found = 0
    products_missed = 0
    total_products = 0

    driver = None
    connection = None

    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.maximize_window()
        driver.get("https://www.croma.com")
        
        # Establish MySQL connection
        connection = establish_mysql_connection()

        while products_found < max_products:
            if products_found >= max_products:
                break

            url = get_url(search_term)
            driver.get(url)

            # Wait for all product elements to be loaded
            products_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='content-wrap']//div[contains(@class, 'product ')]"))
            )

            for product_element in products_elements:
                total_products += 1
                try:
                    title = product_element.find_element(By.XPATH, ".//h3[@class='product-title plp-prod-title 999']").text
                    price = product_element.find_element(By.XPATH, ".//span[@class='amount plp-srp-new-amount']").text

                    print(f"Title: {title}, Price: {price}")
                    
                    insert_into_mysql(connection, title, price)

                    products_found += 1
                    if products_found >= max_products:
                        break

                except NoSuchElementException:
                    print("Title or price not found for this product element.")
                    products_missed += 1

            try:
                # Click on the "View More" button to load additional products
                view_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-viewmore')]"))
                )
                view_more_button.click()
            except TimeoutException:
                print("No more products to load.")
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()  # Quit the driver instance if it exists
        if connection:
            connection.close()

    print(f"Scraping completed! Total products found: {total_products}, Products found: {products_found}, Products missed: {products_missed}")
    return f"Scraping completed! Total products found: {total_products}, Products found: {products_found}, Products missed: {products_missed}"

if __name__ == '__main__':
    app.run(debug=True)
