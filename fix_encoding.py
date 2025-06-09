"""
Fix Unicode encoding issues by replacing emojis with safe text
"""

import os
import re

def fix_file_encoding(file_path):
    """Replace emojis with safe text in a file"""
    
    # Emoji to text mapping
    emoji_map = {
        '🔍': '[SEARCH]',
        '📡': '[SERVER]',
        '⏱️': '[TIME]',
        '🛑': '[STOP]',
        '📝': '[LOG]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        'ℹ️': '[INFO]',
        '📂': '[FOLDER]',
        '📊': '[STATS]',
        '📤': '[SEND]',
        '🔄': '[REFRESH]',
        '🎯': '[TARGET]',
        '🚀': '[START]',
        '🧪': '[TEST]',
        '🔗': '[LINK]',
        '💬': '[CHAT]',
        '📋': '[LIST]',
        '🔪': '[KILL]',
        '📄': '[FILE]',
        '🎮': '[GAME]',
        '🖥️': '[DESKTOP]',
        '📱': '[MOBILE]',
        '🌐': '[WEB]',
        '🔧': '[TOOL]',
        '⚙️': '[SETTINGS]',
        '🎉': '[SUCCESS]',
        '🕵️': '[STEALTH]',
        '🛡️': '[SECURITY]',
        '💻': '[COMPUTER]',
        '📈': '[CHART]',
        '🔒': '[LOCK]',
        '🌍': '[GLOBAL]',
        '⭐': '[STAR]',
        '🎯': '[TARGET]',
        '🔥': '[FIRE]',
        '💡': '[IDEA]',
        '🚨': '[ALERT]',
        '📢': '[ANNOUNCE]',
        '🎪': '[CIRCUS]',
        '🎭': '[MASK]',
        '🕐': '[CLOCK]',
        '⏰': '[ALARM]',
        '📅': '[CALENDAR]',
        '📆': '[DATE]',
        '🗂️': '[FOLDER]',
        '📁': '[DIRECTORY]',
        '🗃️': '[ARCHIVE]',
        '🗄️': '[CABINET]',
        '📑': '[DOCUMENT]',
        '📜': '[SCROLL]',
        '📋': '[CLIPBOARD]',
        '📌': '[PIN]',
        '📍': '[LOCATION]',
        '🔖': '[BOOKMARK]',
        '🏷️': '[TAG]',
        '💾': '[SAVE]',
        '💿': '[DISK]',
        '💽': '[MINIDISK]',
        '💻': '[LAPTOP]',
        '🖥️': '[MONITOR]',
        '🖨️': '[PRINTER]',
        '⌨️': '[KEYBOARD]',
        '🖱️': '[MOUSE]',
        '🖲️': '[TRACKBALL]',
        '💡': '[BULB]',
        '🔦': '[FLASHLIGHT]',
        '🕯️': '[CANDLE]',
        '🪔': '[LAMP]',
        '🔥': '[FLAME]',
        '💥': '[EXPLOSION]',
        '💫': '[DIZZY]',
        '💨': '[DASH]',
        '💢': '[ANGER]',
        '💬': '[SPEECH]',
        '💭': '[THOUGHT]',
        '🗯️': '[ANGER_BUBBLE]',
        '♨️': '[HOT_SPRINGS]',
        '💈': '[BARBER]',
        '🛑': '[STOP_SIGN]',
        '🚧': '[CONSTRUCTION]',
        '⚠️': '[WARNING_SIGN]',
        '🚸': '[CHILDREN_CROSSING]',
        '⛔': '[NO_ENTRY]',
        '🚫': '[PROHIBITED]',
        '🚳': '[NO_BICYCLES]',
        '🚭': '[NO_SMOKING]',
        '🚯': '[NO_LITTERING]',
        '🚱': '[NON_POTABLE_WATER]',
        '🚷': '[NO_PEDESTRIANS]',
        '📵': '[NO_MOBILE_PHONES]',
        '🔞': '[NO_ONE_UNDER_EIGHTEEN]',
        '☢️': '[RADIOACTIVE]',
        '☣️': '[BIOHAZARD]',
        '⬆️': '[UP]',
        '↗️': '[UP_RIGHT]',
        '➡️': '[RIGHT]',
        '↘️': '[DOWN_RIGHT]',
        '⬇️': '[DOWN]',
        '↙️': '[DOWN_LEFT]',
        '⬅️': '[LEFT]',
        '↖️': '[UP_LEFT]',
        '↕️': '[UP_DOWN]',
        '↔️': '[LEFT_RIGHT]',
        '↩️': '[LEFT_HOOK]',
        '↪️': '[RIGHT_HOOK]',
        '⤴️': '[UP_CURVE]',
        '⤵️': '[DOWN_CURVE]',
        '🔃': '[CLOCKWISE]',
        '🔄': '[COUNTERCLOCKWISE]',
        '🔙': '[BACK]',
        '🔚': '[END]',
        '🔛': '[ON]',
        '🔜': '[SOON]',
        '🔝': '[TOP]'
    }
    
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace emojis
        for emoji, replacement in emoji_map.items():
            content = content.replace(emoji, replacement)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed encoding in: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix encoding in agent files"""
    files_to_fix = [
        "vercel_client_configs/enhanced_agent.py",
        "enhanced_agent.py",
        "agent_gui.py"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_file_encoding(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
