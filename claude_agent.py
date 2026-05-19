import os
import json
import subprocess
from pathlib import Path
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    base_url="https://agentrouter.org"
)
conversation_history = []

SYSTEM_PROMPT = """Kamu adalah Claude Agent yang bisa membantu dengan:
- Menjalankan command (PowerShell/bash)
- Membaca file
- Menulis/mengedit file

Format action JSON saat diminta user:
{"action": "command|read_file|write_file|edit_file", "details": {...}}

Jelaskan action FIRST, baru berikan JSON.
"""

def execute_command(cmd):
    """Execute PowerShell/bash command."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": True,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def read_file(path):
    """Read file content."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return {"success": True, "content": f.read()}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(path, content):
    """Write/create file."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"File created/updated: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def edit_file(path, old_text, new_text):
    """Edit file by replacing text."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if old_text not in content:
            return {"success": False, "error": "Text not found in file"}
        new_content = content.replace(old_text, new_text, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return {"success": True, "message": "File edited successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_action(action_json_str):
    """Parse and execute action from Claude."""
    try:
        action_data = json.loads(action_json_str)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}

    action = action_data.get("action")
    details = action_data.get("details", {})

    if action == "command":
        cmd = details.get("cmd")
        desc = details.get("description", "Execute command")
        print(f"\n📋 Action: {desc}")
        print(f"   Command: {cmd}")
        return execute_command(cmd)

    elif action == "read_file":
        path = details.get("path")
        desc = details.get("description", "Read file")
        print(f"\n📖 Action: {desc}")
        print(f"   Path: {path}")
        return read_file(path)

    elif action == "write_file":
        path = details.get("path")
        content = details.get("content", "")
        desc = details.get("description", "Write file")
        print(f"\n✍️  Action: {desc}")
        print(f"   Path: {path}")
        return write_file(path, content)

    elif action == "edit_file":
        path = details.get("path")
        old = details.get("old_text", "")
        new = details.get("new_text", "")
        desc = details.get("description", "Edit file")
        print(f"\n✏️  Action: {desc}")
        print(f"   Path: {path}")
        return edit_file(path, old, new)

    return {"error": "Unknown action"}

def chat_with_agent(user_message):
    """Send message to Claude Agent."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Limit history
    if len(conversation_history) > 20:
        conversation_history.pop(0)

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=conversation_history
        )

        assistant_message = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message
    except Exception as e:
        conversation_history.pop()
        return f"Error: {str(e)}"

def main():
    """Main agent loop."""
    print("=" * 60)
    print("Claude Agent - Dengan File/Command Execute Capability")
    print("=" * 60)
    print("Type 'exit' untuk quit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("\n🤔 Claude sedang thinking...")
        response = chat_with_agent(user_input)
        print(f"\nClaude: {response}\n")

        # Check if Claude suggested an action
        if '{"action"' in response:
            print("-" * 60)
            # Extract JSON dari response
            try:
                start = response.find('{"action"')
                end = response.find('}', start) + 1
                if start >= 0 and end > start:
                    action_json = response[start:end]

                    # Ask for approval
                    approve = input("\nApprove this action? (y/n): ").strip().lower()

                    if approve == 'y':
                        result = execute_action(action_json)
                        print(f"\n✅ Result: {json.dumps(result, indent=2)}\n")

                        # Send result back to Claude
                        result_message = f"Action result: {json.dumps(result)}"
                        print("🤔 Claude processing result...")
                        followup = chat_with_agent(result_message)
                        print(f"Claude: {followup}\n")
                    else:
                        print("❌ Action cancelled\n")
            except Exception as e:
                print(f"Error parsing action: {e}\n")

if __name__ == "__main__":
    main()
