# it has to have to have a ruote
# it has to have a method (get/put/post/delete)
# it has to have a status code(200,201,403)
# it has to return data as Json(key :value pair)

from flask import Flask,request,jsonify
import json

app = Flask(__name__)

@app.route("/")
def home():
    if request.method == "GET":
        data = {"flask Api": "Version 1"}
        return jsonify (data),200
    else:
        error={"Error":"Method not allowed"}

        return jsonify(error),403


app.run(debug=True)


