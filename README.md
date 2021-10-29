[![Build Status](https://app.travis-ci.com/ThaiRepose/thairepose.svg?branch=oauth)](https://app.travis-ci.com/ThaiRepose/thairepose)
[![codecov](https://codecov.io/gh/ThaiRepose/thairepose/branch/oauth/graph/badge.svg?token=uocBU8wW8W)](https://codecov.io/gh/ThaiRepose/thairepose)
# ThaiRepose
**ThaiRepose** website is a web application that helps to find areas that users want to travel and it can help people to make decisions for making trips. People who don't even have any experience planning a trip before, it can help them to easily plan a trip. ThaiRepose.com will be a community for people who love to travel.

## Project Documents
- [Project Proposal](https://docs.google.com/document/d/1mOMiqBmQl6vW7RYVQD6Gk-mEcFnmdsmku2gpTglZRmE/edit?usp=sharing)

## Getting Started
### Requirements
|Name  | Recommended version(s)|   
|------|-----------------------|
|Python | 3.7 or higher |
|Django | 2.2 or higher |

### Install Packages
1. Clone this project repository to your machine.

    ```
    git clone https://github.com/ThaiRepose/thairepose.git
    ```
2. Get into the directory of this repository.

    ```
    cd thairepose
    ```
3. Create a virtual environment.

    ```
    python -m venv venv
    ```
4. Activate the virtual environment.

    - for Mac OS / Linux.   
    ```
    source venv/bin/activate
    ```
    - for Windows.   
    ```
    venv\Scripts\activate
    ```
5. Install all required packages.

    ```
    pip install -r requirements.txt
    ```
6. Create `.env` file in the same level as manage.py and write down:

    ```
    DEBUG=True
    SECRET_KEY=Your-Secret-Key
    HOSTS=localhost,127.0.0.1
    EMAIL_FROM_USER = email-for-send-verification-form 
    EMAIL_HOST_PASSWORD = email-password
    ```
    (If you don't use gmail. Please change EMAIL_PORT and EMAIL_HOST in setting)
7. Install TailwindCSS framework.

    ```
    python manage.py tailwind install
    ```
8. Build TailwindCSS frontend framework the get GUI.

    ```
    python manage.py tailwind build
    ```
9. Run this command to migrate the database.

    ```
    python manage.py migrate
    ```
10. Start running the server by this command.
    ```
    python manage.py runserver
    ```
11. Add Oauth API Key
    Go to domain/admin/socialaccount/socialapp/ (local: http://127.0.0.1:8000/admin/socialaccount/socialapp/) 
    - Add Client id and Secret key that retrieve form API owner.
    - Add site to chosen sites.
12. Add location for store profile picture in setting.py
    ```
    PROFILE_PIC_LOCATION = your-storage-path-for-store-picture
    ```
    recommend: project-folder/users/static/profile_pic



## Team Members
| Name | Github  |
|------|:-------:|
| Tawan Boonma | [☕️ tboonma](https://github.com/tboonma) |
| Tanin Pewluangsawat | [💤 TaninDean](https://github.com/TaninDean) |
| Vitvara Varavithya | [💦 vitvara](https://github.com/vitvara) |
| Nabhan Suwanachote | [ ☔ nabhan-au](https://github.com/nabhan-au) |
