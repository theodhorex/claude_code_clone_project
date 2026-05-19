import os
import json
import subprocess
import re
from pathlib import Path
from anthropic import Anthropic
from typing import Optional, Dict, Any

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    base_url="https://agentrouter.org"
)
conversation_history = []

# MINIMAL system prompt - reduce token usage
SYSTEM_PROMPT = """You are a code assistant. Help with file/command operations.

When executing an action, provide JSON:
```json
{"action": "read_file|write_file|edit_file|command", "details": {...}}
```

Be brief."""

class AgentError(Exception):
    pass

def execute_command(cmd: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute PowerShell/bash command."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[:1500],
            "stderr": result.stderr[:500],
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stderr": "Timeout"}
    except Exception as e:
        return {"success": False, "stderr": str(e)[:200]}

def read_file(path: str) -> Dict[str, Any]:
    """Read file - optimized."""
    try:
        path = Path(path).resolve()
        if not path.exists():
            return {"success": False, "stderr": f"Not found: {path}"}

        if path.is_dir():
            items = list(path.iterdir())
            files = [f.name for f in items if f.is_file()][:15]
            return {
                "success": True,
                "type": "dir",
                "files": files
            }

        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(8000)
        return {
            "success": True,
            "type": "file",
            "path": str(path),
            "content": content
        }
    except Exception as e:
        return {"success": False, "stderr": str(e)[:150]}

def write_file(path: str, content: str) -> Dict[str, Any]:
    """Write file."""
    try:
        path = Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": str(path)}
    except Exception as e:
        return {"success": False, "stderr": str(e)[:150]}

def edit_file(path: str, old_text: str, new_text: str) -> Dict[str, Any]:
    """Edit file."""
    try:
        path = Path(path).resolve()
        if not path.exists():
            return {"success": False, "stderr": "Not found"}

        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        if old_text not in content:
            return {"success": False, "stderr": "Text not found"}

        new_content = content.replace(old_text, new_text, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return {"success": True, "path": str(path)}
    except Exception as e:
        return {"success": False, "stderr": str(e)[:150]}

def extract_json_from_response(response_text: str) -> Optional[Dict]:
    """Extract first JSON action from response."""
    # Look for ```json block
    json_pattern = r'```json\s*(.*?)\s*```'
    match = re.search(json_pattern, response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass

    # Fallback: raw JSON
    try:
        start = response_text.find('{"action"')
        if start >= 0:
            depth = 0
            for i, char in enumerate(response_text[start:]):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        return json.loads(response_text[start:start + i + 1])
    except:
        pass

    return None

def execute_action(action_data: Dict) -> Dict[str, Any]:
    """Execute action from JSON."""
    action = action_data.get("action")
    details = action_data.get("details", {})

    if action == "command":
        cmd = details.get("cmd") or details.get("command")
        if not cmd:
            return {"success": False, "stderr": "No cmd"}
        print(f"   💻 {cmd[:60]}")
        return execute_command(cmd)

    elif action == "read_file":
        path = details.get("path")
        if not path:
            return {"success": False, "stderr": "No path"}
        print(f"   📖 {path[:50]}")
        return read_file(path)

    elif action == "write_file":
        path = details.get("path")
        content = details.get("content", "")
        if not path:
            return {"success": False, "stderr": "No path"}
        print(f"   ✍️  {path[:50]}")
        return write_file(path, content)

    elif action == "edit_file":
        path = details.get("path")
        old_text = details.get("old_text", "")
        new_text = details.get("new_text", "")
        if not path or not old_text:
            return {"success": False, "stderr": "Missing params"}
        print(f"   ✏️  {path[:50]}")
        return edit_file(path, old_text, new_text)

    return {"success": False, "stderr": f"Unknown: {action}"}

def stream_chat(user_message: str):
    """Chat with streaming - optimized."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Keep only last 20 turns (40 messages) to save tokens
    if len(conversation_history) > 40:
        # Remove oldest pair
        conversation_history.pop(0)
        conversation_history.pop(0)

    try:
        # Non-streaming to avoid content-blocked issues
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=conversation_history
        )

        full_response = response.content[0].text
        print(full_response)
        print()

        conversation_history.append({
            "role": "assistant",
            "content": full_response
        })

        return full_response

    except Exception as e:
        conversation_history.pop()
        raise AgentError(f"Error: {str(e)[:100]}")

def main():
    """Main loop."""
    print("=" * 70)
    print("🚀 Claude Agent v2.1 OPTIMIZED - Streaming + Token Efficient")
    print("=" * 70)
    print("\nQuick commands: baca | buat | edit | jalanin | debug | exit\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() == "exit":
                print("Goodbye! 👋")
                break

            if not user_input:
                continue

            print("\n")
            response = stream_chat(user_input)

            # Check for action
            action_data = extract_json_from_response(response)

            if action_data:
                print("\n" + "-" * 70)
                approve = input("✅ Execute? (y/n): ").strip().lower()

                if approve == 'y':
                    print()
                    result = execute_action(action_data)

                    # Compact result for sending back
                    result_str = json.dumps(result, ensure_ascii=False)[:500]
                    print(f"\n📊 Result: {result_str}\n")

                    # Brief feedback from Claude
                    print("Processing...\n")
                    stream_chat(f"Action result: {result_str}. Brief summary & next step?")
                else:
                    print("❌ Cancelled\n")
            else:
                print()

        except AgentError as e:
            print(f"❌ {str(e)}\n")
        except KeyboardInterrupt:
            print("\n\nInterrupted.\n")
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}\n")

if __name__ == "__main__":
    main()
