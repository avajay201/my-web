# Standard Library Imports
import re
import time
import cv2
import numpy as np
import requests
from datetime import datetime, timedelta
import concurrent.futures
from collections import Counter

# Google API Imports
from googleapiclient.discovery import build

# NLTK (Natural Language Processing)
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk import pos_tag
from nltk.corpus import wordnet, stopwords

# Third-party NLP Libraries
from transformers import pipeline
from langdetect import detect
from deep_translator import GoogleTranslator
import emoji

# Download necessary NLTK resources (if not already installed)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('vader_lexicon', quiet=True)
nltk.download('stopwords', quiet=True)

# Initialize transformers pipeline for emotion detection from text
text_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device="cuda")

# Initialize NLP Tools
sia = SentimentIntensityAnalyzer()  # VADER for sentiment analysis
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))  # Load stopwords for English

# Constants
BASE_URL = 'https://www.instagram.com'

def rotate_image(image, angle):
    """
    Rotate the given image by the specified angle.
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    # Get rotation matrix
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Perform the rotation
    rotated = cv2.warpAffine(image, M, (w, h))

    return rotated

def fetch_face_locations(img):
    """
    Detect faces in the given image.
    """
    # Detect faces in the image
    angles = [0, 90, 180, 270]
    face_exists = []
    for angle in angles:
        rotated_img = rotate_image(img, angle)
        face_locations = face_recognition.face_locations(rotated_img)
        if face_locations:
            face_exists = face_locations
            break
    return face_exists

def image_normalize(file):
    """
    Normalize the given image file.
    """
    # Convert file to a NumPy array
    file_bytes = np.frombuffer(file.read(), np.uint8)

    # Decode image using OpenCV
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return img

def get_user_id(username):
    """
    Fetches the Instagram User ID for a given username.
    
    Parameters:
    username (str): The Instagram username.

    Returns:
    str or None: The user's Instagram ID if found, else None.
    """
    # Instagram API endpoint to fetch user profile info
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"

    # Headers to simulate a real browser request (helps avoid blocking)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "x-ig-app-id": "936619743392459"  # Instagram App ID
    }

    user_id = None

    try:
        # Send GET request to fetch user profile data
        response = requests.get(url, headers=headers)

        # If response is successful (status code 200)
        if response.status_code == 200:
            data = response.json()

            # Extract user ID safely
            user_data = data.get("data", {}).get("user", {}) if data.get("data", {}) else {}
            user_id = user_data.get("id")
            if not user_id:
                print(f"⚠ No user found for username: {username}")
        else:
            print(f"❌ Failed to fetch user ID. Status Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching data: {e}")

    return user_id

def get_profile(user_id):
    """
    Fetches Instagram profile details for a given user ID.

    Parameters:
    user_id (str): The Instagram user ID.

    Returns:
    dict: A dictionary containing the user's profile details, or an empty dictionary if an error occurs.
    """
    # Instagram GraphQL API endpoint
    url = "https://www.instagram.com/graphql/query"

    # Headers to mimic a real Instagram web request (prevents bot detection)
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-prefers-color-scheme": "dark",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-full-version-list": "\"Not(A:Brand\";v=\"99.0.0.0\", \"Google Chrome\";v=\"133.0.6943.142\", \"Chromium\";v=\"133.0.6943.142\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": "\"\"",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-ch-ua-platform-version": "\"19.0.0\"",
        "x-asbd-id": "359341",
        "x-bloks-version-id": "8cfdad7160042d1ecf8a994bb406cbfffb9a769a304d39560d6486a34ea8a53e",
        "x-csrftoken": "eLcnItS3kK4QZVUFM1PeaT9RzXVdQUDx",
        "x-fb-friendly-name": "PolarisProfilePageContentQuery",
        "x-fb-lsd": "2qRvagxUi5SCc7vNP2293a",
        "x-ig-app-id": "936619743392459"
    }

    # GraphQL query parameters with the user ID
    data = {
        "av": "17841409795510157",
        "__d": "www",
        "__user": "0",
        "__a": "1",
        "__req": "18",
        "__hs": "20149.HYP:instagram_web_pkg.2.1...1",
        "dpr": "1",
        "__ccg": "EXCELLENT",
        "__rev": "1020522517",
        "__s": "ttan9g:6nkb18:hy5aiz",
        "__hsi": "7477148673611444906",
        "__dyn": "7xeUjG1mxu1syaxG4Vp41twpUnwgU7SbzEdF8aUco2qwJyEiw9-1DwUx60p-0LVE4W0qa321Rw8G11wBz81s8hwGxu786a3a1YwBgao6C0Mo2iyo7u3ifK0zEkxe2GewGw9a3614xm0zK5o4q3y261kx-0ma2-azqwt8d-2u2J08O321LwTwKG1pg2fwxyo6O1FwlEcUed6goK2OubK5V89FbxG1oxe6UaUaE2xyVrx6",
        "__csr": "iM9A5Yh5l2vWn4YCyvnZi-JkO6AOp5Z8xlbJaQFBiKya9OyAuq4kt4yV5hlZqcjlAjZplCWSmsyqhriQRgyvBHy9Gi8KES_-EGAmdGhbWDkxbK9DF4iBDK5ppmhNp9ELxelGfz6mbhedyQ5ojoydAG5qAGfBKEnhp8yu8BxCiEK4Q58sDy801cvA0GEjng6a5E9po5mro6m488B8Qp4A4adhE-6p6dwa21rgmxDwBa36Vo22p4NwCXw8choao4OyPa444E89Q6Q1YU0z68wje583Exy0su0jW09xAwnrzoma9xVDc3-4UDxp0xw9a0liohplp4ETO0PBl0p8450kEW3A9ANoi4U2Dgqwl8gwVABkM2yixe6_gfO285-14wko0jQwIEw4u2mlu0bsCyp8vUGdwp406vE0cyU7WBg5uF819o26w2potw2Y8mwiE4G5lw1j10cq",
        "__comet_req": "7",
        "fb_dtsg": "NAcNf8QOArCi7SE9yL57hjZoI2FYFBE_dPT7pKs7h8XnTuXWKH2Jvkw:17854477105113577:1730355965",
        "jazoest": "26105",
        "lsd": "2qRvagxUi5SCc7vNP2293a",
        "__spin_r": "1020522517",
        "__spin_b": "trunk",
        "__spin_t": "1740909338",
        "fb_api_caller_class": "RelayModern",
        "fb_api_req_friendly_name": "PolarisProfilePageContentQuery",
        "variables": f'{{"id":"{user_id}","render_surface":"PROFILE"}}',
        "server_timestamps": "true",
        "doc_id": "28949739181283923"
    }

    # Initialize an empty dictionary to store profile data
    profile_data = {}
    try:
        # Send POST request to fetch profile data
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            data = response.json()
            user_data = data.get('data', {}).get('user', {})

            if user_data:
                # Extract profile details
                profile_data = {
                    "user_id": user_data.get('pk', ''),  # Instagram User ID
                    "username": user_data.get('username', ''),  # Username
                    "full_name": user_data.get('full_name', ''),  # Full name
                    "biography": user_data.get('biography', ''),  # Bio description
                    "profile_pic": user_data.get('hd_profile_pic_url_info', {}).get('url', '') if user_data.get('hd_profile_pic_url_info', {}) else '',  # Profile picture URL
                    "is_private": user_data.get('is_private', False),  # Account privacy status
                    "is_verified": user_data.get('is_verified', False),  # Verified badge status
                    "account_type": user_data.get('account_type', ''),  # Account type (1=Personal, 2=Creator, 3=Business)
                    "follower_count": user_data.get('follower_count', 0),  # Followers count
                    "following_count": user_data.get('following_count', 0),  # Following count
                    "media_count": user_data.get('media_count', 0),  # Number of posts
                    "total_clips_count": user_data.get('total_clips_count', 0),  # Story Clip highlights count
                    "category": user_data.get('category', ''),  # Category of the profile
                    "bio_links": [
                        {
                            "title": link.get('title', ''),
                            "url": link.get('url', '')
                        }
                        for link in user_data.get('bio_links', []) if link
                    ]  # Extract bio links if available
                }
            else:
                print("⚠ No user data found in the response.")
        else:
            print(f"❌ Request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

    return profile_data

def get_posts(username, posts=30):
    """
    Fetches recent posts from an Instagram user's timeline.

    Parameters:
    username (str): The Instagram username.
    posts (int): The number of posts to retrieve (default is 30).

    Returns:
    list: A list of dictionaries containing post details.
    """
    # Instagram GraphQL API endpoint
    url = "https://www.instagram.com/graphql/query"

    # Headers to mimic a real Instagram web request (prevents bot detection)
    headers = {
        "accept": "*/*",
        "accept-language": "en-NA,en-US;q=0.9,en;q=0.8,hi;q=0.7",
        "content-type": "application/x-www-form-urlencoded",
        "priority": "u=1, i",
        "sec-ch-prefers-color-scheme": "dark",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-full-version-list": "\"Not(A:Brand\";v=\"99.0.0.0\", \"Google Chrome\";v=\"133.0.6943.142\", \"Chromium\";v=\"133.0.6943.142\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": "\"\"",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-ch-ua-platform-version": "\"19.0.0\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-asbd-id": "359341",
        "x-bloks-version-id": "8cfdad7160042d1ecf8a994bb406cbfffb9a769a304d39560d6486a34ea8a53e",
        "x-csrftoken": "eLcnItS3kK4QZVUFM1PeaT9RzXVdQUDx",
        "x-fb-friendly-name": "PolarisProfilePostsTabContentQuery_connection",
        "x-fb-lsd": "o2qSYT0-MhEFbe1L-2q2kO",
        "x-ig-app-id": "936619743392459"
    }

    # GraphQL query parameters with the username and number of posts
    data = {
        "variables": f'{{"after":null,"before":null,"data":{{"count":{posts},"include_reel_media_seen_timestamp":true,"include_relationship_info":true,"latest_besties_reel_media":true,"latest_reel_media":true}},"first":{posts},"last":null,"username":"{username}","__relay_internal__pv__PolarisIsLoggedInrelayprovider":true,"__relay_internal__pv__PolarisShareSheetV3relayprovider":true}}',
        "doc_id": "9218791164857396"
    }

    # Initialize an empty list for storing post data
    posts_data = []

    try:
        import json
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        if response.status_code == 200:
            # Extract the post feed data
            user_feed_data = data.get('data', {}).get('xdt_api__v1__feed__user_timeline_graphql_connection', {}) if data.get('data', {}) else {}

            # Extract individual post details
            post_data = user_feed_data.get('edges', []) if user_feed_data else []
            if post_data:
                for post in post_data:
                    node_data = {}
                    node = post.get('node', {})
                    if node:
                        # post_code = node.get('code', '')  # Post shortcode
                        posted_at = node.get('taken_at', '')
                        if posted_at:
                            # Convert timestamp to readable format
                            dt = datetime.utcfromtimestamp(posted_at)
                            posted_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                        # caption = node.get('caption', {}).get('text', '') if node.get('caption', {}) else ''

                        # Extract image URL (if available)
                        image_versions = node.get('image_versions2', {}).get('candidates', []) if node.get('image_versions2', {}) else []
                        post_media = image_versions[0].get('url', '') if image_versions else ''

                        # Extract other post details
                        node_data = {
                            'post_code': node.get('code', ''),  # Unique post identifier
                            'posted_at': posted_at,  # Timestamp of post
                            'caption': node.get('caption', {}).get('text', '') if node.get('caption', {}) else '',  # Post caption
                            'post_media': post_media,  # Post image URL
                            'comment_count': node.get('comment_count', 0),  # Number of comments
                            'like_count': node.get('like_count', 0),  # Number of likes
                            'location': node.get('location', {})  # Location details
                        }
                        posts_data.append(node_data)
    except Exception as e:
        print(f"❌ Error fetching posts: {e}")

    return posts_data

def post_serialize(post):
    """
    Serialize the given post data.
    """
    return {
        'post_url': f"{BASE_URL}/p/{post['post_code']}",
        'post_media': post['post_media'],
        'posted_at': post['posted_at'],
        'comments': post['comment_count'],
        'likes': post['like_count'],
    }

def process_instagram_data(profile, posts):
    """
    Process Instagram profile and post data for analytics.
    """
    # Extract user profile details
    user_profile = {
        'username': profile['username'],
        'full_name': profile['full_name'],
        'biography': profile['biography'],
        'profile_pic': profile['profile_pic'],
        'is_verified': profile['is_verified'],
        'followers': profile['follower_count'],
        'followings': profile['following_count'],
        'posts': profile['media_count'],
    }

    latest_post = post_serialize(posts[0])

    most_liked_post = max(posts, key=lambda x: x.get("like_count", 0))  # Post with the highest likes
    most_commented_post = max(posts, key=lambda x: x.get("comment_count", 0))  # Post with highest comments

    # Generate last 30 days
    last_30_days = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]

    # Format the data for analytics
    formatted_data = {
        "total_likes": sum(post.get("like_count", 0) for post in posts),  # Total Likes
        "total_comments": sum(post.get("comment_count", 0) for post in posts),  # Total Comments
        "most_liked_post": post_serialize(most_liked_post),
        "most_commented_post": post_serialize(most_commented_post),
        "last_30d_post_frequency": {date: 0 for date in last_30_days},  # Initialize all last 30 days with 0
        "last_30p_likes": [],  # Stores last 30 posts likes
        "last_30p_comments": [],  # Stores last 30 posts comments
    }

    # Populate post frequency, likes and comments
    for i, post in enumerate(posts):
        date_str = post.get("posted_at", "").split(" ")[0]

        # Update post count only if the date is in last_30_days
        if date_str in formatted_data["last_30d_post_frequency"]:
            formatted_data["last_30d_post_frequency"][date_str] += 1

        # Store last 30 post likes and comments
        if i < 30:
            serialized_post = post_serialize(post)
            formatted_data["last_30p_likes"].append({'date': date_str, 'likes': post.get('like_count', 0), 'post': serialized_post.get('post_url', '')})
            formatted_data["last_30p_comments"].append({'date': date_str, 'comments': post.get('comment_count', 0), 'post': serialized_post.get('post_url', '')})

    # Combine all data into a single dictionary
    formatted_data["last_30p_likes"].reverse()
    formatted_data["last_30p_comments"].reverse()
    final_data = {
        'profile': user_profile,
        'latest_post': latest_post,
        'analytics': formatted_data
    }

    return final_data

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    video_id_match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    return video_id_match.group(1) if video_id_match else None

def get_comments(video_id):
    """Fetch comments from YouTube API."""
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )
    response = request.execute()

    while response:
        for item in response['items']:
            snippet = item['snippet']['topLevelComment']['snippet']
            comment = snippet['textDisplay']
            comments.append(comment)
            # comments.append({
            #     "Author": snippet['authorDisplayName'],
            #     "Comment": snippet['textDisplay'],
            #     "Author Profile": snippet['authorProfileImageUrl'],
            #     "Author Channel": snippet['authorChannelUrl'],
            #     "Created At": snippet['publishedAt'],
            #     "Updated At": snippet['updatedAt']
            # })

        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100
            )
            response = request.execute()
        else:
            break

    return comments

def analyze_sentiment(comment):
    """Perform sentiment analysis using VADER."""
    score = sia.polarity_scores(comment)['compound']
    return 1 if score > 0.05 else 0 if score < -0.05 else 1

def translate_comment(comment):
    """Translate non-English comments using Google Translator."""
    try:
        lang = detect(comment)
        if lang != "en":
            return GoogleTranslator(source='auto', target='en').translate(comment)
        return comment
    except:
        return comment

def get_wordnet_pos(treebank_tag):
    """
    Convert POS tags from Penn Treebank format to WordNet format for lemmatization.

    Parameters:
    - treebank_tag (str): POS tag in Penn Treebank format.

    Returns:
    - WordNet POS tag if applicable, else default to 'n' (noun).
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ  # Adjective
    elif treebank_tag.startswith('V'):
        return wordnet.VERB  # Verb
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN  # Noun
    elif treebank_tag.startswith('R'):
        return wordnet.ADV  # Adverb
    else:
        return wordnet.NOUN  # Default to noun

