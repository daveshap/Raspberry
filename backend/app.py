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
    for step in thought_chain:
        prompt = f"""The user has asked: '{user_query}'. 
Consider the following step: '{step}'.

Important guidelines:
1. Think carefully and methodically through each step.
2. Pay attention to each letter when spelling out words.
3. Double-check your work for accuracy.
4. Explain your reasoning clearly at this step.

Your thought for this step:"""

        response = ai_gen([{"role": "user", "content": prompt}])
        intermediate_output += f"\nStep '{step}': {response}"
        yield f"data: {json.dumps({'thought': step, 'response': response})}\n\n"

    # Final response generation
    final_prompt = f"""Based on the analysis: {intermediate_output}
Provide a concise, accurate answer to the user's question: '{user_query}'.
Remember:
1. Double-check your answer for accuracy.
2. Only include relevant information.
3. Provide the correct final count.

Your final response:"""

    final_response = ai_gen([{"role": "user", "content": final_prompt}])
    yield f"data: {json.dumps({'final_response': final_response})}\n\n"



@app.route('/api/chat', methods=['GET'])
def chat():
    user_message = request.args.get('message')
    if not user_message:
        return jsonify({'error': 'No user message provided'}), 400

    try:
        global memory
        thought_chains = load_thought_chains()
        thought_chain, chain_name = construct_chain(thought_chains, user_message)

        return Response(stream_thought_process(user_message, thought_chain, memory),
                        content_type='text/event-stream')
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)