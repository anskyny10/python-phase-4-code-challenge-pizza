#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
# from flask_sqlalchemy import SQLAlchemy
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class AllRestaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict(only=('address', 'id', 'name')) for restaurant in Restaurant.query.all()]
        # restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)

api.add_resource(AllRestaurants, '/restaurants')

# tried the app.route because I couldn't get RESTFUL to work, but then I realized
# the issue was the serialize_rules...by far the most confusing part for me

# @app.route('/restaurants')
# def all_restaurants():
#     restaurants = Restaurant.query.all()
#     if(not restaurants):
#         return make_response({"message": "No restaurants found"}, 404)
#     restaurants_serial = [restaurant.to_dict(only=('address', 'id', 'name')) for restaurant in Restaurant.query.all()]
#     return make_response(restaurants_serial, 200)
    
class IDRestaurant(Resource):
    
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        # specific format specified in requirements
        restaurant_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [{
                'id': rp.id,
                'pizza': {
                    'id': rp.pizza.id,
                    'name': rp.pizza.name,
                    'ingrdients': rp.pizza.ingredients
                },
                'pizza_id': rp.pizza.id,
                'price': rp.price,
                'restaurant_id': rp.restaurant_id
                }
                # if multiple restaurant_pizzas in the restaurant instance relationship, loop through them
                for rp in restaurant.rest_pizza
            ]
        }
        return make_response(jsonify(restaurant_dict), 200)
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({"message": "Restaurant deleted"}, 204)

api.add_resource(IDRestaurant, '/restaurants/<int:id>')

class AllPizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict(only=('id', 'ingredients', 'name')) for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)
    
api.add_resource(AllPizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_rp = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_rp)
            db.session.commit()
            return make_response(jsonify(new_rp.to_dict()), 201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