def text_pre_processing(text):
    """
    Preprocesses a given text by removing HTML tags, converting emojis to text,
    tokenizing, normalizing case, removing stop words, and lemmatizing words.
    """
    # Remove HTML tags
    clean_text = re.sub(r'<.*?>', '', text)

    # Remove special characters (keep only words, numbers, and spaces)
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', clean_text)

    # Convert emojis to their textual representation
    clean_text = emoji.demojize(clean_text).replace('_', ' ')

    # Convert to lowercase
    clean_text = clean_text.lower()

    # Normalize spaces (removes extra spaces and newlines)
    clean_text = ' '.join(clean_text.split())

    # Tokenize the text
    words = word_tokenize(clean_text)

    # Remove stop words
    words = [word for word in words if word not in stop_words]

    # Get POS tags
    pos_tags = pos_tag(words)

    # Lemmatize words using their POS tags
    lemmatized_sentence = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tags]

    # Join words back into a sentence
    return ' '.join(lemmatized_sentence)

def text_emotion(text):
    """
    Detects the primary emotion in a given text using a pre-trained emotion classification model.

    Parameters:
        text (str): The input text for emotion analysis.

    Returns:
        str: The detected emotion (e.g., "Happy", "Sad", "Angry", etc.).
    """

    # Analyze the text using the pre-trained classifier
    result = text_classifier(text)

    # Extract the emotion label and capitalize the first letter
    return result['label'].capitalize()

