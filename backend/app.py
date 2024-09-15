from flask import Flask, request, jsonify
from raspberry import process_query  # Import the process_query function from raspberry.py
from ai_handler import ai_gen

app = Flask(__name__)

# Try to import and use CORS, but continue without it if not available
try:
    from flask_cors import CORS
    CORS(app)
    print("CORS has been enabled")
except ImportError:
    print("CORS is not available. The API may not work correctly with frontend applications on different domains.")

# Chat endpoint that processes user queries using raspberry.py
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    print(f"Received data: {data}")  # Log the received data

    if not data:
        print("No data received in request.")
        return jsonify({'error': 'No data received'}), 400

    # Extract the latest user message from the messages array
    messages = data.get('messages', [])
    user_message = None

    for message in messages:
        if message['role'] == 'user':
            user_message = message['content']

    if not user_message:
        print("No user message provided in the data.")
        return jsonify({'error': 'No user message provided'}), 400

    try:
        response, chain_name, thought_chain = process_query(user_message)
        return jsonify({
            'response': response,
            'thought_chain': {
                'name': chain_name,
                'steps': thought_chain
            }
        })
    except Exception as e:
        print(f"Error processing query: {e}")  # Log the error in the terminal
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500



# Test endpoint for basic AI interaction
@app.route('/api/test', methods=['GET'])
def test():
    test_messages = [
        {"role": "user", "content": "Hello! Can you tell me a short joke?"}
    ]

    response = ai_gen(test_messages)

    return jsonify({
        'response': response
    })


if __name__ == '__main__':
    app.run(debug=True)
