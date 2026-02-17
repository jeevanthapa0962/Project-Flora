import os
import sys
import argparse
import threading 
import time
from dotenv import load_dotenv
from core.voice import speak, listen
from core.registry import SkillRegistry
from core.engine import FloraEngine
from gui.app import run_gui as run_gui_app


# Load Env
load_dotenv(override=True)

groq_key = os.environ.get("GROQ_API_KEY", "").strip().strip('"').strip("'")
if groq_key:
    # Normalize accidental quoting/spacing from .env values.
    os.environ["GROQ_API_KEY"] = groq_key

if not groq_key or groq_key in {"your_key_here", "gsk_your_existing_key_here"}:
    print("Error: GROQ_API_KEY is missing or still set to a placeholder value.")
    print("Update .env with a real key from https://console.groq.com/keys and restart.")
    sys.exit(1)

def flora_loop(pause_event, registry, args):
    """
    Main loop for FLORA, running in a separate thread.
    Checks pause_event to determine if it should listen/process.
    """
    # Initialize Engine
    flora = FloraEngine(registry)

    if args.text:
        print("FLORA: Flora Online. Ready for command (Text Mode).")
    else:
        speak("Flora Online. Ready for command.")

    while True:
        # Check for pause
        if pause_event.is_set():
            time.sleep(0.5)
            continue

        if args.text:
            try:
                user_query = input("YOU: ").lower()
            except EOFError:
                break
        else:
            user_query = listen()
            
        # Double check pause after listening (in case paused during listen)
        if pause_event.is_set():
            continue

        if user_query == "none" or not user_query: continue
        if "quit" in user_query: 
            print("Shutting down FLORA loop...")
            # We can't easily kill the main thread (GUI) from here, 
            # but we can stop this loop. The user will have to close the GUI.
            speak("Shutting down.")
            break
        
        # Wake word / Command filtering Logic
        direct_commands = [
            "open", "volume", "search", "create", "write", "read", "make",
            "who", "what", "when", "where", "how", "why", "thank", "hello"
        ]
        
        is_direct = any(cmd in user_query for cmd in direct_commands)
        
        if "flora" not in user_query and not is_direct:
            print(f"Ignored: {user_query}")
            continue
            
        clean_query = user_query.replace("flora", "").strip()
        
        try:
            print(f"Thinking: {clean_query}")
            response = flora.run_conversation(clean_query)
            
            # Check pause before speaking response
            if pause_event.is_set():
                continue

            if response:
                if args.text:
                    print(f"FLORA: {response}")
                else:
                    speak(response)
        except Exception as e:
            print(f"Main Loop Error: {e}")
            if args.text:
                print("FLORA: System error.")
            else:
                speak("System error.")

def main():
    parser = argparse.ArgumentParser(description="FLORA AI Assistant")
    parser.add_argument("--text", action="store_true", help="Run in text mode (no voice I/O)")
    args = parser.parse_args()

    # 1. Setup Pause Event
    # Event is SET when PAUSED, CLEARED when RUNNING
    pause_event = threading.Event()
    context = {"pause_event": pause_event}

    # 2. Initialize Registry and Load Skills
    registry = SkillRegistry()
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    registry.load_skills(skills_dir, context=context)
    
    # 3. Start FLORA Loop in Background Thread
    # Daemon thread so it dies when GUI closes
    t = threading.Thread(target=flora_loop, args=(pause_event, registry, args), daemon=True)
    t.start()
    
    # 4. Start GUI in Main Thread (Required for PyQt)
    # This will block until the window is closed
    run_gui_app(pause_event)

if __name__ == "__main__":
    main()