def final_sentiment_result(comments, results):
    words = [comment.split() for comment in comments]
    words = [word for sublist in words for word in sublist if len(word) > 2]
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(25)
    most_common_words = [word for word, _ in most_common_words]

    st = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        emotions = list(executor.map(text_emotion, comments))
    print(f'Emotion detection completed in {int(time.time() - st)}s')
    print('Emotions:', emotions)

    pos = results.count(1)
    neg = results.count(0)
    total = len(results)
    pos_percent = round((pos / total) * 100, 2)
    neg_percent = round((neg / total) * 100, 2)

    if pos > neg:
        video_type = "This video is mostly positive based on viewer comments."
    elif neg > pos:
        video_type = "This video is mostly negative based on viewer comments."
    else:
        video_type = "This video has a balanced mix of positive and negative comments."

    final_result = {}
    overall_result = {
        'neg': f'{neg_percent}%',
        'pos': f'{pos_percent}%',
        'video_type': video_type
    }

    final_result['ove_res'] = overall_result
    final_result['graph_data'] = {'pos': pos, 'neg': neg, 'total': total}
    final_result['most_common_words'] = most_common_words
    return final_result

def process_batch(comments_batch):
    """Ek batch ka pura processing flow handle karega"""
    
    print(f'Processing batch of {len(comments_batch)} comments...')
    
    # 1. Translate comments
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        translated_comments = list(executor.map(translate_comment, comments_batch))

    # 2. Pre-process comments
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        pre_processed_comments = list(executor.map(text_pre_processing, translated_comments))

    # 3. Sentiment analysis
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        sentiment_results = list(executor.map(analyze_sentiment, pre_processed_comments))
    
    return pre_processed_comments, sentiment_results

