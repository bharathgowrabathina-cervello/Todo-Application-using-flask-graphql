from ariadne.explorer import ExplorerPlayground
from flask import Flask, request, jsonify
from ariadne import gql, QueryType, MutationType, make_executable_schema, graphql_sync, snake_case_fallback_resolvers
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import requests
import json

PLAYGROUND_HTML = ExplorerPlayground(title="Cool API").html(None)

# Define type definitions (schema) using SDL
type_defs = gql(
   """
   type Query {
       places: [Place]
   }


   type Place {
       name: String!
       description: String!
       country: String!
       }  

   type Mutation{
    add_place(name: String!, description: String!, country: String!): Place!}
   """
)

# Initialize query

query = QueryType()

# Initialize mutation

mutation = MutationType() # MutationType() is just a shortcut for ObjectType("Mutation").
# mutation.set_field("add_place", mutation.add_place)


# Define resolvers

# places resolver (return places )
# @query.field("places")
# def places(*_):
#    return places

# # place resolver (add new  place)
# @mutation.field("add_place")
# def add_place(_, info, name, description, country):
#    places.append({"name": name, "description": description, "country": country})
#    return {"name": name, "description": description, "country": country}


# places resolver (return places )
@query.field("places")
def places(*_):
   return [place.to_json() for place in Places.query.all()]

# place resolver (add new  place)
@mutation.field("add_place")
def add_place(_, info, name, description, country):
   print("11111111111111111")
   place = Places(name=name, description=description, country=country)
   print("-----------------")
   print(place)
   place.save()
   return place.to_json()

# Create executable schema
# schema = make_executable_schema(type_defs, [query, mutation])
schema = make_executable_schema(type_defs, query, mutation, snake_case_fallback_resolvers)

# initialize flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Places(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(80), nullable=False)
   description = db.Column(db.String(255), nullable=False)
   country = db.Column(db.String(80), nullable=False)

   def to_json(self):
       return {
           "name": self.name,
           "description": self.description,
           "country": self.country,
       }

   def save(self):
       db.session.add(self)
       db.session.commit()

# Create a GraphQL Playground UI for the GraphQL schema
@app.route("/graphql", methods=["GET"])
def graphql_playground():
   # Playground accepts GET requests only.
   # If you wanted to support POST you'd have to
   # change the method to POST and set the content
   # type header to application/graphql
   return PLAYGROUND_HTML

# Create a GraphQL endpoint for executing GraphQL queries
@app.route("/graphql", methods=["POST"])
def graphql_server():
   data = request.get_json()
   print("************")
   # data = request.get_data()
   print(data)
   success, result = graphql_sync(
                     schema, 
                     data, 
                     context_value=request
                     )
   # res = requests.post(
   #          f"http://127.0.0.1:5000/graphql",
   #          data = data,
   #          headers={
   #              "Content-Type": "application/json",
   #              "Accept": "application/json",
   #          },
   #      )
   status_code = 200 if success else 400
   
   # response =  json.loads(res.text)
   # return {
   #          "success": True,
   #          "data": response["data"],
   #      }
   return jsonify(result), status_code

# @app.route("/add-place", methods=["POST"])
# def add_lecture():
#    data = request.get_json()
#    db.session.add(Places(name=data["name"], description=data["description"], country=data["country"]))
#    db.session.commit()
#    return jsonify({"message":"Place added successfully"})

@app.route("/", methods=["GET"])
def home_page():
   return "<h1>Hello World</h1>"

# Run the app
if __name__ == "__main__":
   # places = [
   #     {"name": "Paris", "description": "The city of lights", "country": "France"},
   #     {"name": "Rome", "description": "The city of pizza", "country": "Italy"},
   #     {
   #         "name": "London",
   #         "description": "The city of big buildings",
   #         "country": "United Kingdom",
   #     },
   # ]
   app.run(debug=True)


