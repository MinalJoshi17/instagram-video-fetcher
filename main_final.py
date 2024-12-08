import os
import requests
import instaloader


FLIC_TOKEN = "flic_b083be3bf15e7f9e78032b213ae877b7774d652971c45f3f4807b7da6fab19a4"
CATEGORY_ID = 25

# Directory for storing downloaded videos
DOWNLOAD_DIR = './downloads'

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def fetch_instagram_videos(username):
    """
    Fetches video URLs from a public Instagram profile.
    """
    print(f"Fetching Instagram videos from user {username}...")
    loader = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        video_urls = []

        for post in profile.get_posts():
            if post.is_video:
                video_urls.append(post.video_url)
            if len(video_urls) >= 10:  # Limit to 10 videos per user
                break
        return video_urls
    except Exception as e:
        print(f"Error fetching videos from user {username}: {e}")
        return []

def download_video(url, filename):
    """
    Downloads a video from a given URL.
    """
    print(f"Downloading {filename}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {filename}.")
    except Exception as e:
        print(f"Error downloading video {filename}: {e}")

def generate_upload_url():
    """
    Sends a request to generate the upload URL.
    """
    upload_url_endpoint = "https://api.socialverseapp.com/posts/generate-upload-url"
    
    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    
    response = requests.get(upload_url_endpoint, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Upload URL Response: ", data)  # Debugging print
        upload_url = data.get("url")  # Corrected key
        video_hash = data.get("hash")  # Corrected key
        
        if upload_url and video_hash:
            return upload_url, video_hash
        else:
            print("Failed to retrieve upload URL or video hash.")
            return None, None
    else:
        print(f"Error generating upload URL: {response.status_code} - {response.text}")
        return None, None

def upload_video(upload_url, video_path):
    """
    Uploads the video to the pre-signed URL.
    """
    try:
        with open(video_path, 'rb') as video_file:
            upload_response = requests.put(upload_url, data=video_file)
            upload_response.raise_for_status()  # Raise exception for HTTP errors
            
            print(f"Video uploaded successfully: {video_path}")
            return True
    except Exception as e:
        print(f"Error uploading video {video_path}: {e}")
        return False

def create_post(video_hash, video_path):
    """
    Creates a post after the video is uploaded.
    """
    create_post_url = "https://api.socialverseapp.com/posts"
    post_data = {
        "title": f"Uploaded Video - {os.path.basename(video_path)}",
        "hash": video_hash,
        "is_available_in_public_feed": False,
        "category_id": CATEGORY_ID
    }
    
    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        post_response = requests.post(create_post_url, json=post_data, headers=headers)
        post_response.raise_for_status()
        
        print("Post created successfully.")
        return True
    except Exception as e:
        print(f"Error creating post for {video_path}: {e}")
        return False

def process_video(usernames=None):
    """
    Main function to download and upload videos.
    """
    video_urls = []

    # Fetch videos from multiple Instagram accounts
    if usernames:
        for username in usernames:
            video_urls.extend(fetch_instagram_videos(username))

    if not video_urls:
        print("No videos found.")
        return

    for idx, video_url in enumerate(video_urls[:20]):  # Limit to 20 videos
        video_filename = os.path.join(DOWNLOAD_DIR, f"video_{idx + 1}.mp4")
        download_video(video_url, video_filename)

        # Generate upload URL and video hash
        upload_url, video_hash = generate_upload_url()
        if upload_url and video_hash:
            # Upload the video
            if upload_video(upload_url, video_filename):
                # Create post after uploading video
                create_post(video_hash, video_filename)
            os.remove(video_filename)  # Remove local file after upload
        else:
            print(f"Skipping video {video_filename} due to upload URL failure.")

# Run the bot
if __name__ == "__main__":
    process_video(usernames=["motivationloft", "motivationdaily.ig","4secondsquotivation"])

