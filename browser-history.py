class BrowserHistory:
    def __init__(self):
        # Stack for previously visited pages
        self.back_stack = []

        # Stack for pages available through Forward
        self.forward_stack = []

        # Current page
        self.current_page = None

    # Visit a new website
    def visit_website(self, url):
        if self.current_page is not None:
            self.back_stack.append(self.current_page)

        self.current_page = url

        # Forward history is cleared when a new page is visited
        self.forward_stack.clear()

        print(f"\n✓ Visited: {url}")

    # Go back
    def go_back(self):
        if not self.back_stack:
            print("\n✗ No previous page available.")
            return

        # Move current page to forward stack
        self.forward_stack.append(self.current_page)

        # Get previous page from back stack
        self.current_page = self.back_stack.pop()

        print(f"\n← Going back")
        print(f"Current Page: {self.current_page}")

    # Go forward
    def go_forward(self):
        if not self.forward_stack:
            print("\n✗ No forward page available.")
            return

        # Move current page to back stack
        self.back_stack.append(self.current_page)

        # Get page from forward stack
        self.current_page = self.forward_stack.pop()

        print(f"\n→ Going forward")
        print(f"Current Page: {self.current_page}")

    # Display current page
    def show_current_page(self):
        if self.current_page is None:
            print("\n✗ No page is currently open.")
        else:
            print(f"\nCurrent Page: {self.current_page}")

    # Display complete history
    def display_history(self):
        print("\n========== BROWSING HISTORY ==========")

        if not self.back_stack and self.current_page is None:
            print("History is empty.")
            return

        print("\nPreviously Visited:")

        if self.back_stack:
            for i, page in enumerate(reversed(self.back_stack), 1):
                print(f"{i}. {page}")
        else:
            print("No previous pages.")

        if self.current_page:
            print(f"\n★ Current Page: {self.current_page}")

        print("\nForward History:")

        if self.forward_stack:
            for i, page in enumerate(reversed(self.forward_stack), 1):
                print(f"{i}. {page}")
        else:
            print("No forward pages.")

    # Clear all history
    def clear_history(self):
        self.back_stack.clear()
        self.forward_stack.clear()
        self.current_page = None

        print("\n✓ Browser history cleared.")


# Main program
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


# Start the program
if __name__ == "__main__":
    main()