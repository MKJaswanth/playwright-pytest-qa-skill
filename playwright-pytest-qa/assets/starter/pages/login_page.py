import re

from playwright.sync_api import expect


class LoginPage:
    def __init__(self, page):
        self.page = page

    def open(self, base_url):
        self.page.goto(f"{base_url}/login")
        expect(self.page.get_by_role("heading", name="Sign in", exact=True)).to_be_visible()

    def sign_in(self, base_url, email, password):
        self.open(base_url)
        self.page.get_by_label("Email", exact=True).fill(email)
        self.page.get_by_label("Password", exact=True).fill(password)
        self.page.get_by_role("button", name="Sign in", exact=True).click()
        expect(self.page).to_have_url(re.compile(r"/dashboard$"))
