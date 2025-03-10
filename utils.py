from bs4 import BeautifulSoup
import cv2
from datetime import datetime, timedelta
import face_recognition
import json
import numpy as np
import re
import requests
import time
from transformers import pipeline


BASE_URL = 'https://www.instagram.com'
# sentiment_analysis = pipeline("sentiment-analysis",model="siebert/sentiment-roberta-large-english")

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
        # "av": "17841409795510157",
        # "__d": "www",
        # "__user": "0",
        # "__a": "1",
        # "__req": "1k",
        # "__hs": "20149.HYP:instagram_web_pkg.2.1...1",
        # "dpr": "1",
        # "__ccg": "EXCELLENT",
        # "__rev": "1020522147",
        # "__s": "un3lap:dtv0g6:ocpd5e",
        # "__hsi": "7477116263966954821",
        # "__dyn": "7xeUjG1mxu1syUbFp41twpUnwgU7SbzEdF8aUco2qwJxS0DU2wx609vCwjE1EE2Cw8G11wBz81s8hwGxu786a3a1YwBgao6C0Mo2swtUd8-U2zxe2GewGw9a361qw8Xxm16wUwtE1wEbUGdG1QwTU9UaQ0Lo6-3u2WE5B08-269wr86C1mwPwUQp1yUb8jK5V8aUuwm8jxK2K2G0EoKmUhw",
        # "__csr": "iM9A5cIh5l2vsIJY_nQBRbWRAQqjRAGR8vbHG_hJ6Eyy5uajKq4ox4yV4FlZqt4Rp4_G8yZBDQCUTAl29-mK8ykC-ES_V8GVogALADHhbK9yA8x65ppmlhoKbUjBovpoJ4USbglxdy8SiElGiE-mWxt2Ey48vAG3m7801dZpo5mro2tp9Aigg68-6p6dwa20zu2kEcrBw89w6bgrg0H20lm0cvw2pE5SUS13pP0_xe9Umg8o2iw5kCP95lAizv83elk0FA1izEegCj5x8jwat1G1kx23Wlj0a9a4UrZ0_88wnU4i1hw1i6y00nZqw6Nw1oK",
        # "__comet_req": "7",
        # "fb_dtsg": "NAcPHmr6C42mr_tng7yHPFwtqAY6z6FO1HF1PmfhRDOQ7VFARmy2BeA:17854477105113577:1730355965",
        # "jazoest": "26110",
        # "lsd": "o2qSYT0-MhEFbe1L-2q2kO",
        # "__spin_r": "1020522147",
        # "__spin_b": "trunk",
        # "__spin_t": "1740901792",
        # "fb_api_caller_class": "RelayModern",
        # "fb_api_req_friendly_name": "PolarisProfilePostsTabContentQuery_connection",
        "variables": f'{{"after":null,"before":null,"data":{{"count":{posts},"include_reel_media_seen_timestamp":true,"include_relationship_info":true,"latest_besties_reel_media":true,"latest_reel_media":true}},"first":{posts},"last":null,"username":"{username}","__relay_internal__pv__PolarisIsLoggedInrelayprovider":true,"__relay_internal__pv__PolarisShareSheetV3relayprovider":true}}',
        # "server_timestamps": "true",
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

def is_valid_url(url):
    """
    Check given url is correct url or not
    """
    regex = re.compile(
        r'^(https?:\/\/)?'          # Optional http or https
        r'([a-zA-Z0-9-]+\.)+'       # Subdomain or domain
        r'[a-zA-Z]{2,}'             # Domain extension (like .com, .org)
        r'(:\d+)?'                  # Optional port
        r'(\/\S*)?$'                # Optional path
    )
    return bool(regex.match(url))

def filter_token(json_data):
    token = None
    try:
        token = json_data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][-1]["itemSectionRenderer"]["contents"][0]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
    except Exception as err:
        print('Error', err)
    return token

