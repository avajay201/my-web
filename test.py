# input_string = '3[a2[c]]'

# task_num = ''
# task = []
# tasks_strings = []
# string = ''
# result = ''

# for c in input_string:
#     if c.isdigit():
#         task_num += c
#     elif c == '[':
#         task.append(int(task_num))
#         task_num = ''
#         if string:
#             tasks_strings.append(string)
#             string = ''
#     elif c == ']':
#         if string:
#             tasks_strings.append(string)
#             string = ''
#         new_str = ''
#         while task:
#             num = task.pop()
#             strr = tasks_strings.pop()
#             if new_str:
#                 new_str = (strr + new_str) * num
#             else:
#                 new_str = num * strr
#         result += new_str
#     else:
#         string += c

# print(result)


# import openai

# client = openai.OpenAI(api_key="")

# response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "How does OpenAI API work?"}
#     ]
# )

# print(response.choices[0].message.content)



# import speech_recognition as sr
# import requests

# recognizer = sr.Recognizer()


# def listen():
#     with sr.Microphone() as source:
#         print("Say something...")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)

#     try:
#         text = recognizer.recognize_google(audio)
#         print("You said:", text)
#         return text
#     except sr.UnknownValueError:
#         print("Could not understand the audio.")
#     except sr.RequestError:
#         print("Could not request results from Google Speech Recognition.")

# def answer(cmd):
#     API_KEY = ""

#     # API URL
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

#     # Headers
#     headers = {
#         "Content-Type": "application/json"
#     }

#     # Data payload
#     data = {
#         "contents": [
#             {
#                 "parts": [
#                     {"text": cmd}
#                 ]
#             }
#         ]
#     }

#     # Send POST request
#     response = requests.post(url, headers=headers, json=data)

#     # Print response
#     if response.status_code == 200:
#         # print(response.json())  # Full response
#         print("Response:", response.json()["candidates"][0]["content"]["parts"][0]["text"])  # Extracted text
#     else:
#         print("Error:", response.status_code, response.text)
# if __name__ == '__main__':
# while True:
    # command = listen()
    # if not command:
    #     print('Listening error, please say again!')
    # else:
    #     answer(command)

from openai import OpenAI

YOUR_API_KEY = "INSERT API KEY HERE"
def answer(command):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {   
            "role": "user",
            "content": (
                command
            ),
        },
    ]

    client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

    # chat completion without streaming
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )
    print(response)

    # chat completion with streaming
    response_stream = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
        stream=True,
    )
    for response in response_stream:
        print(response)
command ='''Give me answer in short response with better response of this query -
            Tell me some dunder method in oops.'''
answer(command)

# import requests

# response = requests.get('https://www.youtube.com/watch?v=oLHivRyXzE8', headers={
#     "Cookie": "LOGIN_INFO=AFmmF2swRgIhAKFC9HF0waQ-DkfrRPiMcsPDVT5S9fpRtpyykPWP3o80AiEAtojvJVtPG9R0qrYbQ7eVVc-GQFRqSP6NLN_7ryOG1RA:QUQ3MjNmeVE1VmF2LVFUeGhFY0dNMGJHdUtnOVRubG9SWHZ4eFdEVUxhc0lsUUJNZXJoUXJObzRmVTd3eUtMMGFmemZHUVIxenlZMXhYQ0tTNDFsS29jRkpGZmo2ZEhoQXVNV1hWYXFPMDhuSnBfYlJ3QzhNSGp5LWY1amRxV1g0MVZWMUVzODZGR1BZNUlqbmpGcnMzNVVrZGt3VFhyUC1n; VISITOR_INFO1_LIVE=zXxFUxNYULU; VISITOR_PRIVACY_METADATA=CgJJThIEGgAgOA%3D%3D; HSID=AoNFZi0DNQIBFd_Cv; SSID=A11c6GpVw-7LlSeJA; APISID=4R0A_U_etOT3jYJ9/A1nBp0LMfhB16HmKc; SAPISID=brzrbmmtKF9ud2UX/AbHtLUo0AEhYmmI_J; __Secure-1PAPISID=brzrbmmtKF9ud2UX/AbHtLUo0AEhYmmI_J; __Secure-3PAPISID=brzrbmmtKF9ud2UX/AbHtLUo0AEhYmmI_J; SID=g.a000twj9WsskBlDsKij4ojXOrAyxal3kLIaeE2ocybttohIb9-lgrjbc8JEkgke6VpDSg7rYFAACgYKAX8SARASFQHGX2MiK4Ssz74Cac0TufTXexzgsRoVAUF8yKqihxmizdlk4JUPO5t1voCU0076; __Secure-1PSID=g.a000twj9WsskBlDsKij4ojXOrAyxal3kLIaeE2ocybttohIb9-lgPHlRQFHioNr-zIMyfvmXgQACgYKAaQSARASFQHGX2MiTjqyXGV08AM8XEHhfUj1lBoVAUF8yKoOKWAAJ6IustZPehgpx1Ec0076; __Secure-3PSID=g.a000twj9WsskBlDsKij4ojXOrAyxal3kLIaeE2ocybttohIb9-lgm1uvrig348MINIjL08BAagACgYKAcwSARASFQHGX2MiqypJigxPiv8qY_vTzeWegBoVAUF8yKpz9VAUysLKEey5Q_6Mt8DP0076; PREF=tz=Asia.Calcutta&f4=4000000&f7=150&f6=40000000; YSC=tV--KsiT4Dw; __Secure-ROLLOUT_TOKEN=COClz9Gn5aXa9QEQ_MWQ-KPXiQMY5-3Q-_z1iwM%3D; __Secure-1PSIDTS=sidts-CjEBEJ3XV1yHPc9kMV54H-NC9SxRuKYVubYhuhEOHYJ9XkaVcn8M0ytSLQegFZACz-6qEAA; __Secure-3PSIDTS=sidts-CjEBEJ3XV1yHPc9kMV54H-NC9SxRuKYVubYhuhEOHYJ9XkaVcn8M0ytSLQegFZACz-6qEAA; SIDCC=AKEyXzV1nt0TdbUEDl2_hi6So1CIdCadkgIupGadtD47STnzCz7g9UUT8NmYEhv_9PTvbSJPdA; __Secure-1PSIDCC=AKEyXzVaIkrmZHHR6uYPuex0KL7-QUQmbMicixy6EaV4Qs0FCJkzD49micpqBQIo-iFGJu9icQ; __Secure-3PSIDCC=AKEyXzWLOlD-",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
# })