def ytb_comments_sentiment_analysis(video_url):
    """Main function to fetch comments and perform sentiment analysis."""
    st = time.time()
    video_id = extract_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL.")
        return

    print('Fetching comments...')
    start_time = time.time()
    comments = get_comments(video_id)
    print(f'Fetched {len(comments)} comments in {int(time.time() - start_time)}s')

    # # Parallel translation of non-English comments
    # print('Translating comments...')
    # start_time = time.time()
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     translated_comments = list(executor.map(translate_comment, comments))
    # print(f'Translation completed in {int(time.time() - start_time)}s')

    # # Pre processing on comments
    # start_time = time.time()
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     pre_processed_comments = list(executor.map(text_pre_processing, translated_comments))

    # # Sentiment analysis on comments
    # start_time = time.time()
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     sentiment_results = list(executor.map(analyze_sentiment, pre_processed_comments))
    # print(f'Sentiment analysis completed in {int(time.time() - start_time)}s')
    all_preprocessed = []
    all_results = []
    BATCH_SIZE = 200
    comment_batches = [comments[i:i+BATCH_SIZE] for i in range(0, len(comments), BATCH_SIZE)]
    for batch in comment_batches:
        pre_processed_comments, sentiment_results = process_batch(batch)
        all_preprocessed.extend(pre_processed_comments)
        all_results.extend(sentiment_results)

    result = final_sentiment_result(all_preprocessed, all_results)
    print('Result:', result)
    print(f'Full process completed in {int(time.time() - st)}s')


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=sxmFfNLT4tI'
    api_key = "AIzaSyDtNHmz8N5bGVV24aAwQw4h3B3mbSccCjc" 
    youtube = build("youtube", "v3", developerKey=api_key)
    # url = input('Enter a video URL: ')
    ytb_comments_sentiment_analysis(url)
