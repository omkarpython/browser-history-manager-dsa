"""
Browser History Manager - DSA Mini Project (Stack Data Structure)
Preserves original Stack-based LIFO logic:
- back_stack: Python list where last element is top of stack
- forward_stack: Python list where last element is top of stack
- current_page: String representing active URL, or None
"""

import sys

# Attempt UTF-8 console output for Windows systems
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _safe_print(text):
    """Safely print text handling Windows consoles that don't support full Unicode."""
    try:
        print(text)
    except UnicodeEncodeError:
        safe_text = (
            text.replace("✓", "[+]")
            .replace("✗", "[-]")
            .replace("←", "<-")
            .replace("→", "->")
            .replace("★", "*")
        )
        print(safe_text)


class BrowserHistory:
    def __init__(self):
        # Stack for previously visited pages (Last-In, First-Out)
        self.back_stack = []

        # Stack for pages available through Forward (Last-In, First-Out)
        self.forward_stack = []

        # Current page
        self.current_page = None

    # 1. Visit a new website
    def visit_website(self, url):
        if not url or not str(url).strip():
            return False, "URL cannot be empty."

        clean_url = str(url).strip()

        # If a current page exists, push it onto back_stack
        if self.current_page is not None:
            self.back_stack.append(self.current_page)

        # Set the new URL as current_page
        self.current_page = clean_url

        # Forward history is cleared when a new page is visited
        self.forward_stack.clear()

        _safe_print(f"\n✓ Visited: {self.current_page}")
        return True, f"Visited: {self.current_page}"

    # 2. Go back
    def go_back(self):
        if not self.back_stack:
            _safe_print("\n✗ No previous page available.")
            return False, "No previous page available."

        # Move current page to forward stack
        self.forward_stack.append(self.current_page)

        # Get previous page from back stack (Pop top of stack)
        self.current_page = self.back_stack.pop()

        _safe_print(f"\n← Going back")
        _safe_print(f"Current Page: {self.current_page}")
        return True, f"Navigated back to {self.current_page}"

    # 3. Go forward
    def go_forward(self):
        if not self.forward_stack:
            _safe_print("\n✗ No forward page available.")
            return False, "No forward page available."

        # Move current page to back stack (Push current page)
        self.back_stack.append(self.current_page)

        # Get page from forward stack (Pop top of stack)
        self.current_page = self.forward_stack.pop()

        _safe_print(f"\n→ Going forward")
        _safe_print(f"Current Page: {self.current_page}")
        return True, f"Navigated forward to {self.current_page}"

    # 4. Display current page
    def show_current_page(self):
        if self.current_page is None:
            _safe_print("\n✗ No page is currently open.")
            return None, "No page is currently open."
        else:
            _safe_print(f"\nCurrent Page: {self.current_page}")
            return self.current_page, f"Current Page: {self.current_page}"

    # 5. Display complete history
    def display_history(self):
        _safe_print("\n========== BROWSING HISTORY ==========")

        is_empty = not self.back_stack and self.current_page is None and not self.forward_stack

        if is_empty:
            _safe_print("History is empty.")
        else:
            _safe_print("\nPreviously Visited:")
            if self.back_stack:
                for i, page in enumerate(reversed(self.back_stack), 1):
                    _safe_print(f"{i}. {page}")
            else:
                _safe_print("No previous pages.")

            if self.current_page:
                _safe_print(f"\n★ Current Page: {self.current_page}")

            _safe_print("\nForward History:")
            if self.forward_stack:
                for i, page in enumerate(reversed(self.forward_stack), 1):
                    _safe_print(f"{i}. {page}")
            else:
                _safe_print("No forward pages.")

        return {
            "previously_visited": list(reversed(self.back_stack)),
            "current_page": self.current_page,
            "forward_history": list(reversed(self.forward_stack)),
            "back_stack": list(self.back_stack),
            "forward_stack": list(self.forward_stack),
            "is_empty": is_empty
        }

    # 6. Clear all history
    def clear_history(self):
        self.back_stack.clear()
        self.forward_stack.clear()
        self.current_page = None

        _safe_print("\n✓ Browser history cleared.")
        return True, "Browser history cleared."

    # Helper: Get current state for API representation
    def get_state(self):
        return {
            "current_page": self.current_page,
            "back_stack": list(self.back_stack),
            "forward_stack": list(self.forward_stack),
            "can_go_back": len(self.back_stack) > 0,
            "can_go_forward": len(self.forward_stack) > 0,
            "back_count": len(self.back_stack),
            "forward_count": len(self.forward_stack)
        }


# Main CLI program for terminal execution
def main():
    browser = BrowserHistory()

    while True:
        print("\n")
        print("=" * 45)
        print("        BROWSER HISTORY MANAGER")
        print("=" * 45)

        print("1. Visit Website")
        print("2. Go Back")
        print("3. Go Forward")
        print("4. Current Page")
        print("5. Display History")
        print("6. Clear History")
        print("7. Exit")

        print("=" * 45)

        choice = input("Enter your choice: ")

        if choice == "1":
            url = input("Enter website URL: ")
            if url.strip() == "":
                print("\n✗ URL cannot be empty.")
            else:
                browser.visit_website(url)

        elif choice == "2":
            browser.go_back()

        elif choice == "3":
            browser.go_forward()

        elif choice == "4":
            browser.show_current_page()

        elif choice == "5":
            browser.display_history()

        elif choice == "6":
            browser.clear_history()

        elif choice == "7":
            print("\nThank you for using Browser History Manager!")
            break

        else:
            print("\n✗ Invalid choice. Please try again.")


# Start the program in terminal
if __name__ == "__main__":
    main()
