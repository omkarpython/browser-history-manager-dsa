import uuid
from flask import Flask, render_template, request, jsonify, session
from browser_history import BrowserHistory

app = Flask(__name__)
# Secret key for session management
app.secret_key = "dsa_browser_history_manager_secret_key"

# In-memory dictionary to store separate BrowserHistory instance for each user session
# session_id -> BrowserHistory()
session_store = {}


def get_browser():
    """
    Retrieve or initialize the BrowserHistory instance for the current user session.
    Supports cookie session as well as X-Session-ID header for API clients.
    """
    session_id = request.headers.get("X-Session-ID") or session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

    if session_id not in session_store:
        session_store[session_id] = BrowserHistory()

    return session_store[session_id]


@app.route("/")
def index():
    """Render the Browser History Manager website."""
    # Ensure session is created upon initial visit
    get_browser()
    return render_template("index.html")


@app.route("/api/state", methods=["GET"])
def get_state():
    """
    GET /api/state
    Return current page, back stack, and forward stack.
    """
    browser = get_browser()
    state = browser.get_state()
    return jsonify({
        "success": True,
        "current_page": state["current_page"],
        "back_stack": state["back_stack"],
        "forward_stack": state["forward_stack"],
        "can_go_back": state["can_go_back"],
        "can_go_forward": state["can_go_forward"],
        "back_count": state["back_count"],
        "forward_count": state["forward_count"]
    }), 200


@app.route("/api/visit", methods=["POST"])
def visit():
    """
    POST /api/visit
    Accept a URL and execute the Visit Website operation.
    Request body: { "url": "https://www.google.com" }
    """
    browser = get_browser()
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "message": "URL cannot be empty."
        }), 400

    success, message = browser.visit_website(url)
    state = browser.get_state()

    return jsonify({
        "success": success,
        "message": message,
        "current_page": state["current_page"],
        "back_stack": state["back_stack"],
        "forward_stack": state["forward_stack"],
        "can_go_back": state["can_go_back"],
        "can_go_forward": state["can_go_forward"],
        "back_count": state["back_count"],
        "forward_count": state["forward_count"]
    }), 200


@app.route("/api/back", methods=["POST"])
def go_back():
    """
    POST /api/back
    Execute the Go Back operation.
    Pops from back_stack and pushes current page to forward_stack.
    """
    browser = get_browser()
    success, message = browser.go_back()
    state = browser.get_state()

    # Note: Returning 200 with success: false when stack is empty allows frontend
    # to display user-friendly alert message without treating as server error
    return jsonify({
        "success": success,
        "message": message,
        "current_page": state["current_page"],
        "back_stack": state["back_stack"],
        "forward_stack": state["forward_stack"],
        "can_go_back": state["can_go_back"],
        "can_go_forward": state["can_go_forward"],
        "back_count": state["back_count"],
        "forward_count": state["forward_count"]
    }), 200 if success else 400


@app.route("/api/forward", methods=["POST"])
def go_forward():
    """
    POST /api/forward
    Execute the Go Forward operation.
    Pops from forward_stack and pushes current page to back_stack.
    """
    browser = get_browser()
    success, message = browser.go_forward()
    state = browser.get_state()

    return jsonify({
        "success": success,
        "message": message,
        "current_page": state["current_page"],
        "back_stack": state["back_stack"],
        "forward_stack": state["forward_stack"],
        "can_go_back": state["can_go_back"],
        "can_go_forward": state["can_go_forward"],
        "back_count": state["back_count"],
        "forward_count": state["forward_count"]
    }), 200 if success else 400


@app.route("/api/history", methods=["GET"])
def get_history():
    """
    GET /api/history
    Return browsing history, including previously visited, current page, and forward history.
    """
    browser = get_browser()
    history = browser.display_history()

    return jsonify({
        "success": True,
        "current_page": history["current_page"],
        "back_stack": history["back_stack"],
        "forward_stack": history["forward_stack"],
        "previously_visited": history["previously_visited"],
        "forward_history": history["forward_history"],
        "is_empty": history["is_empty"]
    }), 200


@app.route("/api/history", methods=["DELETE"])
def clear_history():
    """
    DELETE /api/history
    Clear the browsing history (clears back_stack, forward_stack, and sets current_page to None).
    """
    browser = get_browser()
    success, message = browser.clear_history()
    state = browser.get_state()

    return jsonify({
        "success": success,
        "message": message,
        "current_page": state["current_page"],
        "back_stack": state["back_stack"],
        "forward_stack": state["forward_stack"],
        "can_go_back": state["can_go_back"],
        "can_go_forward": state["can_go_forward"],
        "back_count": 0,
        "forward_count": 0
    }), 200


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Browser History Manager — Flask Web Server")
    print("  Open in browser: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
