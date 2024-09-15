import json
from ai_handler import ai_gen


# Load the thought chains and thought map from JSON files
def load_thought_chains():
    with open('thought_chains.json', 'r') as f:
        return json.load(f)['thought_chains']


def load_thought_map():
    with open('thought_map.json', 'r') as f:
        return json.load(f)['thought_types']


# Construct a thought chain based on the query
def construct_chain(thought_chains, thought_map):
    # For this version, we'll just select the first matching chain as the default
    if thought_chains:
        return thought_chains[0]['chain'], thought_chains[0]['name']

    # If no chains are defined, construct a new one based on thought_map
    new_chain = [thought['name'] for thought in thought_map[:5]]
    return new_chain, "Custom Chain"


# Build a prompt based on the constructed thought chain
def build_prompt(user_query, step_description, previous_output=None, memory=[]):
    # Start the prompt with the memory, if available
    prompt = "The following is a conversation between a user and an AI.\n\n"

    for exchange in memory:
        prompt += f"User: {exchange['user']}\nAI: {exchange['ai']}\n"

    # Now, add the current query
    if previous_output:
        prompt += f"\nThe user has asked: '{user_query}'. Here is what we have so far: '{previous_output}'.\n"
    else:
        prompt += f"\nThe user has asked: '{user_query}'.\n"

    prompt += f"Now, consider the following step: '{step_description}'. Please provide your reasoning based on this step."

    return prompt


# Process each thought in the chain sequentially with memory
def process_thought_chain(user_query, thought_chain, memory):
    intermediate_output = ""
    all_outputs = []  # To store the output of each step in the chain

    for step in thought_chain:
        # Build the prompt for the current step, incorporating memory
        prompt = build_prompt(user_query, step, intermediate_output, memory)

        # Call the AI model to process this step
        response = ai_gen([{"role": "user", "content": prompt}])

        # Append the response to intermediate_output for the next step
        intermediate_output += f"\nStep '{step}': {response}"
        all_outputs.append(intermediate_output)  # Keep track of each step's output

    # Return the final output after all steps
    return intermediate_output, all_outputs


# Function to manage memory: add new conversation and prune old ones if needed
def update_memory(memory, user_query, ai_response, max_memory=5):
    # Add the latest user query and AI response to memory
    memory.append({"user": user_query, "ai": ai_response})

    # Prune memory if it exceeds the max allowed exchanges
    if len(memory) > max_memory:
        memory.pop(0)  # Remove the oldest exchange to keep memory size in check

    return memory


# Main function to process the user query and output the response
def process_query(user_query, memory):
    # Load the thought chains and thought map
    thought_chains = load_thought_chains()
    thought_map = load_thought_map()

    # Construct the best matching thought chain
    thought_chain, chain_name = construct_chain(thought_chains, thought_map)

    # Process the thought chain step-by-step with memory
    final_response, all_outputs = process_thought_chain(user_query, thought_chain, memory)

    # Update memory with the new user query and final response
    memory = update_memory(memory, user_query, final_response)

    return final_response, chain_name, thought_chain, all_outputs, memory
