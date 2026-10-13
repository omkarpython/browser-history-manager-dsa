"""
Unit & API Test Suite for Browser History Manager
Tests both DSA Stack logic and Flask REST API endpoints
"""

import sys
import unittest
from browser_history import BrowserHistory
from app import app


class TestBrowserHistoryDSA(unittest.TestCase):
    def setUp(self):
        self.browser = BrowserHistory()

    def test_initial_state(self):
        self.assertIsNone(self.browser.current_page)
        self.assertEqual(self.browser.back_stack, [])
        self.assertEqual(self.browser.forward_stack, [])

    def test_visit_website(self):
        # 1. Visit first website
        success, msg = self.browser.visit_website("https://www.google.com")
        self.assertTrue(success)
        self.assertEqual(self.browser.current_page, "https://www.google.com")
        self.assertEqual(self.browser.back_stack, [])
        self.assertEqual(self.browser.forward_stack, [])

        # 2. Visit second website - first website pushed to back_stack
        success, msg = self.browser.visit_website("https://github.com")
        self.assertTrue(success)
        self.assertEqual(self.browser.current_page, "https://github.com")
        self.assertEqual(self.browser.back_stack, ["https://www.google.com"])
        self.assertEqual(self.browser.forward_stack, [])

        # 3. Visit third website
        success, msg = self.browser.visit_website("https://wikipedia.org")
        self.assertTrue(success)
        self.assertEqual(self.browser.current_page, "https://wikipedia.org")
        self.assertEqual(self.browser.back_stack, ["https://www.google.com", "https://github.com"])

    def test_go_back_and_forward(self):
        self.browser.visit_website("https://site1.com")
        self.browser.visit_website("https://site2.com")
        self.browser.visit_website("https://site3.com")

        # Back to site2
        success, msg = self.browser.go_back()
        self.assertTrue(success)
        self.assertEqual(self.browser.current_page, "https://site2.com")
        self.assertEqual(self.browser.back_stack, ["https://site1.com"])
        self.assertEqual(self.browser.forward_stack, ["https://site3.com"])

        # Back to site1
        success, msg = self.browser.go_back()
        self.assertTrue(success)
        self.assertEqual(self.browser.current_page, "https://site1.com")
        self.assertEqual(self.browser.back_stack, [])
        self.assertEqual(self.browser.forward_stack, ["https://site3.com", "https://site2.com"])

        # Back when empty
        success, msg = self.browser.go_back()
        self.assertFalse(success)
        self.assertIn("No previous page available", msg)

        # Forward to site2
        success, msg = self.browser.go_forward()
        self.assertTrue(success)
        self.assertEqual(self.browser.current_page, "https://site2.com")
        self.assertEqual(self.browser.back_stack, ["https://site1.com"])
        self.assertEqual(self.browser.forward_stack, ["https://site3.com"])

        # Forward to site3
        success, msg = self.browser.go_forward()
        self.assertTrue(success)
        self.assertEqual(self.browser.current_page, "https://site3.com")
        self.assertEqual(self.browser.forward_stack, [])

        # Forward when empty
        success, msg = self.browser.go_forward()
        self.assertFalse(success)
        self.assertIn("No forward page available", msg)

    def test_branching_visit_clears_forward(self):
        self.browser.visit_website("https://site1.com")
        self.browser.visit_website("https://site2.com")
        self.browser.go_back()
        self.assertEqual(len(self.browser.forward_stack), 1)

        # Visiting a new page must clear forward stack
        self.browser.visit_website("https://site-branch.com")
        self.assertEqual(len(self.browser.forward_stack), 0)
        self.assertEqual(self.browser.current_page, "https://site-branch.com")

    def test_clear_history(self):
        self.browser.visit_website("https://site1.com")
        self.browser.visit_website("https://site2.com")
        success, msg = self.browser.clear_history()
        self.assertTrue(success)
        self.assertIsNone(self.browser.current_page)
        self.assertEqual(self.browser.back_stack, [])
        self.assertEqual(self.browser.forward_stack, [])


class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_state_initial(self):
        res = self.app.get("/api/state")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsNone(data["current_page"])
        self.assertEqual(data["back_stack"], [])
        self.assertEqual(data["forward_stack"], [])
        self.assertFalse(data["can_go_back"])
        self.assertFalse(data["can_go_forward"])

    def test_visit_api(self):
        # Empty url
        res = self.app.post("/api/visit", json={"url": ""})
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()["success"])

        # Valid url
        res = self.app.post("/api/visit", json={"url": "https://www.google.com"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["current_page"], "https://www.google.com")

        # Second url
        res = self.app.post("/api/visit", json={"url": "https://github.com"})
        data = res.get_json()
        self.assertEqual(data["current_page"], "https://github.com")
        self.assertEqual(data["back_stack"], ["https://www.google.com"])
        self.assertTrue(data["can_go_back"])

    def test_back_and_forward_api(self):
        self.app.post("/api/visit", json={"url": "https://alpha.com"})
        self.app.post("/api/visit", json={"url": "https://beta.com"})

        # Back
        res = self.app.post("/api/back")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["current_page"], "https://alpha.com")
        self.assertTrue(data["can_go_forward"])

        # Forward
        res = self.app.post("/api/forward")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["current_page"], "https://beta.com")

    def test_history_and_clear_api(self):
        self.app.post("/api/visit", json={"url": "https://one.com"})
        self.app.post("/api/visit", json={"url": "https://two.com"})

        # GET history
        res = self.app.get("/api/history")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["current_page"], "https://two.com")
        self.assertEqual(data["previously_visited"], ["https://one.com"])

        # DELETE history
        res = self.app.delete("/api/history")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsNone(data["current_page"])
        self.assertEqual(data["back_stack"], [])


if __name__ == "__main__":
    unittest.main()
