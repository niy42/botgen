import random
from faker import Faker
import json
import time

# Initialize Faker instance
fake = Faker()

# Define a list of random dates of birth, now with 5 additional dates
random_dob = [
    "07/28/2004",
    "04/22/2000",
    "03/17/2003",
    "05/10/1992",
    "09/09/1986",
    "01/15/2001",
    "10/02/1998",
    "08/25/1995",
    "12/07/1993",
    "11/09/1989",
    "02/15/2000",
    "06/05/2002",
    # Additional random dates
    "01/05/1997",
    "08/10/1985",
    "12/11/1999",
    "03/25/1990",
    "07/14/2001",
]


def generate_multiple_users(num_users=1):
    """
    Generates multiple users with random names, emails, passwords, and dates of birth.

    :param num_users: The number of users to generate.
    :return: A list of user dictionaries.
    """
    users = []
    for _ in range(num_users):
        username = fake.user_name()
        email = fake.email()
        password = fake.password(
            length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
        )
        # Use random.choice() to select a random date of birth from the list
        dob = random.choice(random_dob)

        users.append(
            {"username": username, "email": email, "password": password, "dob": dob}
        )

    return users


def save_users_to_file(users, filename="users.json"):
    """
    Saves the generated users to a JSON file.

    :param users: List of user dictionaries.
    :param filename: Name of the file to save the data to.
    """
    # If you want to append to the file instead of overwriting, you can change the mode to 'a'
    try:
        with open(filename, "r") as file:
            existing_users = json.load(file)
    except FileNotFoundError:
        existing_users = []

    existing_users.extend(users)  # Add the new users to the existing list

    with open(filename, "w") as file:
        json.dump(existing_users, file, indent=4)


def main():
    users = []  # List to store the users

    # Run indefinitely to generate users at intervals
    try:
        while True:
            # Generate at least 2 users
            new_users = generate_multiple_users(
                2
            )  # Pass the number of users to generate
            users.extend(new_users)  # Add generated users to the list

            # Save the updated list of users to the file
            save_users_to_file(new_users)
            print(f"Generated 2 users, total users: {len(users)}.")

            # Wait for 30 minutes (1800 seconds) before generating more users
            time.sleep(1800)

    except KeyboardInterrupt:
        print("\nProcess interrupted. Saving users to 'users.json'.")
        save_users_to_file(users)
        print(f"Final count of users: {len(users)}.")


if __name__ == "__main__":
    main()
