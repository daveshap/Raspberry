import os
import json
import time
from openai import OpenAI

# Set up the client to point to your local LLM server
client = OpenAI(
    api_key="LMSTUDIO",
    base_url="http://localhost:1234/v1",  # Your local server URL
)

# Load JSON data for domains and task areas
def load_json_data(file_path):
    print(f"Loading JSON file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}. Returning empty list.")
        return []

# Function to generate a novel question
def generate_question(client, domain, task_area, model="gpt-4o-mini"):
    prompt = f"Generate a novel and complex question for the domain '{domain}' and the task area '{task_area}' that requires significant reasoning to answer."
    print(f"Generating question for domain: {domain} and task area: {task_area}")
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    question = response.choices[0].message.content.strip()
    return question

# Function to generate an answer to the question
def generate_response(client, question, model="gpt-4o-mini"):
    print(f"Generating response for question: {question}")
    
    prompt = f"Answer the following novel question: {question}"
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    answer = response.choices[0].message.content.strip()
    return answer

# Function to perform Chain-of-Thought (CoT) grading on the response
def grade_response_cot(client, question, answer, model="gpt-4o-mini"):
    print(f"Grading response for question: {question} using Chain-of-Thought reasoning.")
    
    grading_prompt = (
        f"You are an expert grader tasked with evaluating a response based on chain-of-thought reasoning. "
        f"Evaluate the following answer for logical coherence, reasoning steps, and correctness.\n\n"
        f"Question: {question}\n\nResponse: {answer}\n\n"
        "Grade the response according to these criteria:\n"
        "1. **Logical Coherence**: Does the answer logically follow from the question? Are there clear and valid reasoning steps?\n"
        "2. **Depth of Reasoning**: Does the answer demonstrate deep reasoning, considering multiple aspects of the problem?\n"
        "3. **Correctness**: Is the response factually accurate?\n"
        "4. **Clarity**: Is the response easy to understand and free from ambiguity?\n\n"
        "For each criterion, provide a brief evaluation followed by a score from 1 to 10.\n\n"
        "Please provide the evaluation in the following format:\n"
        '{\n'
        '  "Logical Coherence": {\n'
        '    "evaluation": "<short evaluation blurb>",\n'
        '    "score": <score>\n'
        '  },\n'
        '  "Depth of Reasoning": {\n'
        '    "evaluation": "<short evaluation blurb>",\n'
        '    "score": <score>\n'
        '  },\n'
        '  "Correctness": {\n'
        '    "evaluation": "<short evaluation blurb>",\n'
        '    "score": <score>\n'
        '  },\n'
        '  "Clarity": {\n'
        '    "evaluation": "<short evaluation blurb>",\n'
        '    "score": <score>\n'
        '  }\n'
        '}'
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": grading_prompt}],
        max_tokens=1000
    )
    
    evaluation = response.choices[0].message.content.strip()
    
    try:
        scores = json.loads(evaluation)
        print("Grading results successfully parsed.")
        return scores
    except json.JSONDecodeError:
        print(f"Error parsing grading response: {evaluation}")
        return None

# Function to check if the response meets the quality criteria
def check_grading(scores):
    if not scores:
        return False

    overall_score = sum([scores[category]["score"] for category in scores]) / len(scores)
    
    print(f"Overall Score: {overall_score}\n")
    
    if any(score["score"] < 6 for score in scores.values()) or overall_score < 8:
        print("Content rejected based on Chain-of-Thought grading.")
        return False
    else:
        print("Content accepted based on Chain-of-Thought grading.")
        return True

# Save the results as a JSON file
def save_as_json(question, answer, file_path):
    entry = {
        "prompt": question,
        "response": answer
    }
    append_json_file(entry, file_path)

# Append JSON file
def append_json_file(data, file_path):
    """Save or append JSON content to a file."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    if isinstance(existing_data, list):
        existing_data.append(data)
    else:
        print("Warning: Overwriting non-list data.")
        existing_data = [data]

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4)
    print(f"Data saved to {file_path}.")

# Main function to run the process
def main():
    # Load the JSON file that contains the domain and task area information
    input_file = "domains_and_tasks.json"
    domains_and_tasks = load_json_data(input_file)
    
    output_file = "questions_and_responses.json"

    # Iterate over each domain and task area
    for item in domains_and_tasks:
        domain = item.get("domain")
        task_area = item.get("task_area")
        
        if not domain or not task_area:
            continue
        
        # Step 1: Generate a novel question for the domain and task area
        question = generate_question(client, domain, task_area)
        
        # Step 2: Generate a response to the question
        answer = generate_response(client, question)
        
        # Step 3: Grade the response using Chain-of-Thought grading
        scores = grade_response_cot(client, question, answer)
        
        # Step 4: Check if the response meets the quality criteria
        if check_grading(scores):
            # Step 5: Save the results in JSON format
            save_as_json(question, answer, output_file)
        else:
            print(f"Skipping saving for question: {question}")

        # Pause for a short time between API calls to avoid rate limits
        time.sleep(2)

if __name__ == "__main__":
    main()
