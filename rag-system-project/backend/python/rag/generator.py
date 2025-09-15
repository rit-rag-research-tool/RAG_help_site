def generate_response(prompt):
    import openai
    import os

    # Load the OpenAI API key from environment variables
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Call the OpenAI API to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract and return the generated text
    return response['choices'][0]['message']['content']

def main():
    # Example usage
    prompt = "What are the benefits of using a Retrieval-Augmented Generation system?"
    response = generate_response(prompt)
    print(response)

if __name__ == "__main__":
    main()