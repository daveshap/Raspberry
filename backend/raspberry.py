import json
from ai_handler import ai_gen
from sentence_transformers import SentenceTransformer, util

# Load the model for semantic similarity
model = SentenceTransformer('all-MiniLM-L6-v2')


# Load the thought chains from JSON file
def load_thought_chains():
    with open('thought_chains.json', 'r') as f:
        return json.load(f)['thought_chains']


def load_thought_dict():
    with open('thought_dict.json', 'r') as f:
        return json.load(f)['thought_dictionary']


def load_abstract_thought_dict():
    with open('abstract_thought_dict.json', 'r') as f:
        return json.load(f)['abstract_thought_dictionary']


# Function to construct the thought chain based on the user's query using semantic similarity
def construct_chain(thought_chains, user_query):
    # Encode the user's query
    query_embedding = model.encode(user_query, convert_to_tensor=True)

    # Initialize variables
    best_match_chain = None
    highest_similarity = -1

    for chain in thought_chains:
        # Encode the chain description
        description_embedding = model.encode(chain['description'], convert_to_tensor=True)
        # Compute similarity
        similarity = util.pytorch_cos_sim(query_embedding, description_embedding).item()

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match_chain = chain

    if best_match_chain:
        return best_match_chain['chain'], best_match_chain['name']
    else:
        # Default to a generic chain if no good match is found
        default_chain = thought_chains[0]['chain']
        default_name = thought_chains[0]['name']
        return default_chain, default_name


# Build a prompt based on the constructed thought chain
def build_prompt(user_query, step_description, previous_output=None, memory=[]):
    # Start the prompt with the memory, if available
    prompt = "The following is a conversation between a user and an AI assistant called Raspberry.\n\n"

    for exchange in memory:
        prompt += f"User: {exchange['user']}\nAI: {exchange['ai']}\n"

    # Add the current query and previous output
    if previous_output:
        prompt += f"\nThe user has asked: '{user_query}'. Here is what we have so far: '{previous_output}'.\n"
    else:
        prompt += f"\nThe user has asked: '{user_query}'.\n"

    prompt += f"Now, consider the following step: '{step_description}'. Use this step to guide your thinking.\n"

    # Add guidelines to encourage detailed reasoning
    prompt += """
    Important guidelines:
    1. Think carefully and methodically through each step.
    2. Pay close attention to details.
    3. Double-check your work for accuracy.
    4. Explain your reasoning clearly at this step.
    
    Your thought for this step:
    """

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

    # Generate the final response
    final_prompt = f"""Based on the analysis: {intermediate_output}
    Provide a concise, accurate answer to the user's question: '{user_query}'.
    Remember:
    1. Double-check your answer for accuracy.
    2. Only include relevant information.
    3. Provide the correct final answer.
    
    Your final response:"""

    final_response = ai_gen([{"role": "user", "content": final_prompt}])
    all_outputs.append(final_response)

    return final_response, all_outputs


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
    # Load the thought chains
    thought_chains = load_thought_chains()

    # Construct the best matching thought chain using semantic similarity
    thought_chain, chain_name = construct_chain(thought_chains, user_query)

    # Process the thought chain step-by-step with memory
    final_response, all_outputs = process_thought_chain(user_query, thought_chain, memory)

    # Update memory with the new user query and final response
    memory = update_memory(memory, user_query, final_response)

    return final_response, chain_name, thought_chain, all_outputs, memory
