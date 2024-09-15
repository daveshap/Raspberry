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
def build_prompt(user_query, thought_chain):
    # Start the prompt with the user query
    prompt = f"The user has asked: '{user_query}'. To guide your response, consider the following steps in your reasoning process:\n\n"

    # Add steps from the thought chain
    for step in thought_chain:
        prompt += f"- {step}: Please incorporate this step into your reasoning.\n"

    # Conclude the prompt
    prompt += "\nPlease provide a well-reasoned response incorporating these steps."

    return prompt


# Main function to process the user query and output the response
def process_query(user_query):
    # Load the thought chains and thought map
    thought_chains = load_thought_chains()
    thought_map = load_thought_map()

    # Construct the best matching thought chain
    thought_chain, chain_name = construct_chain(thought_chains, thought_map)

    # Build a prompt based on the thought chain
    prompt = build_prompt(user_query, thought_chain)

    # Call Claude using the ai_handler function and pass the constructed prompt
    response = ai_gen([{"role": "user", "content": prompt}])

    return response, chain_name, thought_chain


# Looping main function for continuous user input and testing
if __name__ == "__main__":
    print("Welcome to the Raspberry. Type 'exit' to quit.\n")

    while True:
        # Get user input
        user_query = input("Enter your query: ")

        if user_query.lower() == 'exit':
            print("Exiting Chain of Thought Tester.")
            break

        # Process the query and output the response
        response, chain_name, thought_chain = process_query(user_query)

        # Display the response and the chain used
        print(f"\nClaude's Response:\n{response}\n")
        print(f"Thought Chain Used: {chain_name}")
        print(f"Chain Steps: {thought_chain}\n")
