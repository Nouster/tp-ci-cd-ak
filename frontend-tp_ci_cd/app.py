import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:5000")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TP CI/CD — Frontend</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f5f5f5; }
    h1 { color: #333; }
    .status { padding: 8px 14px; border-radius: 4px; display: inline-block; margin-bottom: 20px; }
    .ok { background: #d4edda; color: #155724; }
    .error { background: #f8d7da; color: #721c24; }
    form { display: flex; gap: 10px; margin-bottom: 20px; }
    input[type=text] { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
    button { padding: 8px 16px; background: #007bff; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
    button.delete { background: #dc3545; }
    ul { list-style: none; padding: 0; }
    li { background: #fff; padding: 12px 16px; margin-bottom: 8px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
    .flash { padding: 10px; margin-bottom: 16px; border-radius: 4px; background: #fff3cd; color: #856404; }
  </style>
</head>
<body>
  <h1>TP CI/CD — Item Manager</h1>

  <span class="status {{ 'ok' if backend_status == 'ok' else 'error' }}">
    Backend: {{ backend_status }}
  </span>

  {% for msg in messages %}
    <div class="flash">{{ msg }}</div>
  {% endfor %}

  <form method="POST" action="/items">
    <input type="text" name="name" placeholder="Item name" required />
    <input type="text" name="description" placeholder="Description (optional)" />
    <button type="submit">Add Item</button>
  </form>

  <ul>
    {% for item in items %}
    <li>
      <span><strong>{{ item.name }}</strong>{% if item.description %} — {{ item.description }}{% endif %}</span>
      <form method="POST" action="/items/{{ item.id }}/delete">
        <button class="delete" type="submit">Delete</button>
      </form>
    </li>
    {% else %}
    <li>No items yet. Add one above.</li>
    {% endfor %}
  </ul>
</body>
</html>
"""


def get_backend_status():
    try:
        resp = requests.get(f"{BACKEND_URL}/api/health", timeout=3)
        return resp.json().get("status", "error")
    except Exception:
        return "unreachable"


def get_items():
    try:
        resp = requests.get(f"{BACKEND_URL}/api/items", timeout=3)
        return resp.json()
    except Exception:
        return []


@app.route("/")
def index():
    messages = [m for m in (request.args.get("msg"),) if m]
    return render_template_string(
        HTML_TEMPLATE,
        backend_status=get_backend_status(),
        items=get_items(),
        messages=messages,
    )


@app.route("/items", methods=["POST"])
def create_item():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name:
        return redirect(url_for("index", msg="Name is required."))
    try:
        requests.post(
            f"{BACKEND_URL}/api/items",
            json={"name": name, "description": description},
            timeout=3,
        )
    except Exception:
        return redirect(url_for("index", msg="Could not reach backend."))
    return redirect(url_for("index"))


@app.route("/items/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    try:
        requests.delete(f"{BACKEND_URL}/api/items/{item_id}", timeout=3)
    except Exception:
        return redirect(url_for("index", msg="Could not reach backend."))
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
