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
#     API_KEY = "AIzaSyCxQOEEj1YWE7SaP1tMG3Ug_jwqYPIJpZI"

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
#         print(response.json())  # Full response
#         print("Response:", response.json()["candidates"][0]["content"]["parts"][0]["text"])  # Extracted text
#     else:
#         print("Error:", response.status_code, response.text)
# if __name__ == '__main__':
#     while True:
#         command = listen()
#         if not command:
#             print('Listening error, please say again!')
#         else:
#             answer(command)




class Meta(type):
    def __new__(cls, name, bases, dct):
        print(cls, f"Creating class {name}", bases, dct)
        return super().__new__(cls, name, bases, dct)

class MyClass(Meta, metaclass=Meta):
    a = 10
    def test():
        pass

