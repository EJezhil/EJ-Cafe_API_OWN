from flask import Flask, render_template, redirect, url_for, request, jsonify
from sqlalchemy import Update, Delete
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///cafes.db")
app.app_context().push()

db = SQLAlchemy()
db.init_app(app)


class Cafe_API(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


db.create_all()


@app.route('/')
def home():
    return render_template("usage.html")


@app.route('/random')
def random():
    result = db.session.execute(db.select(Cafe_API))
    results = result.scalar()
    print(results)

    if results is None:
        dict = {
        "cafe": [
        ]
        }
    else:
        dict = {
            "cafe": {
                "id": results.id,
                "name": results.name,
                "map_url": results.map_url,
                "img_url": results.img_url,
                "location": results.location,
                "seats": results.seats,
                "has_toilet": results.has_toilet,
                "has_wifi": results.has_wifi,
                "has_sockets": results.has_sockets,
                "can_take_calls": results.can_take_calls,
                "coffee_price": results.coffee_price
            }
        }
    return jsonify(dict)


@app.route('/all')
def all():
    result = db.session.execute(db.select(Cafe_API))
    results = result.scalars()

    diction2 = {
        "cafe": [
        ]
    }
    for i in results:
        cafe = {
            "id": i.id,
            "name": i.name,
            "map_url": i.map_url,
            "img_url": i.img_url,
            "location": i.location,
            "seats": i.seats,
            "has_toilet": i.has_toilet,
            "has_wifi": i.has_wifi,
            "has_sockets": i.has_sockets,
            "can_take_calls": i.can_take_calls,
            "coffee_price": i.coffee_price
        }
        diction2["cafe"].append(cafe)
    return jsonify(diction2)


@app.route('/search')
def search():
    location = request.args.get('loc')
    results = db.session.execute(db.select(Cafe_API).where(Cafe_API.location == location)).scalars()
    print(results)
    diction3 = {
        "cafe": [
        ]
    }
    for i in results:
        cafe = {
            "id": i.id,
            "name": i.name,
            "map_url": i.map_url,
            "img_url": i.img_url,
            "location": i.location,
            "seats": i.seats,
            "has_toilet": i.has_toilet,
            "has_wifi": i.has_wifi,
            "has_sockets": i.has_sockets,
            "can_take_calls": i.can_take_calls,
            "coffee_price": i.coffee_price
        }

        diction3["cafe"].append(cafe)

    error = {
        "error": {
            "Not Found": "Sorry given location is not found"
        }
    }
    if not diction3["cafe"]:
        return jsonify(error)
    else:
        return jsonify(diction3)


# POST = request.FORM.get
# GET = request.ARGS.get
@app.route('/add', methods=["POST"])
def add():
    name = request.form.get('name')
    map_url = request.form.get('map_url')
    img_url = request.form.get('img_url')
    location = request.form.get('location')
    seats = request.form.get('seats')
    has_toilet = bool(request.form.get('has_toilet'))
    has_wifi = bool(request.form.get('has_wifi'))
    has_sockets = bool(request.form.get('has_sockets'))
    can_take_calls = bool(request.form.get('can_take_calls'))
    coffee_price = request.form.get('coffee_price')

    new_cafe = Cafe_API(name=name, map_url=map_url, img_url=img_url, location=location, seats=seats,
                        has_toilet=has_toilet,
                        has_wifi=has_wifi, has_sockets=has_sockets, can_take_calls=can_take_calls,
                        coffee_price=coffee_price)
    db.session.add(new_cafe)
    db.session.commit()

    diction4 = {
        "response": {
            "success": "successfully added the new cafe"
        }
    }
    return jsonify(diction4)


@app.route('/report-closed', methods=["DELETE"])
def delete():
    id = request.args.get('id')
    api_key = request.args.get('api-key')
    cafe_to_delete = db.session.execute(db.select(Cafe_API).where(Cafe_API.id == id))
    # print(cafe_to_delete)
    cafe_to_deletes = cafe_to_delete.scalar()
    print(cafe_to_deletes)
    if cafe_to_deletes is None:
        diction5 = {
            "Error": {
                "Not found": "No cafe with the given id is present"
            }
        }
        return jsonify(diction5)
    elif api_key != "Secret":
        diction5 = {
            "Error": {
                "Not Allowed": "Api Key is incorrect"
            }
        }
        return jsonify(diction5)
    else:
        db.session.delete(cafe_to_deletes)
        db.session.commit()
        diction5 = {
            "Success": {
                "Done": "Cafe_API deleted from database"
            }
        }
        return jsonify(diction5)


@app.route('/update-price', methods=["PUT"])
def update():
    id = request.args.get('id')
    new_price = request.args.get('new_price')
    cafe_price_to_update = db.session.execute(db.select(Cafe_API).where(Cafe_API.id == id))
    cafe_price_to_updates = cafe_price_to_update.scalar()
    if cafe_price_to_updates is None:
        diction6 = {
            "Error": {
                "Not found": "No cafe with the given id is present"
            }
        }
        return jsonify(diction6)
    else:
        db.session.execute(Update(Cafe_API).where(Cafe_API.id == id).values(coffee_price=new_price))
        db.session.commit()
        diction6 = {
            "Success": {
                "Done": "Cafe_API price updated in the database"
            }
        }
        return jsonify(diction6)


if __name__ == "__main__":
    app.run(debug=True)