def scrape_token(video_url):
    token = None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }
        response = requests.get(video_url, timeout=10, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            scripts = soup.find_all('script')
            if scripts:
                match = re.search(r'(\{.*\})', str(scripts[46]))
                if match:
                    json_data = json.loads(match.group(1))
                    token = filter_token(json_data)
                else:
                    print("No JSON-like object found")
            else:
                print('No matching <script> tags found')
    except Exception as err:
        print('Error:', err)

    return token

def extract_continuation_command(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "continuationCommand" and isinstance(value, dict):
                return value.get("token")
            result = extract_continuation_command(value)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = extract_continuation_command(item)
            if result:
                return result
    return None

def video_comments(video_url, token, total_comments_count, c):
    url = 'https://www.youtube.com/youtubei/v1/next?prettyPrint=false'
    headers = {
        "Cookie": "LOGIN_INFO=AFmmF2swRgIhAKFC9HF0waQ-DkfrRPiMcsPDVT5S9fpRtpyykPWP3o80AiEAtojvJVtPG9R0qrYbQ7eVVc-GQFRqSP6NLN_7ryOG1RA:QUQ3MjNmeVE1VmF2LVFUeGhFY0dNMGJHdUtnOVRubG9SWHZ4eFdEVUxhc0lsUUJNZXJoUXJObzRmVTd3eUtMMGFmemZHUVIxenlZMXhYQ0tTNDFsS29jRkpGZmo2ZEhoQXVNV1hWYXFPMDhuSnBfYlJ3QzhNSGp5LWY1amRxV1g0MVZWMUVzODZGR1BZNUlqbmpGcnMzNVVrZGt3VFhyUC1n; VISITOR_INFO1_LIVE=zXxFUxNYULU; VISITOR_PRIVACY_METADATA=CgJJThIEGgAgOA%3D%3D; HSID=AoNFZi0DNQIBFd_Cv; SSID=A11c6GpVw-7LlSeJA; APISID=4R0A_U_etOT3jYJ9/A1nBp0LMfhB16HmKc; SAPISID=brzrbmmtKF9ud2UX/AbHtLUo0AEhYmmI_J; __Secure-1PAPISID=brzrbmmtKF9ud2UX/AbHtLUo0AEhYmmI_J; __Secure-3PAPISID=brzrbmmtKF9ud2UX/AbHtLUo0AEhYmmI_J; SID=g.a000twj9WsskBlDsKij4ojXOrAyxal3kLIaeE2ocybttohIb9-lgrjbc8JEkgke6VpDSg7rYFAACgYKAX8SARASFQHGX2MiK4Ssz74Cac0TufTXexzgsRoVAUF8yKqihxmizdlk4JUPO5t1voCU0076; __Secure-1PSID=g.a000twj9WsskBlDsKij4ojXOrAyxal3kLIaeE2ocybttohIb9-lgPHlRQFHioNr-zIMyfvmXgQACgYKAaQSARASFQHGX2MiTjqyXGV08AM8XEHhfUj1lBoVAUF8yKoOKWAAJ6IustZPehgpx1Ec0076; __Secure-3PSID=g.a000twj9WsskBlDsKij4ojXOrAyxal3kLIaeE2ocybttohIb9-lgm1uvrig348MINIjL08BAagACgYKAcwSARASFQHGX2MiqypJigxPiv8qY_vTzeWegBoVAUF8yKpz9VAUysLKEey5Q_6Mt8DP0076; PREF=tz=Asia.Calcutta&f4=4000000&f7=150&f6=40000000; YSC=tV--KsiT4Dw; __Secure-ROLLOUT_TOKEN=COClz9Gn5aXa9QEQ_MWQ-KPXiQMY5-3Q-_z1iwM%3D; __Secure-1PSIDTS=sidts-CjEBEJ3XV7OF4DtWBrsJVOnldfWNOyC-zPxKkc6ytWzX0XmCn3SZJkHtxkII1p33Fz_TEAA; __Secure-3PSIDTS=sidts-CjEBEJ3XV7OF4DtWBrsJVOnldfWNOyC-zPxKkc6ytWzX0XmCn3SZJkHtxkII1p33Fz_TEAA; SIDCC=AKEyXzXBv_Y-qG23Z26Kzch9nY5-ZHcpo0QmWcNe6GcKW6Hg9GdDjl5kYQV8kgmSLlUHKUa-PQ; __Secure-1PSIDCC=AKEyXzX6Ujm1z_SUSMf0r4thZZgd_84kDV6_x1Jff7CkgMrF4-g5rhg6QjqSxhg9oXRyIWHcDQ; __Secure-3PSIDCC=AKEyXzW-XbcQrs1OKgEG88ffdeZVb-Csx1TOsFmeNvD7yT9LxvBOvqrqdW9I5QpNLXMAxOrNKI0; ST-amrb2j=session_logininfo=AFmmF2swRgIhAKFC9HF0waQ-DkfrRPiMcsPDVT5S9fpRtpyykPWP3o80AiEAtojvJVtPG9R0qrYbQ7eVVc-GQFRqSP6NLN_7ryOG1RA%3AQUQ3MjNmeVE1VmF2LVFUeGhFY0dNMGJHdUtnOVRubG9SWHZ4eFdEVUxhc0lsUUJNZXJoUXJObzRmVTd3eUtMMGFmemZHUVIxenlZMXhYQ0tTNDFsS29jRkpGZmo2ZEhoQXVNV1hWYXFPMDhuSnBfYlJ3QzhNSGp5LWY1amRxV1g0MVZWMUVzODZGR1BZNUlqbmpGcnMzNVVrZGt3VFhyUC1n",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "X-Goog-Visitor-Id": "Cgt6WHhGVXhOWVVMVSjWtae-BjIKCgJJThIEGgAgOA%3D%3D",
    }
    
    json_data = {
        "context": {
            "client": {
                "hl": "en",
                "gl": "IN",
                "remoteHost": "223.178.212.205",
                "deviceMake": "",
                "deviceModel": "",
                "visitorData": "Cgt6WHhGVXhOWVVMVSiy6qy-BjIKCgJJThIEGgAgOA%3D%3D",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36,gzip(gfe)",
                "clientName": "WEB",
                "clientVersion": "2.20250304.01.00",
                "osName": "Windows",
                "osVersion": "10.0",
                "originalUrl": "https://www.youtube.com/",
                "screenPixelDensity": 1,
                "platform": "DESKTOP",
                "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                "configInfo": {
                    "appInstallData": "CLLqrL4GEOHssAUQhL3OHBDL0bEFEOODuCIQ3q2xBRDv2c4cELby_xIQndCwBRCBzc4cEM3RsQUQ39zOHBCdprAFEPirsQUQ4OD_EhCU_rAFEJPZzhwQ8OLOHBCHrM4cENuvrwUQntvOHBC36v4SEMnmsAUQ0-GvBRCv5c4cELfbzhwQudnOHBC9irAFEN_YzhwQkYz_EhDk5_8SEIiHsAUQ1tjOHBC9tq4FEParsAUQ29rOHBDs3s4cEInorgUQmY2xBRCmmrAFEImwzhwQztrOHBCZmLEFEPyyzhwQ18GxBRDgzbEFEN68zhwQ-d3OHBCy6c4cEI3MsAUQiOOvBRC85rAFEInt_xIQyfevBRDM364FEJT8rwUQluTOHBC9mbAFEOLUrgUQ6-j-EhC72c4cELbgzhwQgNHOHBCQsM4cEJbezhwQo_j_EhCq2s4cEM-wzhwqKENBTVNHaFVSb0wyd0ROSGtCdlB0OFF1UDlBN3Ytd2JMSUxiREF4MEg%3D",
                    "coldConfigData": "CLLqrL4GEO-6rQUQvbauBRDi1K4FEL2KsAUQndCwBRDP0rAFELzmsAUQ4_iwBRCkvrEFENfBsQUQktSxBRCJsM4cEJCwzhwQqLDOHBDPsM4cEPayzhwQ_LLOHBDkx84cEJHMzhwQqM7OHBCA0c4cENHWzhwQ5dbOHBDf2M4cEKrazhwQztrOHBCE284cEJPbzhwQntvOHBC3284cEN_czhwQ-d3OHBCW3s4cEOzezhwQvN_OHBC24M4cEPfhzhwQ8OLOHBCW5M4cEPLkzhwQr-XOHBCy6c4cEMjpzhwQh-vOHBDjg7giGjJBT2pGb3gzY0JNQjZ3Sl8xNmcyc1dwV2gzOTdhcVR6TjliME92aTBRbkhTTFdXMVZUUSIyQU9qRm94MXd3NVJCODRYcmtHeDVJdGtSS2FpU0NuWDZiMFV6Z1ZiR09MSGVuNk5BeFEqbENBTVNTdzBadU4yM0F0NFV6ZzJYSDZncXRRUzlGZjBEdXNlYkVQSVZ0d1AyRWFrVUZTNlpzYmNmaGFRRm1yc0dfMW00Z0FJRTVRU3Ryd2JqRWFnVjMxdThxZ2JXUHNkczMzcThpd2J2S0E9PQ%3D%3D",
                    "coldHashData": "CLLqrL4GEhQxNDE0NzI1NzY1NDc2ODQ3MzM2Mhiy6qy-BjIyQU9qRm94M2NCTUI2d0pfMTZnMnNXcFdoMzk3YXFUek45YjBPdmkwUW5IU0xXVzFWVFE6MkFPakZveDF3dzVSQjg0WHJrR3g1SXRrUkthaVNDblg2YjBVemdWYkdPTEhlbjZOQXhRQmxDQU1TU3cwWnVOMjNBdDRVemcyWEg2Z3F0UVM5RmYwRHVzZWJFUElWdHdQMkVha1VGUzZac2JjZmhhUUZtcnNHXzFtNGdBSUU1UVN0cndiakVhZ1YzMXU4cWdiV1BzZHMzM3E4aXdidktBPT0%3D",
                    "hotHashData": "CLLqrL4GEhQxMzEzNDE1NDE5NDQ0MzI1MTIwMhiy6qy-BiiU5PwSKKXQ_RIonpH-EijIyv4SKLfq_hIowIP_EiiRjP8SKLSj_xIopcf_Eii9zv8SKOvZ_xIo4OD_Eijk5_8SKInt_xIo0u3_Eij77f8SKNru_xIotvL_EijN8_8SKMT3_xIoo_j_EjIyQU9qRm94M2NCTUI2d0pfMTZnMnNXcFdoMzk3YXFUek45YjBPdmkwUW5IU0xXVzFWVFE6MkFPakZveDF3dzVSQjg0WHJrR3g1SXRrUkthaVNDblg2YjBVemdWYkdPTEhlbjZOQXhRQixDQU1TSFEwTW90ZjZGYTdCQnBOTjhnb1ZDZDNQd2d6R3AtMEwyTTBKcGNBRg%3D%3D"
                },
                "screenDensityFloat": 1.25,
                "userInterfaceTheme": "USER_INTERFACE_THEME_DARK",
                "timeZone": "Asia/Calcutta",
                "browserName": "Chrome",
                "browserVersion": "133.0.0.0",
                "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "deviceExperimentId": "ChxOelEzT1RFek1EQTVOakkyTURZek1UVXdPUT09ELLqrL4GGLLqrL4G",
                "rolloutToken": "COClz9Gn5aXa9QEQ_MWQ-KPXiQMYspmwr5n7iwM%3D",
                "screenWidthPoints": 1536,
                "screenHeightPoints": 360,
                "utcOffsetMinutes": 330,
                "connectionType": "CONN_CELLULAR_4G",
                "memoryTotalKbytes": "8000000",
                "mainAppWebInfo": {
                    "graftUrl": video_url,
                    "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED",
                    "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                    "isWebNativeShareAvailable": True
                }
            },
            "user": {
                "lockedSafetyMode": False
            },
            "request": {
                "useSsl": True,
                "internalExperimentFlags": [],
                "consistencyTokenJars": []
            },
            "clickTracking": {
                "clickTrackingParams": "CNIDELsvGAMiEwjzy-KDyviLAxXyb50JHeIIHB8="
            }
        },
        "continuation": token
    }

    response = requests.post(url, headers=headers, timeout=10, json=json_data)
    token = None
    fetched_comments = []
    # total_comments_count = 0
    if response.status_code == 200:
        data = response.json()
        try:
            token_key = ''
            for key in data['onResponseReceivedEndpoints'][-1].keys():
                if 'Continuation' in key:
                    token_key = key
                    break
            token = extract_continuation_command(data['onResponseReceivedEndpoints'][-1][token_key]['continuationItems'][-1])
        except KeyError as err:
            print('Error in token:', err)
            pass

        with open(f'data/{c}.json', 'w') as f:
            json.dump(data, f, indent=4)

        if not total_comments_count:
            try:
                total_comments_count = data['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0]['commentsHeaderRenderer']['countText']['runs'][0]['text']
            except KeyError as err:
                # print('Error in total comments count:', err)
                pass

        comments_data = data['frameworkUpdates']['entityBatchUpdate']['mutations']
        for i, comment in enumerate(comments_data):
            try:
                payload = comment['payload']['commentEntityPayload']
                fetched_comments.append(
                    {
                        'text': payload['properties']['content']['content'],
                        'time': payload['properties']['publishedTime'],
                        'owner': payload['author']['displayName'],
                        'owner_avtar': payload['author']['avatarThumbnailUrl'],
                        'likes': payload['toolbar']['likeCountLiked'],
                        'dislikes': payload['toolbar']['likeCountNotliked'],
                        'channel_url': f"https://www.youtube.com/{payload['author']['displayName']}",
                    }
                )
            except KeyError as err:
                # print('Error in comments:', err)
                pass
    else:
        print('Something went wrong! Error Code:', response.status_code)

    return total_comments_count, fetched_comments, token


if __name__ == '__main__':
    url = input('Enter a video URL: ')
    if is_valid_url(url):
        st = time.time()
        token = scrape_token(url)
        total_comments = 0
        fetched_comments = []
        counter = 0
        while token is not None:
            counter += 1
            total_comments, comments, token = video_comments(url, token, total_comments, counter)
            if comments:
                total_comments = int(str(total_comments).replace(",", ""))
                fetched_comments.extend(comments)

            spent_time = int(time.time() - st)
            if spent_time >= 60: # Process only for 1 minute
                print(f'Spent {spent_time} seconds, stopping process stopped due to long time process.')
                break
            if not comments:
                print('No comments')
                break
            if not token:
                print('No token')
                break

        et = time.time()
        with open('comments.json', 'w') as f:
            json.dump(fetched_comments, f, indent=3)

        print('Time:', int(et-st))
        print('Total comments:', len(fetched_comments))
    else:
        print("❌ Invalid URL")
