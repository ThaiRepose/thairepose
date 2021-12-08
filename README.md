![workflow](https://github.com/ThaiRepose/thairepose/actions/workflows/django.yml/badge.svg)
[![codecov](https://codecov.io/gh/ThaiRepose/thairepose/branch/beta/graph/badge.svg?token=uocBU8wW8W)](https://codecov.io/gh/ThaiRepose/thairepose)
# ThaiRepose
**ThaiRepose** website is a web application that helps to find areas that users want to travel and it can help people to make decisions for making trips. People who don't even have any experience planning a trip before, it can help them to easily plan a trip. ThaiRepose.com will be a community for people who love to travel.

## Project Documents
- [Project Proposal](https://docs.google.com/document/d/1mOMiqBmQl6vW7RYVQD6Gk-mEcFnmdsmku2gpTglZRmE)
- [Requirements](../../wiki/Requirements)    
- [Vision Statement](../../wiki/Vision%20Statement)    
- [Project checklist (Google Docs)](https://docs.google.com/document/d/12oLF6wH6xnCxpRtHZMbSnVHXy6lJ3YwSO2AbnYKVLAI/)    
- [Code Checklist](../../wiki/Code%20Checklist)    
- [Code Review Procedure](../../wiki/Code%20Review%20Procedure)
- [Final Presentation slide](https://docs.google.com/presentation/d/17DhKn9v1_Z8-Y42ZlklcQsP6VWc2__LadO0pAYsPKhg)

## Getting Started
### Requirements
|Name  | Recommended version(s)|   
|------|-----------------------|
|Python | 3.9 or higher |
|Django | 3 or higher |

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
   <details>
    <summary>If you're using Windows</summary>
    Run this command to install caching system.

    ```
    pip install --editable src\caching\.
    ```
   </details>


6. Create `.env` file in the same level as manage.py and write down:

   ```
   DEBUG=True
   SECRET_KEY=Your-Secret-Key
   HOSTS=localhost,127.0.0.1
   BACKEND_API_KEY=Your-Google-API-key-in-server-side
   FRONTEND_API_KEY=Your-Google-API-key-in-client-side
   EMAIL_HOST_USER=email-for-send-verification-form 
   EMAIL_HOST_PASSWORD=email-password
   EMAIL_PORT=Your-configured-email-port
   EMAIL_HOST=Your-email-provider-host
   EMAIL_USE_TLS=TLS-using-true-or-false
   EMAIL_USE_SSL=SSL-using-true-or-false
   SITE_ID=1
   ```
   <details>
   <summary>Example email configuration:</summary>     
    
   - [Gmail](https://www.lifewire.com/what-are-the-gmail-smtp-settings-1170854)
   - [Outlook](https://getmailspring.com/setup/access-hotmail-com-via-imap-smtp)
   
     **Warning: If you use Gmail you have to adjust to less secure**
   </details>

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
    python manage.py migrate --run-syncdb
    ```
10. Start running caching system.
    ```
    tr-caching start
    ```
11. Start running the server by this command in another terminal.
    ```
    python manage.py runserver
    ```
12. Add Oauth API Key in Admin page in social app (e.g. in local: http://127.0.0.1:8000/admin/socialaccount/socialapp/) 
    - Add provider.
    - Add client id and secret key that retrieve form API owner.
    - Add site to chosen sites.

    <details>
    <summary>Instruction of getting OAuth API Key:</summary>     
    
    - [For all provider](https://django-allauth.readthedocs.io/en/latest/providers.html)    
    - [Another Example for Google](https://www.ibm.com/docs/en/app-connect/cloud?topic=gmail-connecting-google-application-by-providing-credentials-app-connect-use-basic-oauth)
    </details>


## Team Members
| Name | Github  |
|------|:-------:|
| Tawan Boonma | [☕️ tboonma](https://github.com/tboonma) |
| Tanin Pewluangsawat | [💤 TaninDean](https://github.com/TaninDean) |
| Vitvara Varavithya | [💦 vitvara](https://github.com/vitvara) |
| Nabhan Suwanachote | [ ☔ nabhan-au](https://github.com/nabhan-au) |

