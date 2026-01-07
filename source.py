import speech_recognition as sr
import webbrowser
import pyttsx3
import pyaudio
import datetime
import os
import requests
from bs4 import BeautifulSoup
try:
    from googlesearch import search
    _USE_GOOGLE_SEARCH = True
except Exception:
    from duckduckgo_search import ddg
    _USE_GOOGLE_SEARCH = False
import json
import argparse


# recognizer object (it recognizes what we speak)
recognizer = sr.Recognizer()
engine = pyttsx3.init()  # initializing pyttsx3

# When True, `takeCommand` reads from stdin instead of the microphone.
TEST_MODE = False


# speak function (it takes a text and then speaks that)
def speak(text):
    engine.say(text=text)
    engine.runAndWait()


def takeCommand():
    global TEST_MODE
    if TEST_MODE:
        try:
            cmd = input("Type command (or 'exit'): ")
            return cmd.lower()
        except Exception:
            return "none"
    # listen for the wake word "Friday"
    r = sr.Recognizer()
    with sr.Microphone() as src:                                   #taking microphone acess from system
        print("Listening....")
        r.pause_threshold = 1                                      #pause time initilazation
        audio = r.listen(src, phrase_time_limit=2)                 #audio listning
    try:
        print("Recognizing...")
        command = r.recognize_google(audio, language="en-in")
        print(f"You said: {command}")
        return command.lower()
    except Exception as e:
        print(f"Error: {e}")
        return "none"


def load_knowledge():
    try:
        with open('knowledge.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_knowledge(knowledge):
    with open('knowledge.json', 'w') as f:
        json.dump(knowledge, f, indent=4)


def processCommand(command):
    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://google.com")
    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in command:
        speak("Opening LinkedIn")
        webbrowser.open("https://linkedin.com")
    elif "play music" in command:
        speak("Playing music on YouTube")
        webbrowser.open("https://music.youtube.com")
    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {current_time}")
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        speak(f"Today's date is {current_date}")
    elif "shutdown" in command:
        speak("Shutting down the system")
        os.system("shutdown /s /t 1")
    elif "restart" in command:
        speak("Restarting the system")
        os.system("shutdown /r /t 1")
    elif "lock screen" in command:
        speak("Locking the screen")
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif "sleep" in command:
        speak("Putting the system to sleep")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif "hibernate" in command:
        speak("Hibernating the system")
        os.system("rundll32.exe powrprof.dll,SetSuspendState Hibernate")
    elif "log off" in command:
        speak("Logging off the system")
        os.system("shutdown /l")
    elif "open task manager" in command:
        speak("Opening Task Manager")
        os.system("taskmgr")
    elif "open control panel" in command:
        speak("Opening Control Panel")
        os.system("control")
    elif "stop" in command or "exit" in command:
        speak("Goodbye!")
        return False
    else:
        knowledge = load_knowledge()
        if command in knowledge:
            speak(f"From my knowledge: {knowledge[command]}")
        else:
            # Integrate with web AI: search on Google
            speak(f"Searching for {command} on Google")
            query = command
            results = []
            if _USE_GOOGLE_SEARCH:
                results = list(search(query, num_results=1))
            else:
                try:
                    ddg_res = ddg(query, max_results=1)
                    if ddg_res:
                        # duckduckgo_search returns dicts with 'href' or 'url'
                        first = ddg_res[0]
                        url = first.get('href') or first.get('url') or first.get('link')
                        if url:
                            results = [url]
                except Exception:
                    results = []
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            summary = "No summary found."
            if results:
                url = results[0]
                try:
                    resp = requests.get(url, headers=headers, timeout=5)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # Extract summary from meta description
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc and meta_desc.get('content'):
                        summary = meta_desc['content'][:200]
                        if len(meta_desc['content']) > 200:
                            summary += "..."
                    else:
                        # Fallback to first paragraph
                        first_p = soup.find('p')
                        if first_p:
                            summary = first_p.get_text().strip()[:200]
                            if len(first_p.get_text()) > 200:
                                summary += "..."
                    title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
                    speak(f"Top result: {title}")
                    speak(f"Summary: {summary}")
                except Exception as e:
                    speak("Could not fetch the result details")
                    summary = "Could not fetch summary."
                # Open the search page in browser
                webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            else:
                speak("No search results found on Google, searching on Wikipedia")
                wiki_url = f"https://en.wikipedia.org/w/index.php?search={query.replace(' ', '+')}&title=Special%3ASearch&go=Go"
                try:
                    resp = requests.get(wiki_url, headers=headers, timeout=5)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    if resp.url != wiki_url:  # redirected to the page
                        # Extract summary from Wikipedia
                        first_p = soup.find('p', class_='mw-parser-output')
                        if not first_p:
                            first_p = soup.find('p')
                        if first_p:
                            summary = first_p.get_text().strip()[:200]
                            if len(first_p.get_text()) > 200:
                                summary += "..."
                        title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
                        speak(f"From Wikipedia: {title}")
                        speak(f"Summary: {summary}")
                    else:
                        # on search page, get first result
                        result_div = soup.find('div', class_='mw-search-result-heading')
                        if result_div:
                            link = result_div.find('a')
                            if link:
                                title = link.get('title', 'No title')
                                speak(f"Top Wikipedia result: {title}")
                                summary = f"Wikipedia result: {title}"
                            else:
                                speak("No results found on Wikipedia")
                                summary = "No results found on Wikipedia"
                        else:
                            speak("No results found on Wikipedia")
                            summary = "No results found on Wikipedia"
                except Exception as e:
                    speak("Could not search Wikipedia")
                    summary = "Could not search Wikipedia"
                # Open the Wikipedia search page in browser
                webbrowser.open(wiki_url)

                # Store the learned summary
                knowledge[command] = summary
                save_knowledge(knowledge)
                speak("I have learned this information for future reference.")
            return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run in text input test mode (no microphone)")
    args = parser.parse_args()
    if args.test:
        TEST_MODE = True

    speak("Initializing Friday.......")
    while True:
        command = takeCommand()
        if "friday" in command:
            speak("Yes, how can I help you?")
            command = takeCommand()
            cont = processCommand(command)
            if not cont:
                break
        elif command != "none":
            speak("Please start your command with 'Friday'")
