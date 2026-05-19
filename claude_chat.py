import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    base_url="https://agentrouter.org"
)
conversation_history = []
MAX_HISTORY = 10  # Keep only last 10 messages

def chat(user_message):
    """Send a message and get a response from Claude."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Keep only recent messages to avoid token overflow
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=conversation_history
        )

        assistant_message = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message
    except Exception as e:
        # Remove last user message if request failed
        conversation_history.pop()
        raise e

def main():
    """Main chat loop."""
    print("Claude Chat (Opus 4.6) - Type 'exit' to quit")
    print("-" * 50)

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            print("Claude: ", end="", flush=True)
            response = chat(user_input)
            print(response)
            print()
        except Exception as e:
            print(f"Error: {str(e)}")
            print()

if __name__ == "__main__":
    main()
