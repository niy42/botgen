import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from user_generator import (
    generate_multiple_users,
    save_users_to_file,
)
from faker import Faker
import itertools

# proxy list for rotating proxies
proxy_list = [
    {"http": "http://27.64.18.8:10004", "https": "http://27.64.18.8:10004"},
    {"http": "http://161.35.70.249:3128", "https": "http://161.35.70.249:3129"},
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

# Specify path to chromedriver (use the path where you extracted the file)
chromedriver_path = "C:\\Users\\USER\\Downloads\\chromedriver-win64\\chromedriver.exe"

# Path to your WebDriver (e.g., chromedriver.exe for Chrome)
webdriver_service = Service(executable_path=chromedriver_path)


# Initialize WebDriver with proxy
def get_driver_with_proxy():
    # Get the next proxy from the proxy generator
    proxy = next(proxy_gen)
    chrome_options.add_argument(f"--proxy-server={proxy['http']}")
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    return driver


# Initialize the driver
driver = get_driver_with_proxy()

# URLs (replace with the actual URLs) registration_url = "https://events.bsky.app/v2/rgstr"
login_url = "https://bsky.app/login"
registration_url = "https://bsky.app/signup"
post_url = "https://bsky.app/x"
like_url = "https://bsky.app/x/like"
dislike_url = ""
profile_url = "https://bsky.app/profile/<username>"


# Function to register a new user
def register_user(username, email, password):
    driver.get(registration_url)
    time.sleep(2)

    # Find and fill in the registration form fields (adjust selectors based on the actual page)
    driver.find_element(By.ID, "username_field").send_keys(username)
    driver.find_element(By.ID, "email_field").send_keys(email)
    driver.find_element(By.ID, "password_field").send_keys(password)
    driver.find_element(By.ID, "confirm_password_field").send_keys(password)

    # Submit the registration form
    driver.find_element(By.ID, "register_button").click()
    time.sleep(3)

    # Check for successful registration (adjust the check based on the site's behavior)
    if (
        "registration_success" in driver.current_url
    ):  # Adjust URL check based on actual site
        print(f"User {username} registered successfully.")
    else:
        print(f"Registration failed for {username}.")


# Function to log in
def login(username, password):
    driver.get(login_url)
    time.sleep(2)

    # Find login form fields (adjust the selectors based on the actual page)
    driver.find_element(By.ID, "username_field").send_keys(username)
    driver.find_element(By.ID, "password_field").send_keys(password)

    # Click login button
    driver.find_element(By.ID, "login_button").click()
    time.sleep(3)


# Function to generate a random post content using Faker
def generate_random_post():
    # You can create random sentences, words, or even fake quotes
    return fake.sentence()  # Generate a random sentence


# Function to make a post with randomly generated content
def make_post():
    post_content = generate_random_post()
    driver.get(post_url)
    time.sleep(2)

    # Find the post form (adjust the selectors based on the actual page)
    driver.find_element(By.ID, "post_content_field").send_keys(post_content)
    driver.find_element(By.ID, "post_button").click()
    time.sleep(2)
    print(f"Posted: {post_content}")


# Function to like a post
def like_post(post_id):
    driver.get(like_url + f"?post_id={post_id}")
    time.sleep(2)
    driver.find_element(By.ID, f"like_button_{post_id}").click()
    time.sleep(2)
    print(f"Liked post with ID: {post_id}")


# Function to dislike a post
def dislike_post(post_id):
    driver.get(dislike_url + f"?post_id={post_id}")
    time.sleep(2)
    driver.find_element(By.ID, f"dislike_button_{post_id}").click()
    time.sleep(2)
    print(f"Disliked post with ID: {post_id}")


# Function to follow a user
def follow_user(user_id):
    driver.get(profile_url + f"/{user_id}")
    time.sleep(2)

    follow_button = driver.find_element(By.ID, f"follow_button_{user_id}")
    if follow_button.text == "Follow":  # Ensure it's not already followed
        follow_button.click()
        time.sleep(2)
        print(f"Followed user with ID: {user_id}")
    else:
        print(f"Already following user with ID: {user_id}")


# Function to unfollow a user
def unfollow_user(user_id):
    driver.get(profile_url + f"/{user_id}")
    time.sleep(2)

    unfollow_button = driver.find_element(By.ID, f"unfollow_button_{user_id}")
    if unfollow_button.text == "Unfollow":  # Ensure it's not already unfollowed
        unfollow_button.click()
        time.sleep(2)
        print(f"Unfollowed user with ID: {user_id}")
    else:
        print(f"Already unfollowed user with ID: {user_id}")


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
                # Register the user
                register_user(user["username"], user["email"], user["password"])

                # Log in after registration
                login(user["username"], user["password"])

                # Simulate user actions
                make_post()  # Simulate making a post
                post_id_to_like = 12345  # Example post ID to like
                post_id_to_dislike = 12346  # Example post ID to dislike
                like_post(post_id_to_like)
                dislike_post(post_id_to_dislike)

                # Simulate following and unfollowing users
                user_id_to_follow = 7890  # Example user ID to follow
                user_id_to_unfollow = 7891  # Example user ID to unfollow
                follow_user(user_id_to_follow)
                unfollow_user(user_id_to_unfollow)

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
