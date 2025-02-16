import os
import requests
import subprocess
from gtts import gTTS
import moviepy as mp
from moviepy import TextClip, CompositeVideoClip, VideoFileClip
import srt
from datetime import timedelta
import openai
from dotenv import load_dotenv
import pyperclip
from colored import fg, attr
from typing import List
import nltk
from nltk.tokenize import sent_tokenize

# Load environment variables
load_dotenv()

# Environment variable paths
VIDEO_OUTPUT = os.getenv('VIDEO_OUTPUT')
AUDIO_OUTPUT = os.getenv('AUDIO_OUTPUT')
THUMBNAIL_OUTPUT = os.getenv('THUMBNAIL_OUTPUT')
YOUTUBE_UPLOAD_FOLDER = os.getenv('YOUTUBE_UPLOAD_FOLDER')
SUBTITLE_OUTPUT_FOLDER = os.getenv('SUBTITLE_OUTPUT_FOLDER')
DOWNLOADED_VIDEO_FOLDER = os.getenv('DOWNLOADED_VIDEO_FOLDER')


# Function to generate the script using GPT-3.5, backup OpenAI key, or Claude
def generate_script(topic):
    return "Oh my god I hope this works"


    # print(f"{fg('blue')}Generating script for topic: {topic}...{attr('reset')}")
    # load_dotenv()
    # openai_api_key = os.getenv("OPENAI_API_KEY")
    # backup_openai_api_key = os.getenv("BACKUP_OPENAI_API_KEY")
    # claude_api_key = os.getenv("CLAUDE_API_KEY")
    #
    # if not openai_api_key and not backup_openai_api_key:
    #     print(f"{fg('red')}Error: Missing both primary and backup OpenAI API keys in .env file.{attr('reset')}")
    #     exit(1)
    #
    # try:
    #     openai.api_key = openai_api_key
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[{
    #             "role": "system", "content": "You are an informative and engaging YouTube video script writer."
    #         }, {
    #             "role": "user",
    #             "content": f"Write a detailed, engaging, and informative explanation of the topic {topic}.Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 100 words. Do not include any stage directions, or scene setting. Just provide the words the narrator will read. Keep it all on one line, no line breaks",
    #         }],
    #         temperature=0.7,
    #         max_tokens=600,
    #     )
    #     script = response['choices'][0]['message']['content']
    #     print(f"{fg('green')}Script generated successfully using GPT-3.5!{attr('reset')}")
    #     return script
    # except Exception as e:
    #     print(f"{fg('red')}Error with primary OpenAI API: {e}{attr('reset')}")
    #     if backup_openai_api_key:
    #         try:
    #             openai.api_key = backup_openai_api_key
    #             response = openai.ChatCompletion.create(
    #                 model="gpt-3.5-turbo",
    #                 messages=[{
    #                     "role": "system", "content": "You are an informative and engaging YouTube video script writer."
    #                 }, {
    #                     "role": "user",
    #                     "content": f"Write a detailed, engaging, and informative explanation of the topic {topic}.Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 100 words. Do not include any stage directions, or scene setting. Just provide the words the narrator will read. Keep it all on one line, no line breaks",
    #                 }],
    #                 temperature=0.7,
    #                 max_tokens=600,
    #             )
    #             script = response['choices'][0]['message']['content']
    #             print(f"{fg('green')}Script generated successfully using backup OpenAI API!{attr('reset')}")
    #             return script
    #         except Exception as e:
    #             print(f"{fg('red')}Error with backup OpenAI API: {e}{attr('reset')}")
    #     else:
    #         print(f"{fg('yellow')}No backup OpenAI API key provided. Trying Claude API...{attr('reset')}")
    #
    #     try:
    #         claude_url = "https://api.anthropic.com/v1/complete"
    #         headers = {"Authorization": f"Bearer {claude_api_key}", "Content-Type": "application/json"}
    #         data = {
    #             "prompt": f"Write a detailed, engaging, and informative explanation of the topic {topic}.Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 100 words. Do not include any stage directions, or scene setting. Just provide the words the narrator will read. Keep it all on one line, no line breaks",
    #             "max_tokens": 600,
    #             "temperature": 0.7
    #         }
    #         response = requests.post(claude_url, headers=headers, json=data)
    #         response.raise_for_status()
    #         claude_script = response.json()['completion']
    #         print(f"{fg('green')}Script generated successfully using Claude!{attr('reset')}")
    #         return claude_script
    #     except Exception as e:
    #         print(f"{fg('red')}Error with Claude API: {e}{attr('reset')}")
    #         print(f"{fg('yellow')}Both GPT-3.5 and Claude failed to generate the script.{attr('reset')}")
    #         prompt_text = f"Write a detailed, engaging, and informative explanation of the topic {topic}.Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 100 words. Do not include any stage directions, or scene setting. Just provide the words the narrator will read. Keep it all on one line, no line breaks"
    #         pyperclip.copy(prompt_text)
    #         print(f"{fg('yellow')}The prompt has been copied to your clipboard. Please paste it into ChatGPT at https://chat.openai.com/{attr('reset')}")
    #         user_choice = input(f"{fg('blue')}Would you like to manually input the script or exit the program? (Type '1' to enter script, 'exit' to quit): {attr('reset')} ").strip().lower()
    #         if user_choice == "1":
    #             script = input(f"{fg('blue')}Please paste the script you generated: {attr('reset')}")
    #             print(f"{fg('green')}Script received successfully!{attr('reset')}")
    #             return script
    #         else:
    #             print(f"{fg('red')}Exiting the program.{attr('reset')}")
    #             exit(0)


# Function to generate voiceover
def generate_voiceover(script, topic):
    print(f"DEBUG: Full script to be converted to voiceover:\n{script}")  # Debugging line
    tts = gTTS(text=script, lang='en')
    audio_path = os.path.join(AUDIO_OUTPUT, f"{topic}.mp3")
    tts.save(audio_path)
    print(f"DEBUG: Voiceover for {topic} has been succesfully generated!")
    return audio_path


# Function to fetch stock videos
def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
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


def download_video_from_pexels(topic, video_index, video_url):
    if not os.path.exists(DOWNLOADED_VIDEO_FOLDER):
        os.makedirs(DOWNLOADED_VIDEO_FOLDER)

    video_filename = f"{topic}{video_index:03d}.mp4"
    down_fold_video_path = os.path.join(DOWNLOADED_VIDEO_FOLDER, video_filename)

    try:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(down_fold_video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Video {video_filename} downloaded successfully.")
        else:
            print(f"Failed to download video {video_filename}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading video {video_filename}: {e}")

    return down_fold_video_path


def fetch_stock_videos(keywords, topic):
    print(f"{fg('blue')}Fetching stock videos related to: {keywords}...{attr('reset')}")
    api_key = os.getenv("STOCK_VIDEO_API_KEY")
    videos = search_for_stock_videos(" ".join(keywords), api_key, 5, 10)

    DOWNLOADED_VIDEO_FOLDER = os.getenv("DOWNLOADED_VIDEO_FOLDER")
    if not os.path.exists(DOWNLOADED_VIDEO_FOLDER):
        os.makedirs(DOWNLOADED_VIDEO_FOLDER)

    saved_videos = []
    for i, video_url in enumerate(videos):
        video_filename = f"{topic}{i + 1:03d}.mp4"
        video_path = os.path.join(DOWNLOADED_VIDEO_FOLDER, video_filename)
        download_video_from_pexels(topic, i, video_url)
        saved_videos.append(video_path)

    return saved_videos if saved_videos else ["default_video.mp4"]



def generate_subtitles(script, topic):
    sentences = sent_tokenize(script)  # Split script into sentences
    time_per_sentence = 1.5  # Adjust time per sentence as needed
    total_duration = len(sentences) * time_per_sentence

    # Create subtitles for each sentence
    subs = []
    current_time = timedelta(seconds=0)
    for sentence in sentences:
        subtitle = srt.Subtitle(index=len(subs) + 1,
                                start=current_time,
                                end=current_time + timedelta(seconds=time_per_sentence),
                                content=sentence)
        subs.append(subtitle)
        current_time += timedelta(seconds=time_per_sentence)

    # Ensure subtitle output folder exists
    if not os.path.exists(SUBTITLE_OUTPUT_FOLDER):
        os.makedirs(SUBTITLE_OUTPUT_FOLDER)

    # Define subtitle filename and path
    subtitle_filename = os.path.join(SUBTITLE_OUTPUT_FOLDER, f"{topic}.srt")

    # Write subtitles to file
    with open(subtitle_filename, "w") as subtitle_file:
        subtitle_file.write(srt.compose(subs))

    print(f"DEBUG: Subtitles saved as: {subtitle_filename}.")
    return subtitle_filename




def add_subtitles_to_video(video_path, subtitle_path, output_path, font_path='C:/Windows/Fonts/arial.ttf',
                           font_size=24, color='white', stroke_width=2, stroke_color='black'):
    # Load the video
    video_clip = VideoFileClip(video_path)

    # Read and parse subtitles
    with open(subtitle_path, 'r', encoding='utf-8-sig') as f:
        subtitles = list(srt.parse(f.read()))  # Parse SRT file

    print(f"DEBUG: Parsed {len(subtitles)} subtitles")

    # Store subtitle clips
    subtitle_clips = []

    # Get video dimensions and ensure they're integers
    img_width, img_height = map(int, video_clip.size)  # Casting to integers

    for subtitle in subtitles:
        start_time = subtitle.start.total_seconds()
        end_time = subtitle.end.total_seconds()
        duration = end_time - start_time

        # Create TextClip for each subtitle
        text_clip = TextClip(
            text=subtitle.content,
            font=font_path,
            font_size=font_size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method="caption",  # Use caption method for text wrapping
            size=(int(img_width * 0.8), None),  # 80% of video width, auto height, cast to int
            horizontal_align="center",  # Center text horizontally
            vertical_align="center",    # Align text to the bottom
        )

        # Position the text at the bottom (95% of height)
        text_clip = text_clip.with_position(("center", 0.95), relative=True) \
                             .with_start(start_time) \
                             .with_duration(duration)

        subtitle_clips.append(text_clip)

    # Overlay subtitles on the video
    final_video = CompositeVideoClip([video_clip] + subtitle_clips)

    # Export the final video
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video_clip.fps)

    print(f"DEBUG: Video with subtitles saved as: {output_path}")

# Function to combine video, audio, and subtitles into a final video
def combine_video_with_audio_and_subtitles(topic):
    # Split the topic into keywords
    keywords = topic.split()  # This will create a list of words
    video_paths = fetch_stock_videos(keywords, topic)  # Pass the keywords as a list

    # Ensure we have stock video
    video_file = video_paths[0] if video_paths else "default_video.mp4"

    video_clip = mp.VideoFileClip(video_file)
    video_duration = video_clip.duration

    print(f"{fg('green')}Video Duration: {video_duration} seconds{attr('reset')}")

    # Crop video to vertical (9:16 aspect ratio)
    target_width = 1080  # Adjust based on resolution
    target_height = 1920
    original_width, original_height = video_clip.size

    if original_width > original_height:  # Landscape -> Crop Center
        new_width = int(original_height * (9 / 16))
        x_center = original_width // 2
        video_clip = video_clip.cropped(x1=x_center - new_width // 2, x2=x_center + new_width // 2)
    else:  # If already vertical or square, resize instead
        video_clip = video_clip.resized(height=target_height)

    # Generate script
    script = generate_script(topic)
    voiceover_path = generate_voiceover(script, topic)
    subtitle_filename = generate_subtitles(script, topic)

    voiceover = mp.AudioFileClip(voiceover_path)

    final_video = video_clip.with_audio(voiceover)

    # Using the VIDEO_OUTPUT path from .env to save the final video
    final_video_output_path = os.path.join(VIDEO_OUTPUT, f"{topic}_final.mp4")
    final_video.write_videofile(final_video_output_path, codec="libx264", audio_codec="aac", fps=24)

    # Add subtitles to the final video
    final_video_with_subs_path = final_video_output_path.replace(".mp4", "_with_subs.mp4")
    print(f"DEBUG: Subtitle file path: {subtitle_filename}")
    add_subtitles_to_video(final_video_output_path, subtitle_filename, final_video_with_subs_path)
    print(f"DEBUG: Final video without subtitles saved at: {final_video_output_path}")
    print(f"DEBUG: Final video with subtitles saved at: {final_video_with_subs_path}")

    print(f"{fg('green')}Video successfully created with audio and subtitles!{attr('reset')}")

def main():
    # I have commented out the input and just set topic to "chicken and eggs" to speed up process of debugging
    topic = "chickens and eggs" # todo delete this line
    # topic = input(f"{fg('blue')}Enter a topic for the video: {attr('reset')}") UNCOMMENT THIS LINE
    combine_video_with_audio_and_subtitles(topic)

if __name__ == "__main__":
    main()
