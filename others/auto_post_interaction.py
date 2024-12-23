from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from user_generator import (
    generate_multiple_users,
    save_users_to_file,
)  # Importing the user generator functions

import time

# Set up WebDriver options (in this case, Chrome)
chrome_options = Options()
chrome_options.add_argument(
    "--headless"
)  # Run in headless mode (without opening a browser window)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Specify path to chromedriver (use the path where you extracted the file)
chromedriver_path = "C:\\Users\\USER\\Downloads\\chromedriver-win64\\chromedriver.exe"

# Path to your WebDriver (e.g., chromedriver.exe for Chrome)
webdriver_service = Service(executable_path=chromedriver_path)

# Initialize WebDriver
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# URLs (replace with the actual URLs)
login_url = "https://example.com/login"
registration_url = "https://example.com/register"
post_url = "https://example.com/post"
like_url = "https://example.com/like"
dislike_url = "https://example.com/dislike"
profile_url = (
    "https://example.com/profile"  # Example profile URL for follow/unfollow actions
)

# Example user credentials
username = "newuser123"
password = "newpassword123"
email = "newuser123@example.com"


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
def login():
    driver.get(login_url)
    time.sleep(2)

    # Find login form fields (adjust the selectors based on the actual page)
    driver.find_element(By.ID, "username_field").send_keys(username)
    driver.find_element(By.ID, "password_field").send_keys(password)

    # Click login button
    driver.find_element(By.ID, "login_button").click()
    time.sleep(3)


# Function to make a post
def make_post(content):
    driver.get(post_url)
    time.sleep(2)

    # Find the post form (adjust the selectors based on the actual page)
    driver.find_element(By.ID, "post_content_field").send_keys(content)
    driver.find_element(By.ID, "post_button").click()
    time.sleep(2)
    print(f"Posted: {content}")


# Function to like a post
def like_post(post_id):
    driver.get(like_url + f"?post_id={post_id}")
    time.sleep(2)
    # Find like button (adjust the selectors based on the actual page)
    driver.find_element(By.ID, f"like_button_{post_id}").click()
    time.sleep(2)
    print(f"Liked post with ID: {post_id}")


# Function to dislike a post
def dislike_post(post_id):
    driver.get(dislike_url + f"?post_id={post_id}")
    time.sleep(2)
    # Find dislike button (adjust the selectors based on the actual page)
    driver.find_element(By.ID, f"dislike_button_{post_id}").click()
    time.sleep(2)
    print(f"Disliked post with ID: {post_id}")


# Function to follow a user
def follow_user(user_id):
    driver.get(profile_url + f"/{user_id}")
    time.sleep(2)

    # Find the "Follow" button (adjust the selector based on the actual page)
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

    # Find the "Unfollow" button (adjust the selector based on the actual page)
    unfollow_button = driver.find_element(By.ID, f"unfollow_button_{user_id}")
    if unfollow_button.text == "Unfollow":  # Ensure it's not already unfollowed
        unfollow_button.click()
        time.sleep(2)
        print(f"Unfollowed user with ID: {user_id}")
    else:
        print(f"Already unfollowed user with ID: {user_id}")


# Main automation loop
def main():
    # Register a new user
    register_user(username, email, password)

    # Log in after registration
    login()

    # Post content to simulate creating a post
    make_post("This is a test post.")

    # Simulate liking and disliking posts by post ID
    post_id_to_like = 12345
    post_id_to_dislike = 12346

    like_post(post_id_to_like)
    dislike_post(post_id_to_dislike)

    # Follow and unfollow actions by user ID
    user_id_to_follow = 7890
    user_id_to_unfollow = 7891

    follow_user(user_id_to_follow)
    unfollow_user(user_id_to_unfollow)

    # Close the browser when done
    driver.quit()


if __name__ == "__main__":
    main()
