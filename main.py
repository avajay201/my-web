from amazon import start_amazon_scrapper
import face_recognition
from flipkart import start_flipkart_scrapper
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from google_news import start_g_news_scrapper
import imghdr
import json
from myntra import start_myntra_scrapper
import requests
from utils import fetch_face_locations, image_normalize, get_user_id, get_profile, get_posts, process_instagram_data


app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/scrapers', methods=['GET'])
def scrapers():
    """
    Supported Scrapers Endpoint
    
    This endpoint returns a list of supported e-commerce platforms and news sources for web scraping.
    
    Response:
        - 200: Returns a list of supported sources.
    """
    return jsonify([{ "Flipkart": "flipkart" }, { "Amazon": "amazon" }, { "Myntra": "myntra" }, { "Google News": "g-news" }])

@app.route('/scrape', methods=['POST'])
def scrape():
    """
    Web Scraping Endpoint
    
    This endpoint handles search requests for different e-commerce platforms and news sources.
    
    Request JSON Parameters:
        - search_key (str): The keyword to search for. Must be at least 3 characters long.
        - search_from (str): The source to search from. Must be one of ['amazon', 'flipkart', 'myntra', 'g-news'].
    
    Response:
        - 200: Returns search results from the specified source.
        - 400: If required parameters are missing or invalid.
    """
    search_resources = ['amazon', 'flipkart', 'myntra', 'g-news']
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid input. Request body must be a valid JSON.'}), 400

    search_key = data.get('search_key')
    search_from = data.get('search_from')

    if not search_key:
        return jsonify({'error': 'Missing required parameter: search_key'}), 400
    if not search_from:
        return jsonify({'error': 'Missing required parameter: search_from'}), 400

    search_key = search_key.strip()

    if len(search_key) < 3:
        return jsonify({'error': 'search_key must have at least 3 characters.'}), 400

    if search_from not in search_resources:
        return jsonify({'error': 'search_from must be one of {}'.format(search_resources)}), 400

    # Perform web scraping based on the selected source
    result = []
    if search_from == 'amazon':
        result = start_amazon_scrapper(search_key)
    elif search_from == 'flipkart':
        result = start_flipkart_scrapper(search_key)
    elif search_from == 'myntra':
        result = start_myntra_scrapper(search_key)
    elif search_from == 'g-news':
        result = start_g_news_scrapper(search_key)

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, sort_keys=False),
        status=200,
        mimetype='application/json'
    )

@app.route('/detect_face', methods=['POST'])
def detect_face():
    """
    Face Detection Endpoint

    This endpoint checks whether a given image contains a single human face.

    Request:
        - image (binary): Multipart form-data containing the image file.

    Response:
        - 200: If exactly one face is detected.
        - 400: If no face or multiple faces are detected.
        - 400: If the image file is missing or invalid.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    # Check image is valid or not
    if file.filename.split('.')[-1] not in ['jpg', 'jpeg', 'png'] and file.mimetype.split('/')[-1] not in ['jpg', 'jpeg', 'png']:
        return jsonify({'error': 'Invalid image file'}), 400

    try:
        img = image_normalize(file)

        if img is None:
            return {"error": "Invalid image"}, 400

        face_locations = fetch_face_locations(img)

        if len(face_locations) > 1:
            return jsonify({'error': 'Multiple faces detected.'}), 400
        elif len(face_locations) == 1:
            return jsonify({'message': 'Success'}), 200
        else:
            return jsonify({'error': 'No face detected.'}), 400
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': 'Something went wrong'}), 500

@app.route('/compare_faces', methods=['POST'])
def compare_faces():
    """
    Endpoint to verify if a face in a live camera frame matches a stored image.

    Request (multipart/form-data):
        - image (file): A stored image file (JPG, JPEG, PNG).
        - frame (file): A live camera frame captured from the camera.

    Response:
        - If both images contain a single face: Returns match result (True/False).
        - If any image does not contain a face: Returns an error message.
    """

    # Ensure both files exist in the request
    if 'image' not in request.files or 'frame' not in request.files:
        return jsonify({'error': 'Both image and frame are required'}), 400

    file_image = request.files['image']
    file_frame = request.files['frame']

    # Reset file pointers (Fix for multiple reads issue)
    file_image.seek(0)
    file_frame.seek(0)

    # Validate image format (should be JPG, JPEG, or PNG)
    try:
        valid_extensions = ['jpg', 'jpeg', 'png']
        if (
            imghdr.what(file_image) not in valid_extensions or 
            imghdr.what(file_frame) not in valid_extensions
        ):
            return jsonify({'error': 'Invalid image format. Only JPG, JPEG, and PNG are supported'}), 400

        # Decode image using OpenCV
        img1 = image_normalize(file_image)
        img2 = image_normalize(file_frame)

        if img1 is None or img2 is None:
            return {"error": "Invalid image"}, 400

        # Detect faces in both images
        face_locations1 = fetch_face_locations(img1)
        face_locations2 = fetch_face_locations(img2)

        # Validate that exactly one face exists in each image
        if len(face_locations1) != 1:
            return jsonify({'error': 'The stored image must contain exactly one face'}), 400
        if len(face_locations2) != 1:
            return jsonify({'error': 'The live frame must contain exactly one face'}), 400

        # Encode faces (convert to numerical representation)
        face_encoding1 = face_recognition.face_encodings(img1)
        face_encoding2 = face_recognition.face_encodings(img2)

        if not face_encoding1 or not face_encoding2:
            return jsonify({'error': 'Something went wrong'}), 500

        # Compare faces
        match_result = face_recognition.compare_faces([face_encoding1[0]], face_encoding2[0])[0]
        # similarity_score = np.linalg.norm(face_encoding1[0] - face_encoding2[0])  # Lower score = more similar

        return jsonify({
            'matched': bool(match_result),
            # 'similarity_score': f'{100 - similarity_score * 100}%'
        }), 200
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': 'Something went wrong'}), 500

@app.route('/insta-analytics', methods=['POST'])
def insta_analytics():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    user_id = get_user_id(username)
    if not user_id:
        return jsonify({'error': 'User not found'}), 404

    profile = get_profile(user_id)
    if not profile:
        return jsonify({}), 200

    posts = get_posts(username)
    if not posts:
        return jsonify({}), 200

    response_data = process_instagram_data(profile, posts)

    return jsonify(response_data), 200

@app.route('/fetch-image', methods=['GET'])
def proxy():
    image_url = request.args.get("url")  # Get image URL from query param
    if not image_url:
        return "Missing URL", 400

    try:
        response = requests.get(image_url, stream=True)  # Fetch image from Instagram
        response.raise_for_status()
        
        return Response(response.content, content_type=response.headers['Content-Type'])  # Serve image
    except Exception:
        return "Image fetch failed", 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
