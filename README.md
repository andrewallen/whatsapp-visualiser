# WhatsApp Chat Visualiser

This tool visualises an exported WhatsApp chat log in a web interface designed to resemble the WhatsApp application.

## Features

- Displays text messages, system messages (like group creation, adding users), and date separators.
- Shows sender names and timestamps for each message.
- Differentiates between your messages ('outgoing') and others' messages ('incoming') based on a predefined name (currently 'Andrew Allen' - **you may need to edit `templates/index.html` to change this to your name as it appears in the chat export**).
- Displays attached images and videos inline.
- Basic WhatsApp-like styling.

## Setup

1.  **Prerequisites:**
    *   Python 3.x installed.
    *   pip (Python package installer).

2.  **Clone or Download:**
    *   Place the code files (`app.py`, `requirements.txt`, `templates/`, `static/`) in a project directory.

3.  **Place Chat Export:**
    *   You should have a directory containing your WhatsApp export (e.g., `WhatsApp Chat - Tough Mudder`). This directory must contain the `_chat.txt` file and all associated media files mentioned within it.
    *   **IMPORTANT:** Create a `static` directory in your project folder if it doesn't exist.
    *   **Copy or move** your entire WhatsApp export directory (e.g., `WhatsApp Chat - Tough Mudder`) **inside** the `static` directory. The structure should look like this:
        ```
        your-project-directory/
        ├── app.py
        ├── requirements.txt
        ├── templates/
        │   └── index.html
        ├── static/
        │   ├── style.css
        │   └── WhatsApp Chat - Tough Mudder/  <-- Your export folder here
        │       ├── _chat.txt
        │       ├── image1.jpg
        │       ├── video1.mp4
        │       └── ... (other media files)
        └── README.md
        ```
    *   If your export directory has a different name, you **must** update the `CHAT_EXPORT_DIR` variable at the top of `app.py` to match exactly.

4.  **Install Dependencies:**
    *   Open a terminal or command prompt in `your-project-directory`.
    *   Run: `pip install -r requirements.txt`

## Running the Visualiser

1.  **Start the Server:**
    *   In the terminal (still in `your-project-directory`), run: `python app.py`
    *   You should see output indicating the Flask server is running, typically on `http://127.0.0.1:5000/`.

2.  **View in Browser:**
    *   Open your web browser and navigate to the URL provided (e.g., `http://127.0.0.1:5000/`).
    *   You should see your WhatsApp chat displayed.

## Notes & Limitations

*   **Outgoing Message Detection:** Currently hardcoded in `templates/index.html` to identify messages from "Andrew Allen" as outgoing. You'll likely need to change this to your name.
*   **Parsing Robustness:** The message parsing relies on regular expressions based on the typical WhatsApp export format. Unusual message formats or variations might not parse correctly.
*   **Media Types:** Currently handles common image and video formats (jpg, png, gif, webp, mp4). Other media types might not display correctly.
*   **Performance:** Very large chat files might take longer to load.
*   **Styling:** Basic CSS is provided; further refinements can be made in `static/style.css`.
