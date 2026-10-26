from playwright.sync_api import expect


class RolesPage:
    def __init__(self, page):
        self.page = page

    def open(self, base_url):
        self.page.goto(base_url)
        expect(self.page.get_by_role("heading", name="Roles", exact=True)).to_be_visible()

    def create(self, name):
        self.page.get_by_label("Role name", exact=True).fill(name)
        with self.page.expect_response(
            lambda response: response.url.endswith("/api/roles")
            and response.request.method == "POST"
        ) as result:
            self.page.get_by_role("button", name="Create role", exact=True).click()
        response = result.value
        assert response.status == 201
        return response.json()["id"]

    def expect_role(self, name):
        expect(self.page.get_by_role("listitem").filter(has_text=name)).to_have_text(name)

    def expect_empty(self):
        expect(self.page.get_by_text("No roles found", exact=True)).to_be_visible()
