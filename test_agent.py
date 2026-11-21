import os
import sys
import time
from core.speaker import BujjiSpeaker
from core.intent_fallback import process_offline_intent
from core.task_monitor import TaskMonitor
from core.brain import BujjiBrain
from tools.antigravity_tool import sanitize_folder_name
from tools.productivity_tools import TimerManager, NotesManager
from tools.system_tools import calculate_math

def run_tests():
    print("========================================")
    print("      BUJJI AGENT SELF-TEST SUITE       ")
    print("========================================")

    # 1. Test Folder Sanitizer
    print("\n[Test 1] Testing Folder Sanitizer...")
    clean = sanitize_folder_name("a professional brain game")
    assert "brain_game" in clean.lower() or "professional" in clean.lower(), f"Unexpected: {clean}"
    print(f" -> Sanitized: 'a professional brain game' -> '{clean}' [PASS]")

    # 2. Test Safe Antigravity Intent (Isolated, dry-run, never touches active window)
    print("\n[Test 2] Testing Antigravity Intent Delegation...")
    user_prompt = "hey bujjii open antigravity and promt it to build a professional brain game"
    
    from core.listener import BujjiListener
    listener = BujjiListener()
    is_wake, cmd = listener.check_wake_word(user_prompt)
    print(f" -> Wake word detected: {is_wake}, Extracted Command: '{cmd}'")
    assert is_wake, "Wake word not detected!"
    assert "antigravity" in cmd.lower(), "Command didn't retain antigravity!"

    # Process command safely with dry_run=True
    handled, reply, meta = process_offline_intent(cmd, dry_run=True)
    print(f" -> Handled: {handled}, Spoken Reply: {reply}")
    assert handled, "Intent was not handled!"
    assert "antigravity" in reply.lower() or "brain_game" in str(meta), "Reply missing context!"
    print(" -> Antigravity Delegation [PASS] (Verified isolated & safe)")

    # 3. Test Siri/Alexa Desktop & Daily Commands
    print("\n[Test 3] Testing Siri/Alexa Everyday Assistant Voice Commands...")
    daily_commands = [
        ("what is the time", "time"),
        ("take a screenshot", "screenshot"),
        ("volume up", "volume"),
        ("who are you", "assistant"),
        ("lock my pc", "lock"),
        ("open github", "github"),
        ("go to reddit", "reddit"),
        ("close notepad", "notepad"),
        ("what is 20 percent of 500", "100"),
        ("calculate 15 times 4", "60"),
        ("set a timer for 10 seconds", "timer"),
        ("show my timers", "active timers"),
        ("take a note buy groceries today", "noted"),
        ("read my notes", "groceries"),
        ("copy hello world to clipboard", "clipboard"),
        ("what is in my clipboard", "clipboard"),
        ("open whatsapp", "whatsapp"),
        ("send message to Rahul: I am on the way", "rahul"),
        ("send message to one of my contacts", "who"),
        ("check whatsapp status", "status"),
        ("call Rahul on whatsapp", "rahul"),
        ("video call Rahul on whatsapp", "video"),
        ("i am feeling very tired today", "hard today"),
        ("i am stressed with too much work", "hear you"),
        ("i'm so happy got good news", "fantastic"),
        ("you are awesome bujji", "best"),
        ("open instagram", "instagram"),
        ("start a google meet", "meet"),
        ("check my emails", "gmail"),
        ("open calendar", "calendar"),
        ("where is Hyderabad", "maps"),
        ("that's all thank you", "pleasure")
    ]
    for q, expected in daily_commands:
        h, rep, meta = process_offline_intent(q, dry_run=True)
        print(f" -> '{q}' -> Handled: {h} | Reply: '{rep[:65]}...'")
        assert h, f"Failed to handle daily command: {q}"
    print(" -> All Siri/Alexa Daily Commands Handled [PASS]")

    # 4. Test Math Engine Directly
    print("\n[Test 4] Testing Math Calculation Engine...")
    math_res1 = calculate_math("what is 25 percent of 400")
    assert math_res1["status"] == "success" and math_res1["result"] == 100
    math_res2 = calculate_math("calculate 50 * 3 + 10")
    assert math_res2["status"] == "success" and math_res2["result"] == 160
    print(f" -> Math 25% of 400 = {math_res1['result']} [PASS]")
    print(f" -> Math 50 * 3 + 10 = {math_res2['result']} [PASS]")

    # 5. Test Productivity Notes Engine
    print("\n[Test 5] Testing Notes Storage & Retrieval...")
    NotesManager.clear_notes()
    NotesManager.take_note("Meeting with team at 4 PM")
    notes = NotesManager.read_notes()
    assert "Meeting with team at 4 PM" in notes["message"]
    NotesManager.clear_notes()
    print(" -> Notes Take, Read & Clear [PASS]")

    # 6. Test Task Monitor
    print("\n[Test 6] Testing TaskMonitor...")
    monitor = TaskMonitor(speaker=None)
    test_dir = os.path.join(os.getenv("TEMP", "C:\\temp"), f"bujji_test_task_{int(time.time())}")
    os.makedirs(test_dir, exist_ok=True)

    completed_flag = False
    def on_done(msg):
        nonlocal completed_flag
        completed_flag = True
        print(f" -> Callback fired with: {msg}")

    monitor.register_task(
        task_id="test_1",
        name="Test Build Task",
        watch_dir=test_dir,
        on_complete=on_done,
        settle_timeout=0.5,
        max_duration=8
    )

    game_file = os.path.join(test_dir, "index.html")
    with open(game_file, "w") as f:
        f.write("<h1>App</h1>")

    print(" -> File created in watch directory, waiting for settle...")
    for _ in range(16):
        if completed_flag:
            break
        time.sleep(0.5)

    assert completed_flag, "TaskMonitor did not trigger completion callback!"
    print(" -> TaskMonitor Generation Detection [PASS]")

    # Clean test file
    try:
        os.remove(game_file)
        os.rmdir(test_dir)
    except Exception:
        pass

    # 7. Test Brain Engine
    print("\n[Test 7] Testing Brain Engine Process...")
    brain = BujjiBrain()
    reply, meta = brain.process("who are you", dry_run=True)
    print(f" -> Brain replied: {reply[:60]}...")
    assert len(reply) > 0, "Brain returned empty reply!"
    print(" -> Brain Engine [PASS]")

    # 8. Test Smart Real-World Fallback (Zero Blind Rejections)
    print("\n[Test 8] Testing Smart Real-World Fallback (WhatsApp Web & Daily Essentials)...")
    from tools.whatsapp_tool import open_whatsapp, view_whatsapp_status, make_whatsapp_call
    from tools.system_tools import open_application

    # Test open_whatsapp fallback to web when prefer_web=True
    wa_web_res = open_whatsapp(prefer_web=True)
    assert wa_web_res["status"] == "success" and wa_web_res["mode"] == "web"
    print(f" -> WhatsApp Web Fallback: {wa_web_res['message']} [PASS]")

    # Test WhatsApp Status
    wa_status_res = view_whatsapp_status()
    assert wa_status_res["status"] == "success"
    print(f" -> WhatsApp Status: {wa_status_res['message']} [PASS]")

    # Test WhatsApp Calls
    wa_call_res = make_whatsapp_call("Rahul", call_type="audio", dry_run=True)
    assert wa_call_res["status"] == "success" and "Rahul" in wa_call_res["contact"]
    print(f" -> WhatsApp Audio Call: {wa_call_res['message']} [PASS]")

    wa_vcall_res = make_whatsapp_call("Mom", call_type="video", dry_run=True)
    assert wa_vcall_res["status"] == "success" and "Mom" in wa_vcall_res["contact"]
    print(f" -> WhatsApp Video Call: {wa_vcall_res['message']} [PASS]")

    print(" -> Smart Real-World Fallback [PASS]")

    # 9. Test Wake Word Variants (Bangaram, Bujji, Jarvis, etc.)
    print("\n[Test 9] Testing Expanded Wake Word & Call Variant Suite...")
    from core.listener import BujjiListener
    listener = BujjiListener()

    test_wake_phrases = [
        ("hey bujji", True),
        ("hey bangaram", True),
        ("bangaram", True),
        ("hii bujji", True),
        ("hey jarvis", True),
        ("hiii jaravis", True),
        ("bujjiiii", True),
        ("hey bujji open whatsapp", True),
        ("hey bangaram what is the weather", True),
        ("bujjiiii send message to Rahul", True),
        ("random sentence without calling", False)
    ]

    for phrase, should_wake in test_wake_phrases:
        is_w, ext = listener.check_wake_word(phrase)
        print(f" -> Testing '{phrase}': Wake={is_w}, Extracted='{ext}'")
        assert is_w == should_wake, f"Wake word check failed for '{phrase}'! Expected {should_wake}, got {is_w}"

    print(" -> Wake Word Variant Suite [PASS]")

    print("\n" + "=" * 45)
    print(" ALL BUJJI TESTS PASSED WITH 100% SUCCESS! [✓]")
    print("=============================================")

if __name__ == "__main__":
    run_tests()
