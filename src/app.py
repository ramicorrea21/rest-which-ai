"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Tool
import os
import json
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

tool_path = os.path.join(os.path.dirname(__file__), "tools.json")

#populate tools
@app.route("/populate", methods=["GET"])
def personal_population():
    with open(tool_path, "r") as file:
        data = json.load(file)
        file.close

        for tool in data:
            tool = Tool(
                name=tool["name"],
                category=tool["category"],
                creator=tool["creator"],
                website=tool["website"],
                description=tool["description"],
            )
            db.session.add(tool)
            try:
                db.session.commit()
            except Exception as error:
                print("error:", error.args)
                return jsonify("rodo fallo"), 500
        
    return jsonify("todo funciono"), 201
        
#get all tools
@app.route('/tools', methods=['GET'])
def get_tools():
    tools = Tool.query.all()
    return jsonify(list(map(lambda tool : tool.serialize(), tools))), 200

#get tool by id
@app.route('/tools/<int:id>', methods=['GET'])
def get_tool(id):
    tool = Tool.query.filter_by(id=id).one_or_none()
    if tool:
        return jsonify(tool.serialize()), 200
    else: 
        return jsonify({"error":"no tool found"}), 400

#post tool
    
#edit tool
#delete tool


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
