from flask import Flask, request, jsonify, Response
from raspberry import process_query, load_thought_chains, construct_chain
from ai_handler import ai_gen
import json

app = Flask(__name__)

try:
    from flask_cors import CORS

    CORS(app)
    print("CORS has been enabled")
except ImportError:
    print("CORS is not available. The API may not work correctly with frontend applications on different domains.")

memory = []


def stream_thought_process(user_query, thought_chain, memory):
    intermediate_output = ""
    print(f"Starting thought process for query: {user_query}")  # Add this line

    for step in thought_chain:
        prompt = f"The user has asked: '{user_query}'. Consider the following step: '{step}'."
        response = ai_gen([{"role": "user", "content": prompt}])
        intermediate_output += f"\nStep '{step}': {response}"

        print(f"Streaming thought: {step}")  # Add this line
        yield f"data: {json.dumps({'thought': step, 'response': response})}\n\n"

    print(f"Streaming final response")  # Add this line
    yield f"data: {json.dumps({'final_response': intermediate_output})}\n\n"


@app.route('/api/chat', methods=['GET'])  # Changed to GET
def chat():
    user_message = request.args.get('message')  # Get message from query parameters
    print(f"Received message: {user_message}")  # Add this line

    if not user_message:
        print("No user message provided in the data.")
        return jsonify({'error': 'No user message provided'}), 400

    try:
        global memory

        thought_chains = load_thought_chains()
        thought_chain, chain_name = construct_chain(thought_chains, None)

        print(f"Constructed thought chain: {thought_chain}")  # Add this line

        return Response(stream_thought_process(user_message, thought_chain, memory),
                        content_type='text/event-stream')
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)