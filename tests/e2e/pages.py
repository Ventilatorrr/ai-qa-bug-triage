"""Page objects for UI areas reused across several browser tests.

Only the bug report form and the project bug list are modelled. Other pages
are used by few scenarios and stay clearer as direct Playwright calls.
Page objects expose locators and user actions; assertions stay in the tests.
"""

import re


class BugForm:
    """New Bug / Edit Bug form, including its pending AI suggestions."""

    def __init__(self, page):
        self.page = page
        self.title = page.get_by_label("Title:", exact=True)
        self.environment = page.get_by_label("Environment:", exact=True)
        self.description = page.get_by_label("Description:", exact=True)
        self.severity = page.get_by_label("Severity:", exact=True)
        self.priority = page.get_by_label("Priority:", exact=True)
        self.assignee = page.get_by_label("Assignee:", exact=True)
        self.fix_version = page.get_by_label("Fix Version:", exact=True)
        self.ai_assist = page.get_by_role("button", name="AI Assist", exact=True)
        self.create = page.get_by_role("button", name="Create", exact=True)
        self.save = page.get_by_role("button", name="Save", exact=True)
        self.cancel = page.get_by_role("button", name="Cancel", exact=True)

    def suggestion(self, field):
        return self.page.get_by_role("article", name=f"AI suggestion: {field}", exact=True)

    def use_suggestion(self, field):
        self.page.get_by_role("button", name=f"Use {field} suggestion", exact=True).click()

    def dismiss_suggestion(self, field):
        self.page.get_by_role("button", name=f"Dismiss {field} suggestion", exact=True).click()

    def use_all(self):
        self.page.get_by_role("button", name="Use All", exact=True).click()

    def dismiss_all(self):
        self.page.get_by_role("button", name="Dismiss All", exact=True).click()


class BugList:
    """Project page bug report table with its sort, page-size and pagination controls."""

    def __init__(self, page):
        self.page = page
        self.table = page.get_by_role("table")
        # Includes the header row: N listed reports render N + 1 rows.
        self.rows = self.table.get_by_role("row")
        self.page_size = page.get_by_label("Bugs per page:")
        self.previous_page = page.get_by_role("button", name="Previous", exact=True)
        self.next_page = page.get_by_role("button", name="Next", exact=True)

    def sort_by(self, column):
        # The active sort button appends a direction arrow to the column name.
        self.page.get_by_role("button", name=re.compile(f"^{re.escape(column)}")).click()

    def column_header(self, column):
        return self.page.get_by_role("columnheader", name=column, exact=True)
