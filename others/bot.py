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
    {"http": "http://103.152.112.120:80", "https": "http://3.212.148.199:3128"},
    {"http": "http://162.223.90.130:80", "https": "http://65.155.249.100:8080"},
    {"http": "http://54.67.125.45:3128", "https": "http://50.231.104.58:8080"},
]


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
driver = webdriver.Chrome(service=service, options=chrome_options)


# Initialize the driver with proxy
def get_driver_with_proxy():
    retry_count = 3
    while retry_count > 0:
        try:
            proxy = next(proxy_gen)
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--proxy-server={proxy['http']}")

            driver = webdriver.Chrome(
                ChromeDriverManager().install(), options=chrome_options
            )
            return driver
        except Exception as e:
            retry_count -= 1
            print(f"Proxy failed: {e}. Retries left: {retry_count}.")
            if retry_count == 0:
                print("All retries failed, skipping proxy.")
                continue


# Initialize the driver
driver = get_driver_with_proxy()

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
        driver.get(registration_url)

        # Wait for and click the select service button
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="selectServiceButton"]')
            )
        ).click()

        # Wait for and fill the email field
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="emailInput"]')
            )
        ).send_keys(email)

        # Wait for and fill the password field
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="passwordInput"]')
            )
        ).send_keys(password)

        # Wait for and fill the date of birth picker field
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="date"]'))
        ).send_keys(
            date_of_birth
        )  # Example: "2004-12-27" for December 27, 2004

        # Click the 'Next' button to go to the next page (username)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="nextButton"]'))
        ).click()

        # Wait for the username field
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="usernameInput"]')
            )
        )

        print("Moved to the next stage (username).")

    except Exception as e:
        print(f"Error during registration (stage 1): {e}")


# Function to register the user (Stage 2)
def register_user_stage_2(username):
    try:
        # Wait for and fill the username field on the next page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="usernameInput"]')
            )
        ).send_keys(username)

        # Click the 'Register' button to complete the registration
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="registerButton"]')
            )
        ).click()

        print(f"User {username} registered successfully.")

    except Exception as e:
        print(f"Error during registration (stage 2): {e}")


# Function to log in
def login(username, password):
    try:
        driver.get(login_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username_field"))
        ).send_keys(username)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password_field"))
        ).send_keys(password)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login_button"))
        ).click()
        time.sleep(3)
    except Exception as e:
        print(f"Error during login for {username}: {e}")


# Function to generate a random post content using Faker
def generate_random_post():
    return fake.sentence()  # Generate a random sentence


# Function to make a post with randomly generated content
def make_post():
    post_content = generate_random_post()
    driver.get(post_url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "post_content_field"))
        ).send_keys(post_content)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "post_button"))
        ).click()
        print(f"Posted: {post_content}")
    except Exception as e:
        print(f"Error making post: {e}")


# Function to like a post
def like_post(post_id):
    driver.get(like_url + f"?post_id={post_id}")
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"like_button_{post_id}"))
        ).click()
        print(f"Liked post with ID: {post_id}")
    except Exception as e:
        print(f"Error liking post with ID {post_id}: {e}")


# Function to dislike a post
def dislike_post(post_id):
    driver.get(dislike_url + f"?post_id={post_id}")
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"dislike_button_{post_id}"))
        ).click()
        print(f"Disliked post with ID: {post_id}")
    except Exception as e:
        print(f"Error disliking post with ID {post_id}: {e}")


# Function to follow a user
def follow_user(user_id):
    driver.get(profile_url.format(username=user_id))
    try:
        follow_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, f"follow_button_{user_id}"))
        )
        if follow_button.text == "Follow":
            follow_button.click()
            print(f"Followed user with ID: {user_id}")
        else:
            print(f"Already following user with ID: {user_id}")
    except Exception as e:
        print(f"Error following user with ID {user_id}: {e}")


# Function to unfollow a user
def unfollow_user(user_id):
    driver.get(profile_url.format(username=user_id))
    try:
        unfollow_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, f"unfollow_button_{user_id}"))
        )
        if unfollow_button.text == "Unfollow":
            unfollow_button.click()
            print(f"Unfollowed user with ID: {user_id}")
        else:
            print(f"Already unfollowed user with ID: {user_id}")
    except Exception as e:
        print(f"Error unfollowing user with ID {user_id}: {e}")


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
