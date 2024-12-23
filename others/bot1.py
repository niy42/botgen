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
        "https": "http://3.212.148.199:3128",
    },
    {"http": "http://162.223.90.130:80", "https": "http://65.155.249.100:8080"},
    {"http": "http://54.67.125.45:3128", "https": "http://50.231.104.58:8080"},
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


# Helper function to safely find elements with error handling
def safe_find_element(locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    except Exception as e:
        print(f"Error finding element {locator}: {e}")
        return None


# Function to check if the driver is initialized
def check_driver_initialized():
    global driver
    if driver is None:
        print("Driver is not initialized. Initializing now...")
        driver = get_driver_with_proxy()  # Call the function to initialize the driver
    return driver


# Initialize the driver with proxy
def get_driver_with_proxy():
    retry_count = 3
    while retry_count > 0:
        try:
            proxy = next(proxy_gen)
            chrome_options = Options()  # Reusing the existing options setup
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--proxy-server={proxy['http']}")

            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            retry_count -= 1
            print(f"Proxy failed: {e}. Retries left: {retry_count}.")
            if retry_count == 0:
                print("All retries failed, skipping proxy.")
                raise Exception("Could not initialize WebDriver with proxy.")


# URLs
login_url = "https://bsky.app/login"
registration_url = "https://bsky.app/signup"
post_url = "https://bsky.app/x"
like_url = "https://bsky.app/x/like"
dislike_url = ""
profile_url = "https://bsky.app/profile/{username}"


# Function to register a new user (Stage 1)
def register_user_stage_1(email, password, date_of_birth):
    try:
        check_driver_initialized()  # Ensure the driver is initialized before usage
        driver.get(registration_url)

        # Wait for and click the select service button
        select_service_button = safe_find_element(
            (By.CSS_SELECTOR, '[data-testid="selectServiceButton"]')
        )
        if select_service_button:
            select_service_button.click()

        # Wait for and fill the email field
        email_input = safe_find_element((By.CSS_SELECTOR, '[data-testid="emailInput"]'))
        if email_input:
            email_input.send_keys(email)

        # Wait for and fill the password field
        password_input = safe_find_element(
            (By.CSS_SELECTOR, '[data-testid="passwordInput"]')
        )
        if password_input:
            password_input.send_keys(password)

        # Wait for and fill the date of birth picker field
        date_input = safe_find_element((By.CSS_SELECTOR, '[data-testid="date"]'))
        if date_input:
            date_input.send_keys(date_of_birth)

        # Click the 'Next' button to go to the next page (username)
        next_button = safe_find_element(
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
        username_input = safe_find_element(
            (By.CSS_SELECTOR, '[data-testid="usernameInput"]')
        )
        if username_input:
            username_input.send_keys(username)

        # Click the 'Register' button to complete the registration
        register_button = safe_find_element(
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
        driver.get(login_url)
        username_field = safe_find_element((By.ID, "username_field"))
        if username_field:
            username_field.send_keys(username)

        password_field = safe_find_element((By.ID, "password_field"))
        if password_field:
            password_field.send_keys(password)

        login_button = safe_find_element((By.ID, "login_button"))
        if login_button:
            login_button.click()

        time.sleep(3)
    except Exception as e:
        print(f"Error during login for {username}: {e}")


# Function to generate a random post content using Faker
def generate_random_post():
    return fake.sentence()  # Generate a random sentence


# Function to make a post with randomly generated content
def make_post():
    post_content = generate_random_post()
    check_driver_initialized()  # Ensure the driver is initialized before usage
    driver.get(post_url)
    try:
        post_content_field = safe_find_element((By.ID, "post_content_field"))
        if post_content_field:
            post_content_field.send_keys(post_content)

        post_button = safe_find_element((By.ID, "post_button"))
        if post_button:
            post_button.click()
        print(f"Posted: {post_content}")
    except Exception as e:
        print(f"Error making post: {e}")


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