# if response.status_code == 200:
#     with open('data.html', 'wb') as f:
#         f.write(response.content)
# else:
#     print('Failed!', response.status_code)


# from pytube import YouTube

# def get_youtube_comments(video_url):
#     yt = YouTube(video_url)
#     print(dir(yt))
#     # print(f"Title: {yt.title}")
#     print(f"Views: {yt.views}")
#     print(f"Author: {yt.author}")
#     print(f"Channel URL: {yt.channel_url}")
#     print(f"Publish Date: {yt.publish_date}")
#     print(f"Rating: {yt.rating}")
#     print(f"Description: {yt.description}")
#     print(f"Thumbnail: {yt.thumbnail_url}")
    
# Test with a YouTube video
# get_youtube_comments("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
# from itertools import islice
# from youtube_comment_downloader import *
# downloader = YoutubeCommentDownloader()
# comments = downloader.get_comments_from_url('https://www.youtube.com/watch?v=oLHivRyXzE8', sort_by=SORT_BY_POPULAR)
# for i, comment in enumerate(islice(comments, 100)):
#     print(i+1, comment['text'])

# import requests
# from bs4 import BeautifulSoup
# import re
# import json


# url = 'https://www.youtube.com/watch?v=AZeU5_YpqsA'

# response = requests.get(url)
# if response.status_code == 200:
#     with open('data.html', 'w') as f:
#         f.write(response.text)

#     soup = BeautifulSoup(response.text, 'html.parser')

#     nonce_value = "i6mQo2ZNkoQ4oGY7o82WAw"
#     scripts = soup.find_all('script')

    # if scripts:
    #     print(len(scripts))
    #     match = re.search(r'(\{.*\})', str(scripts[46]))
    #     if match:
    #         json_data = json.loads(match.group(1))
    #         with open('script.json', 'w') as f:
    #             json.dump(json_data, f, indent=4)
    #         print("Extracted JSON-like object:", json_data)
    #     else:
    #         print("No JSON-like object found")
    # else:
    #     print('No matching <script> tags found')

# with open('script.json') as f:
#     data = json.load(f)

# print(data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][-1]["itemSectionRenderer"]["contents"][0]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"])
# def extract_keys(obj, keys):
#     result = {}
#     if isinstance(obj, dict):
#         for key, value in obj.items():
#             if key in keys:
#                 result[key] = value
#             else:
#                 nested = extract_keys(value, keys)
#                 if nested:
#                     result[key] = nested
#     elif isinstance(obj, list):
#         nested_list = [extract_keys(item, keys) for item in obj]
#         result = [item for item in nested_list if item]
#     return result

# specific_keys = ["continuationCommand", "lat", "email", "skills"]
# filtered_data = extract_keys(data, specific_keys)

# print("Filtered Data:", json.dumps(filtered_data, indent=4))