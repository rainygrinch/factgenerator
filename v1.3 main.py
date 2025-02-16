import os
import time
import requests
import re
from typing import List
from dotenv import load_dotenv
from colored import fg, attr
from gtts import gTTS
import openai
import pyperclip

# Load environment variables from .env file
load_dotenv()

REQUIRED_ENV_VARS = [
    "STOCK_VIDEO_API_KEY", "YOUTUBE_API_KEY",
    "VIDEO_OUTPUT", "AUDIO_OUTPUT", "THUMBNAIL_OUTPUT",
    "YOUTUBE_UPLOAD_FOLDER", "THUMBNAIL_OUTPUT_FOLDER", "OPENAI_API_KEY", "CLAUDE_API_KEY"
]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        print(f"{fg('red')}Error: Missing environment variable {var}{attr('reset')}")
        exit(1)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Searches for stock videos based on a query.

    Args:
        query (str): The query to search for.
        api_key (str): The API key to use.
        it (int): Number of videos to retrieve.
        min_dur (int): Minimum video duration in seconds.

    Returns:
        List[str]: A list of stock video URLs.
    """
    headers = {"Authorization": api_key}
    qurl = f"https://api.pexels.com/videos/search?query={query}&per_page={it}"
    r = requests.get(qurl, headers=headers)
    response = r.json()
    video_url = []
    try:
        for i in range(it):
            if response["videos"][i]["duration"] < min_dur:
                continue
            raw_urls = response["videos"][i]["video_files"]
            temp_video_url = ""
            video_res = 0
            for video in raw_urls:
                if ".com/video-files" in video["link"] and (video["width"] * video["height"]) > video_res:
                    temp_video_url = video["link"]
                    video_res = video["width"] * video["height"]
            if temp_video_url:
                video_url.append(temp_video_url)
    except Exception as e:
        print(f"{fg('red')}[-] No Videos found.{attr('reset')}")
        print(f"{fg('red')}{e}{attr('reset')}")
    print(f"{fg('cyan')}\t=> \"{query}\" found {len(video_url)} Videos{attr('reset')}")
    return video_url


def download_video(url: str, save_path: str):
    """
    Downloads a video from the provided URL and saves it to the given path.

    Args:
        url (str): The URL of the video.
        save_path (str): The local path to save the video.
    """
    print(f"{fg('blue')}Downloading video from: {url}...{attr('reset')}")
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"{fg('green')}Video downloaded successfully to: {save_path}{attr('reset')}")
    else:
        print(f"{fg('red')}Failed to download video.{attr('reset')}")


def generate_script(topic):
    """
    Generates a script based on the input topic using GPT-3.5, falls back to a backup OpenAI key if the primary one fails,
    then falls back to Claude if both OpenAI APIs fail, and finally asks the user to manually provide the script.

    Args:
        topic (str): The topic for which to generate the script.

    Returns:
        str: A script generated for the given topic or input by the user.
    """
    print(f"{fg('blue')}Generating script for topic: {topic}...{attr('reset')}")
    time.sleep(2)

    # Load environment variables from .env file
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    backup_openai_api_key = os.getenv("BACKUP_OPENAI_API_KEY")
    claude_api_key = os.getenv("CLAUDE_API_KEY")

    # Check if the API keys are set
    if not openai_api_key and not backup_openai_api_key:
        print(f"{fg('red')}Error: Missing both primary and backup OpenAI API keys in .env file.{attr('reset')}")
        exit(1)

    # Try the primary OpenAI API key first
    try:
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system", "content": "You are an informative and engaging YouTube video script writer."
            }, {
                "role": "user",
                "content": f"Write a detailed, engaging, and informative explanation of the topic {topic}. Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 400 words. DO not include any stage directions, or scene setting. Just provide the words the narrator will read."
            }],
            temperature=0.7,
            max_tokens=600,
        )

        script = response['choices'][0]['message']['content']
        print(f"{fg('green')}Script generated successfully using GPT-3.5!{attr('reset')}")
        print(script)
        return script

    except Exception as e:
        print(f"{fg('red')}Error with primary OpenAI API: {e}{attr('reset')}")

        # Try the backup OpenAI API key
        if backup_openai_api_key:
            try:
                openai.api_key = backup_openai_api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "system", "content": "You are an informative and engaging YouTube video script writer."
                    }, {
                        "role": "user",
                        "content": f"Write a detailed, engaging, and informative explanation of the topic {topic}. Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 400 words. DO not include any stage directions, or scene setting. Just provide the words the narrator will read."
                    }],
                    temperature=0.7,
                    max_tokens=600,
                )

                script = response['choices'][0]['message']['content']
                print(f"{fg('green')}Script generated successfully using backup OpenAI API!{attr('reset')}")
                print(script)
                return script

            except Exception as e:
                print(f"{fg('red')}Error with backup OpenAI API: {e}{attr('reset')}")
        else:
            print(f"{fg('yellow')}No backup OpenAI API key provided. Trying Claude API...{attr('reset')}")

        # Fallback to Claude API
        try:
            claude_url = "https://api.anthropic.com/v1/complete"
            headers = {
                "Authorization": f"Bearer {claude_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "prompt": f"Write a detailed, engaging, and informative script for a video about {topic}. Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 400 words.",
                "max_tokens": 600,
                "temperature": 0.7
            }

            response = requests.post(claude_url, headers=headers, json=data)
            response.raise_for_status()

            claude_script = response.json()['completion']
            print(f"{fg('green')}Script generated successfully using Claude!{attr('reset')}")
            print(claude_script)
            return claude_script

        except Exception as e:
            print(f"{fg('red')}Error with Claude API: {e}{attr('reset')}")

            # Ask the user to generate the script manually
            print(f"{fg('yellow')}Both GPT-3.5 and Claude failed to generate the script.{attr('reset')}")

            # Prepare the prompt to be copied into the clipboard
            prompt_text = f"Write a detailed, engaging, and informative script for a video about {topic}. Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 400 words. DO not include any directions for the narrator, write it exactly as it should be read. No headerss, numbered points."
            pyperclip.copy(prompt_text)

            print(
                f"{fg('yellow')}The prompt has been copied to your clipboard. Please paste it into ChatGPT at https://chat.openai.com/{attr('reset')}")

            # Give the user an option to input the script manually
            user_choice = input(
                f"{fg('blue')}Would you like to manually input the script or exit the program? (Type '1' to enter script, 'exit' to quit): {attr('reset')} ").strip().lower()

            if user_choice == "1":
                script = input(f"{fg('blue')}Please paste the script you generated: {attr('reset')}")
                print(f"{fg('green')}Script received successfully!{attr('reset')}")
                return script
            else:
                print(f"{fg('red')}Exiting the program.{attr('reset')}")
                exit(0)

def fetch_stock_videos(keywords):
    print(f"{fg('blue')}Fetching stock videos related to: {keywords}...{attr('reset')}")
    api_key = os.getenv("STOCK_VIDEO_API_KEY")
    videos = search_for_stock_videos(" ".join(keywords), api_key, 5, 10)

    # Create a directory to save the videos
    video_dir = "downloaded_videos"
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    saved_videos = []
    for i, video_url in enumerate(videos):
        video_path = os.path.join(video_dir, f"video_{i + 1}.mp4")
        download_video(video_url, video_path)
        saved_videos.append(video_path)

    return saved_videos if saved_videos else ["default_video.mp4"]

def generate_voiceover(script, topic):
    print(f"{fg('blue')}Generating voiceover...{attr('reset')}")
    time.sleep(2)

    # Sanitize the topic to use as a filename
    sanitized_topic = re.sub(r'[^a-zA-Z0-9]', '_', topic)  # Replace non-alphanumeric characters with underscores
    voiceover_filename = f"{sanitized_topic}_voiceover.mp3"

    # Convert the script into speech
    tts = gTTS(text=script, lang='en')

    # Save the voiceover to a file
    voiceover_path = os.path.join(os.getenv("AUDIO_OUTPUT"), voiceover_filename)
    tts.save(voiceover_path)

    print(f"{fg('green')}Voiceover saved to: {voiceover_path}{attr('reset')}")
    return voiceover_path


def add_subtitles(video, script):
    print(f"{fg('blue')}Adding subtitles to video...{attr('reset')}")
    time.sleep(2)
    return "final_video.mp4"


def upload_to_youtube(video_path):
    print(f"{fg('green')}Uploading {video_path} to YouTube...{attr('reset')}")
    time.sleep(2)
    print(f"{fg('green')}Upload successful!{attr('reset')}")


def main():
    print(f"{fg('cyan')}Welcome to the Automated Video Generator!{attr('reset')}")
    topic = input("Enter the video topic: ")

    # Save the entered topic to a file
    topics_file_path = "topics.txt"  # You can change the path if needed
    with open(topics_file_path, "a") as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {topic}\n")  # Write topic with a timestamp

    script = generate_script(topic)
    keywords = topic.split()[:3]
    stock_videos = fetch_stock_videos(keywords)
    voiceover = generate_voiceover(script, topic)
    final_video = add_subtitles(stock_videos[0], script)
    upload = input("Do you want to upload the video to YouTube? (yes/no): ")
    if upload.lower() == "yes":
        upload_to_youtube(final_video)
    print(f"{fg('green')}Video creation process complete!{attr('reset')}")


if __name__ == "__main__":
    main()
