import time
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from user_generator import (
    generate_multiple_users,
    save_users_to_file,
)
from faker import Faker
import itertools


# Proxy list for rotating proxies
proxy_list = [
    {
        "http": "http://103.152.112.120:80",
        "http": "http://3.212.148.199:3128",
    },
    {"http": "http://162.223.90.130:80", "http": "http://65.155.249.100:8080"},
    {"http": "http://54.67.125.45:3128", "http": "http://50.231.104.58:8080"},
]  # Get premium proxies


# Define proxy rotator using itertools.cycle
def proxy_rotator(proxy_list):
    return itertools.cycle(proxy_list)


# Initialize proxy generator
proxy_gen = proxy_rotator(proxy_list)

# Faker instance for generating random data
fake = Faker()

# Set up WebDriver options (in this case, Chrome)
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Correctly set the path using WebDriverManager
service = Service(ChromeDriverManager().install())

# Initialize the WebDriver with the proper Service and Options
driver = None

# Flag to control whether to use a proxy or not
use_proxy = False  # Set to False to test without proxy, True to use proxy


# Helper function to safely find elements with error handling (using visibility)
def wait_for_element(locator, timeout=10):
    try:
        # Wait for the element to be visible and located in the DOM
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return element
    except Exception as e:
        print(f"Error finding element {locator}: {e}")
        return None


# Function to test if the proxy works
def test_proxy(proxy):
    try:
        response = requests.get("http://httpbin.org/ip", proxies=proxy, timeout=5)
        if response.status_code == 200:
            print(f"Proxy works: {proxy}")
            return True
        else:
            print(f"Proxy failed: {proxy}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Proxy test failed: {proxy} with error {e}")
        return False


# Function to check if the driver is initialized
def check_driver_initialized():
    global driver
    if driver is None:
        print("Driver is not initialized. Initializing now...")
        driver = get_driver_with_proxy()  # Call the function to initialize the driver
    return driver


# Initialize the driver with proxy (or without proxy if use_proxy is False)
def get_driver_with_proxy():
    retry_count = 3
    while retry_count > 0:
        try:
            if use_proxy:
                # Only use proxy if the flag is set to True
                proxy = next(proxy_gen)
                if test_proxy(proxy):  # Test if the proxy is working before using it
                    chrome_options = Options()  # Reusing the existing options setup
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument(f"--proxy-server={proxy['http']}")

                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    return driver
                else:
                    retry_count -= 1
                    print(f"Proxy {proxy} failed. Retrying...")
            else:
                # If no proxy is used, just initialize the driver without proxy settings
                chrome_options = Options()  # Reusing the existing options setup
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")

                driver = webdriver.Chrome(service=service, options=chrome_options)
                return driver
        except Exception as e:
            retry_count -= 1
            print(
                f"Error setting up driver with proxy: {e}. Retries left: {retry_count}"
            )
            if retry_count == 0:
                print("All retries failed, skipping proxy.")
                raise Exception("Could not initialize WebDriver with proxy.")


# Function to dynamically navigate to the appropriate page
def navigate_to_page():
    # Ensure the driver is initialized before usage
    check_driver_initialized()

    # Go to the homepage or entry point of the app
    driver.get("https://bsky.app")

    # Wait for dynamic elements to load (like the sign-up button)
    signup_button = wait_for_element(
        (
            By.XPATH,
            '//button[@aria-label="Sign up"]',
        )  # Using aria-label to locate the button
    )

    # Check if the signup button is found and click it to navigate to the sign-up page
    if signup_button:
        signup_button.click()  # Click the signup button to proceed


# Function to register a new user (Stage 1)
def register_user_stage_1(email, password, date_of_birth):
    try:
        navigate_to_page()  # Ensure we're on the correct page (e.g., login or registration)

        # Wait for and click the select service button
        select_service_button = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="selectServiceButton"]')
        )
        if select_service_button:
            select_service_button.click()

        # Wait for and fill the email field
        email_input = wait_for_element((By.CSS_SELECTOR, '[data-testid="emailInput"]'))
        if email_input:
            email_input.send_keys(email)

        # Wait for and fill the password field
        password_input = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="passwordInput"]')
        )
        if password_input:
            password_input.send_keys(password)

        # Wait for and fill the date of birth picker field
        date_input = wait_for_element((By.CSS_SELECTOR, '[data-testid="date"]'))
        if date_input:
            date_input.send_keys(date_of_birth)

        # Click the 'Next' button to go to the next page (username)
        next_button = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="nextButton"]'), timeout=15
        )
        if next_button:
            next_button.click()

        print("Moved to the next stage (username).")

    except Exception as e:
        print(f"Error during registration (stage 1): {e}")


# Function to register the user (Stage 2)
def register_user_stage_2(username):
    try:
        check_driver_initialized()  # Ensure the driver is initialized before usage
        # Wait for and fill the username field on the next page
        username_input = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="usernameInput"]')
        )
        if username_input:
            username_input.send_keys(username)

        # Click the 'Register' button to complete the registration
        register_button = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="registerButton"]')
        )
        if register_button:
            register_button.click()

        print(f"User {username} registered successfully.")

    except Exception as e:
        print(f"Error during registration (stage 2): {e}")


# Function to log in
def login(username, password):
    try:
        check_driver_initialized()  # Ensure the driver is initialized before usage
        driver.get("https://bsky.app")  # Go to the homepage

        # Wait for dynamic content like the login form to appear
        login_button = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="loginButton"]')
        )  # Adjust this selector if needed
        if login_button:
            login_button.click()  # Navigate to login

        # Wait for username input and fill it
        username_field = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="loginUsernameInput"]')
        )  # Adjust if necessary
        if username_field:
            username_field.send_keys(username)

        # Wait for password input and fill it
        password_field = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="loginPasswordInput"]')
        )  # Adjust if necessary
        if password_field:
            password_field.send_keys(password)

        # Wait for and click the login button to complete login
        login_submit_button = wait_for_element(
            (By.CSS_SELECTOR, '[data-testid="loginSubmitButton"]')
        )  # Adjust if necessary
        if login_submit_button:
            login_submit_button.click()

        print(f"Logged in as {username}")

    except Exception as e:
        print(f"Error during login for {username}: {e}")


# Main automation loop
def main():
    users = []  # List to store the users
    try:
        while True:
            # Generate 2 new users at regular intervals (you can adjust this number as needed)
            new_users = generate_multiple_users(2)  # Generating 2 users
            users.extend(new_users)  # Add the generated users to the list

            # Register the newly generated users and simulate their actions
            for user in new_users:
                try:
                    # Register the user (Stage 1)
                    register_user_stage_1(user["email"], user["password"], "2004-12-27")

                    # Register the user (Stage 2)
                    register_user_stage_2(user["username"])

                    # Log in after registration
                    login(user["username"], user["password"])
                except Exception as e:
                    print(f"Error during user registration or login: {e}")

            # Save the list of users to the file after each batch
            save_users_to_file(users)
            print(f"Generated and registered 2 users, total users: {len(users)}.")

            # Wait for 30 minutes (1800 seconds) before generating more users
            time.sleep(1800)  # 30 minutes interval

    except KeyboardInterrupt:
        print("\nProcess interrupted. Saving users to 'users.json'.")
        save_users_to_file(users)
        print(f"Final count of users: {len(users)}.")
    finally:
        driver.quit()  # Close the browser when done


if __name__ == "__main__":
    main()
