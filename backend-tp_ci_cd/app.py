import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://appuser:apppassword@db:3306/appdb",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


with app.app_context():
    db.create_all()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "backend"})


@app.route("/api/items", methods=["GET"])
def get_items():
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])


@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400
    item = Item(name=data["name"], description=data.get("description", ""))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
