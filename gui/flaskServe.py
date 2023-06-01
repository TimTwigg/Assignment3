from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import time
from src.query import Queryier, CacheStrategy

app = Flask(__name__)
CORS(app)
Q = Queryier("indexLarge", cacheStrategy = CacheStrategy.POPULARITY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search/")
def query():
    q = request.args.get("query")
    start = time.time_ns()
    res, count = Q.searchIndex(q)
    end = time.time_ns()
    response = {
        "results": res,
        "time": (end-start) / 10**6,
        "count": count
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run()