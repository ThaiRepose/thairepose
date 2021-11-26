from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.urls import reverse
from planner.models import Plan, MAX_DAYS_PER_PLAN


def login(browser: webdriver, url: str, username: str, password: str) -> webdriver:
    """Login with specified username and password.

    Args:
        browser: browser object that is initialized.
        url: login url.
        username: user's username.
        password: user's password.

    Returns:
        browser object that is logged in.
    """
    browser.get(url)
    username_box = browser.find_element_by_xpath('//*[@id="id_login"]')
    username_box.send_keys(username)
    password_box = browser.find_element_by_xpath('//*[@id="id_password"]')
    password_box.send_keys(password)
    # click login button
    browser.find_element_by_xpath('/html/body/div/div[1]/div/div/div/div[2]/form/div[3]/button').click()
    return browser


class E2ETestPlanner(StaticLiveServerTestCase):
    """Tests for Planner app."""

    def setUp(self):
        """Setting up browser."""
        self.url = self.live_server_url
        # create user and login
        self.user_detail = {"username": "Tawan", "password": "ThaiRepose"}
        self.user = User.objects.create_user(username=self.user_detail['username'], password=self.user_detail['password'])
        self.user.save()

        # Initialize webdriver
        options = Options()
        options.add_argument("--headless")
        self.browser = webdriver.Firefox(
            executable_path="/Users/tawaneiei/Desktop/KU/ISP/selenium-exercise/geckodriver", options=options)
        self.browser = login(self.browser, self.url + reverse("account_login"),
                             self.user_detail['username'], self.user_detail['password'])
        self.browser.implicitly_wait(2)  # seconds

    def tearDown(self):
        self.browser.quit()
        super(E2ETestPlanner, self).tearDown()

    def test_planner_creation(self):
        """Test that the planner can be created."""
        self.browser.get(self.url + reverse("planner:index"))
        # create new planner button
        self.browser.find_element_by_xpath('/html/body/div/div[1]/div/div[2]/div/a').click()
        self.browser.implicitly_wait(2)

    def test_increase_day(self):
        """Test increasing day in trip planner."""
        plan = Plan.objects.create(author=self.user)
        plan.save()
        self.browser.get(self.url + reverse("planner:edit_plan", args=[plan.id]))
        # find increase day button
        increase_btn = self.browser.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[1]/div[1]/div[2]/div/button[2]')
        increase_btn.click()
        # from instance of 1 is default, after clicked 1 time should display 2
        displayed_days = self.browser.find_element_by_xpath('//*[@id="days-selector"]').get_attribute("value")
        self.assertEqual(int(displayed_days), 2)

        # test that increase days is limited to MAX_DAYS_PER_PLAN
        for i in range(10):
            increase_btn.click()
        # get planned day again, the day should not more than MAX_DAYS_PER_PLAN. If so, it should be MAX_DAYS_PER_PLAN
        displayed_days = self.browser.find_element_by_xpath('//*[@id="days-selector"]').get_attribute("value")
        self.assertEqual(int(displayed_days), MAX_DAYS_PER_PLAN)

    def test_decrease_day(self):
        """Test decreasing days in trip planner."""
        plan = Plan.objects.create(author=self.user)
        plan.save()
        self.browser.get(self.url + reverse("planner:edit_plan", args=[plan.id]))
        # increase the day first before decreasing
        increase_btn = self.browser.find_element_by_xpath(
            '/html/body/div[1]/div[1]/div/div[1]/div[1]/div[2]/div/button[2]')
        for i in range(3):
            increase_btn.click()
        # get number of days after increased
        initial_days = self.browser.find_element_by_xpath('//*[@id="days-selector"]').get_attribute("value")

        # decrease the day
        decrease_btn = self.browser.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[1]/div[1]/div[2]/div/button[1]')
        decrease_btn.click()
        displayed_days = self.browser.find_element_by_xpath('//*[@id="days-selector"]').get_attribute("value")
        self.assertEqual(int(initial_days) - 1, int(displayed_days))

        # test that number of days is in range of positive integer and should be 1.
        for i in range(int(displayed_days) + 4):
            decrease_btn.click()
        displayed_days = self.browser.find_element_by_xpath('//*[@id="days-selector"]').get_attribute("value")
        self.assertEqual(int(displayed_days), 1)
