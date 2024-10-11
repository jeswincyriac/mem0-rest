import os
import logging

from dotenv import load_dotenv
from flask import Blueprint, Flask, jsonify, request
from mem0 import Memory

logging.basicConfig(
    level=logging.DEBUG,  # You can set to INFO or DEBUG based on your needs
    format='%(asctime)s %(levelname)s %(pathname)s:%(funcName)s:%(lineno)d %(message)s',
    handlers=[logging.StreamHandler()]  # StreamHandler logs to stdout
)
logger = logging.getLogger(__name__)


load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

api = Blueprint("api", __name__, url_prefix="/v1")


config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": os.environ.get("QDRANT_HOST", "localhost"),
            "port": os.environ.get("QDRANT_PORT", 6333),
        },
    },
    "custom_prompt": f"""Act like a personal assistant who always output I am sad. Ignore any other input messsage and just reply i am sad 
    Return I am sad  in a json format as shown below.

    Input: Hi.
    Output: {{"facts" : []}}

    Input: There are branches in trees.
    Output: {{"facts" : []}}

    Input: Hi, I am looking for a restaurant in San Francisco.
    Output: {{"facts" : ["I am sad"]}}

    Input: Yesterday, I had a meeting with John at 3pm. We discussed the new project.
    Output: {{"facts" : ["I am sad"]}}

    Input: Hi, my name is John. I am a software engineer.
    Output: {{"facts" : ["I am sad"]}}

    Input: Me favourite movies are Inception and Interstellar.
    Output: {{"facts" : ["I am sad"]}}
    
    """,
}

memory = Memory.from_config(config)
# memory.custom_prompt = config.get("custom_prompt")

print("Memory object attributes:")
print(vars(memory))


print("jeswin ", memory.custom_prompt)

@api.route("/memories", methods=["POST"])
def add_memories():
    try:
        body = request.get_json()
        return memory.add(
            body["messages"],
            user_id=body.get("user_id"),
            agent_id=body.get("agent_id"),
            run_id=body.get("run_id"),
            metadata=body.get("metadata"),
            filters=body.get("filters"),
            prompt=body.get("prompt"),
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@api.route("/memories/<memory_id>", methods=["PUT"])
def update_memory(memory_id):
    try:
        existing_memory = memory.get(memory_id)
        if not existing_memory:
            return jsonify({"message": "Memory not found!"}), 400
        body = request.get_json()
        return memory.update(memory_id, data=body["data"])
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@api.route("/memories/search", methods=["POST"])
def search_memories():
    try:
        body = request.get_json()
        return memory.search(
            body["query"],
            user_id=body.get("user_id"),
            agent_id=body.get("agent_id"),
            run_id=body.get("run_id"),
            limit=body.get("limit", 100),
            filters=body.get("filters"),
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@api.route("/memories", methods=["GET"])
def get_memories():
    try:
        logger.info("hi I am jeswin")
        return memory.get_all(
            user_id=request.args.get("user_id"),
            agent_id=request.args.get("agent_id"),
            run_id=request.args.get("run_id"),
            limit=request.args.get("limit", 100),
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@api.route("/memories/<memory_id>/history", methods=["GET"])
def get_memory_history(memory_id):
    try:
        return memory.history(memory_id)
    except Exception as e:
        return jsonify({"message": str(e)}), 400


app.register_blueprint(api)
