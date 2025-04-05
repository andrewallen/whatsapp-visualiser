import re
import os
from flask import Flask, render_template, url_for

app = Flask(__name__)

CHAT_EXPORT_DIR = "WhatsApp Chat - Tough Mudder"
# Correctly join 'static', the export dir, and the filename
CHAT_FILE_PATH = os.path.join("static", CHAT_EXPORT_DIR, "_chat.txt")
MEDIA_FOLDER = os.path.join('static', CHAT_EXPORT_DIR) # Store media in static for serving

def parse_chat_file(file_path):
    messages = []
    current_date = None

    # Regex for standard messages: [DD/MM/YYYY, HH:MM:SS] Sender: Message
    # Made sender part non-greedy and message part greedy
    message_pattern = re.compile(
        r'^\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.+?): (.*)$', re.DOTALL
    )
    # Regex for system messages (joining, creating group, etc.)
    system_pattern = re.compile(
        r'^\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*)$'
    )
    # Regex for media attachments - use search to find it anywhere in the message
    media_pattern = re.compile(r'<attached: (.+?)>')
    # Regex for date separators (assuming they are on their own line like DD/MM/YYYY)
    date_separator_pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4})$')

    print(f"Attempting to read chat file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            line_num = 0
            for line in file:
                line_num += 1
                # *** Ensure LRM is removed from the START of the line FIRST ***
                line = line.lstrip('\u200e').strip()
                print(f"\n--- Processing Line {line_num}: {line[:100]}...") # Print start of line

                if not line: # Skip empty lines
                    print("Skipping empty line.")
                    continue

                # Check for date separator first
                date_sep_match = date_separator_pattern.match(line)
                if date_sep_match:
                    date_str = date_sep_match.group(1)
                    # Attempt to standardise date format if needed (e.g., YYYY from YY)
                    # For simplicity, we'll just use the matched string for now
                    if date_str != current_date:
                         print(f"Found Date Separator: {date_str}")
                         messages.append({'type': 'date_separator', 'text': date_str})
                         current_date = date_str # Update current date based on separator
                    continue # Move to next line after handling date separator


                # Check for standard message format
                msg_match = message_pattern.match(line)
                if msg_match:
                    date, time, sender, message_text = msg_match.groups()
                    # Still remove LRM from sender/text just in case, though start-of-line was main issue
                    sender = sender.replace('\u200e', '').strip()
                    message_text = message_text.replace('\u200e', '').strip()

                    print(f"Matched Standard Message: Date={date}, Time={time}, Sender='{sender}', Text='{message_text[:50]}...'")

                    if date != current_date:
                         # Check if a date separator was *just* added for this date
                         if not messages or messages[-1].get('text') != date or messages[-1].get('type') != 'date_separator':
                            print(f"Adding implicit Date Separator: {date}")
                            messages.append({'type': 'date_separator', 'text': date})
                         current_date = date

                    # Check for media within the message text using search
                    media_match = media_pattern.search(message_text)
                    if media_match:
                        filename = media_match.group(1).strip()
                        print(f"Found Media: '{filename}'")
                        media_path = url_for('static', filename=os.path.join(CHAT_EXPORT_DIR, filename))
                        media_type = 'unknown'
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            media_type = 'image'
                        elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                            media_type = 'video'
                        elif filename.lower().endswith('.webp'): # Treat webp as stickers/images
                            media_type = 'sticker'


                        # Extract caption (text before/after the media tag)
                        # Replacing the found tag, then stripping.
                        caption = message_text.replace(media_match.group(0), '').strip()
                        print(f"Media Type: {media_type}, Path: {media_path}, Caption: '{caption}'")

                        messages.append({
                            'type': 'media',
                            'date': date,
                            'time': time,
                            'sender': sender,
                            'media_path': media_path,
                            'media_type': media_type,
                            'caption': caption
                        })
                    elif message_text: # Only add if there's actual text content left
                        print("Added as Text Message.")
                        messages.append({
                            'type': 'text',
                            'date': date,
                            'time': time,
                            'sender': sender,
                            'text': message_text
                        })
                    else:
                         print("Media matched, but no remaining text, skipping separate text message add.")

                else:
                    # Attempt to match system messages
                    sys_match = system_pattern.match(line)
                    if sys_match:
                        date, time, sys_text = sys_match.groups()
                        sys_text = sys_text.strip()
                        print(f"Matched System Message: '{sys_text}'")
                        # Optional: Add date separator if date changed
                        if date != current_date:
                            if not messages or messages[-1].get('text') != date or messages[-1].get('type') != 'date_separator':
                                print(f"Adding implicit Date Separator: {date}")
                                messages.append({'type': 'date_separator', 'text': date})
                            current_date = date

                        messages.append({'type': 'system', 'text': sys_text, 'date': date, 'time': time})
                    # Handle potential multi-line messages (append to previous message if conditions met)
                    elif messages and line and messages[-1]['type'] == 'text':
                        print(f"Appending to previous message: {line[:50]}...")
                        messages[-1]['text'] += '\n' + line
                    else:
                        print(f"Line did not match any pattern: {line[:100]}")


    except FileNotFoundError:
        print(f"Error: Chat file not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error parsing chat file: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        return None

    print("\nParsing complete.")
    if not messages:
        print("Warning: No messages were parsed.")
    else:
        print(f"Successfully parsed {len(messages)} items (messages/separators).")

    return messages


@app.route('/')
def index():
    messages = parse_chat_file(CHAT_FILE_PATH)
    if messages is None:
        return "Error reading or parsing chat file. Check console for details.", 500
    # Use the directory name as the title (can be refined later if needed)
    chat_title = CHAT_EXPORT_DIR
    return render_template('index.html', messages=messages, chat_title=chat_title)

if __name__ == '__main__':
    app.run(debug=True)
