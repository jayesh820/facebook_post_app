# facebook_post_app
📱 Facebook Post Creator – Streamlit App
A powerful and user-friendly Facebook Post Creator built using Streamlit. This app allows you to compose, preview, and publish posts directly to your Facebook Page, including support for scheduled posts and image uploads via the Facebook Graph API.

🚀 Key Features
📝 Create Facebook Posts

Write text-only posts or attach an image

Character counter with 5,000-character limit

🖼 Upload Image

Upload and preview JPG/PNG images before posting

Images are uploaded as part of the Facebook photo endpoint and linked to your post

⏰ Schedule Posts

Choose between posting now or scheduling for later

Uses Graph API's scheduled_publish_time feature

🔐 Secure Credential Management

Supports credentials via .env file using dotenv

Option to enter credentials manually in the sidebar

✅ Success Feedback

Displays confirmation with post ID and image preview after successful submission

Includes real-time error handling and API feedback

📚 Built-in Instructions

Integrated tab with clear instructions, usage tips, security warnings, and troubleshooting

🧰 Tech Stack
Python

Streamlit – For the interactive UI

Facebook Graph API – For posting to Facebook Pages

Pillow – For image handling

dotenv – For managing credentials securely

🛠️ Setup Instructions
Clone the Repository

bash
Copy
Edit
git clone https://github.com/your-username/facebook-post-creator.git
cd facebook-post-creator
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Configure Environment Variables

Create a .env file with your credentials:

ini
Copy
Edit
FB_ACCESS_TOKEN=your_facebook_page_access_token
FB_PAGE_ID=your_facebook_page_id
Run the App

bash
Copy
Edit
streamlit run facebook_post_app.py
🔒 Security Warning
Never expose your Facebook access token in public repositories!
Always use .env files and make sure to add .env to your .gitignore.

🖼 Screenshot
(Add your own image here)

📚 Useful Resources
📘 Facebook Graph API Reference

🔧 Facebook Access Token Tool

🧑‍💻 Streamlit Documentation

Let me know if you want a pre-made README.md, .gitignore, or requirements.txt file too.









Ask ChatGPT
You said:
import streamlit as st
import requests
import os
from datetime import datetime
from PIL import Image
import io
import base64

# Page Configuration
st.set_page_config(
    page_title="LinkedIn Post Pro",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
def inject_css():
    st.markdown(f"""
    <style>
        /* Main container */
        .main {{
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
        }}
        
        /* Header styling */
        .header {{
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        
        .header h1 {{
            color: #0a66c2;
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
        }}
        
        /* Card styling */
        .card {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin-bottom: 1.5rem;
        }}
        
        /* LinkedIn button */
        .linkedin-btn {{
            background-color: #0a66c2 !important;
            color: white !important;
            border-radius: 28px !important;
            padding: 0.7rem 1.5rem !important;
            font-weight: 600 !important;
            border: none !important;
            transition: all 0.3s ease;
            display: inline-flex !important;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        
        .linkedin-btn:hover {{
            background-color: #004182 !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(10, 102, 194, 0.3);
        }}
        
        /* Text editor */
        .stTextArea textarea {{
            min-height: 180px !important;
            border-radius: 8px !important;
            padding: 16px !important;
            font-size: 1rem !important;
            border: 1px solid #ddd !important;
        }}
        
        /* Preview card */
        .preview-card {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 1rem;
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .card {{
                padding: 1.5rem;
            }}
        }}
        
        /* Status messages */
        .success-box {{
            background-color: #e6f7ee;
            color: #0d6832;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }}
    </style>
    """, unsafe_allow_html=True)

# LinkedIn API Functions
def get_linkedin_auth_url():
    LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", st.secrets.get("LINKEDIN_CLIENT_ID"))
    REDIRECT_URI = "http://localhost:8501/callback"  # Update for production
    SCOPE = "w_member_social,r_liteprofile"
    return f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={LINKEDIN_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}"

def exchange_code_for_token(code):
    LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", st.secrets.get("LINKEDIN_CLIENT_ID"))
    LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", st.secrets.get("LINKEDIN_CLIENT_SECRET"))
    REDIRECT_URI = "http://localhost:8501/callback"
    
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def get_user_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def post_to_linkedin(access_token, content, image=None):
    # Prepare the post data
    post_data = {
        "author": f"urn:li:person:{st.session_state.user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    # Handle image if provided
    if image:
        # Step 1: Register upload
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        register_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{st.session_state.user_id}",
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }]
            }
        }
        
        register_response = requests.post(register_url, headers=register_headers, json=register_data)
        
        if register_response.status_code == 200:
            upload_url = register_response.json().get("value", {}).get("uploadMechanism", {}).get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
            asset_urn = register_response.json().get("value", {}).get("asset")
            
            # Step 2: Upload image
            if upload_url and asset_urn:
                image_bytes = image.getvalue()
                upload_headers = {"Authorization": f"Bearer {access_token}"}
                upload_response = requests.put(upload_url, headers=upload_headers, data=image_bytes)
                
                if upload_response.status_code in [200, 201]:
                    # Update post data to include image
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                        "status": "READY",
                        "description": {"text": "Image for LinkedIn post"},
                        "media": asset_urn,
                        "title": {"text": "Post Image"}
                    }]
    
    # Step 3: Create post
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    post_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    response = requests.post(post_url, headers=post_headers, json=post_data)
    return response

# UI Components
def display_header():
    st.markdown("""
    <div class="header">
        <h1>LinkedIn Post Pro</h1>
        <p>Create and publish directly to LinkedIn</p>
    </div>
    """, unsafe_allow_html=True)

def display_auth_section():
    if "access_token" not in st.session_state:
        auth_url = get_linkedin_auth_url()
        st.markdown(f"""
        <div class="card">
            <h3 style="text-align: center;">Connect Your LinkedIn Account</h3>
            <p style="text-align: center; margin-bottom: 1.5rem;">
                Authenticate to enable direct posting
            </p>
            <a href="{auth_url}" target="_self">
                <button class="linkedin-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="white">
                        <path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"/>
                    </svg>
                    Connect with LinkedIn
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        return False
    return True

def display_post_form():
    with st.form("post_form", clear_on_submit=True):
        st.subheader("Create New Post")
        
        # Post content
        content = st.text_area(
            "Post Content",
            placeholder="Share your thoughts...\n\nUse hashtags to increase visibility: #LinkedIn #Professional",
            height=200,
            help="Tip: Keep between 300-1000 characters for best engagement"
        )
        
        # Post options
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Add trending hashtags", value=True)
            st.checkbox("Tag connections", value=False)
        with col2:
            schedule = st.checkbox("Schedule post")
            if schedule:
                st.date_input("Date")
                st.time_input("Time")
        
        # Image upload
        image = st.file_uploader(
            "Add image (optional)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False
        )
        
        # Submit buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("Preview"):
                display_post_preview(content, image)
        with col2:
            if st.form_submit_button("Publish Now", type="primary"):
                if content:
                    return content, image
                else:
                    st.warning("Please enter post content")
    return None, None

def display_post_preview(content, image):
    st.subheader("Post Preview")
    with st.container():
        st.markdown("""
        <div class="preview-card">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <img src="https://via.placeholder.com/50" style="border-radius: 50%; margin-right: 1rem;">
                <div>
                    <strong>{name}</strong><br>
                    <span style="color: #666;">{headline}</span>
                </div>
            </div>
            <p>{content}</p>
            {image}
            <div style="display: flex; margin-top: 1rem; color: #666;">
                <span style="margin-right: 1rem;">👍 Like</span>
                <span style="margin-right: 1rem;">💬 Comment</span>
                <span>🔗 Share</span>
            </div>
        </div>
        """.format(
            name=st.session_state.get("user_name", "Your Name"),
            headline=st.session_state.get("user_headline", "Your Headline"),
            content=content or "Your post content will appear here",
            image=f'<img src="data:image/png;base64,{base64.b64encode(image.getvalue()).decode()}" style="width: 100%; border-radius: 8px; margin: 1rem 0;">' if image else ""
        ), unsafe_allow_html=True)

def display_user_profile():
    if "user_info" in st.session_state:
        user = st.session_state.user_info
        st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <img src="https://via.placeholder.com/80" style="border-radius: 50%; margin-bottom: 0.5rem;">
            <h4>{user.get('localizedFirstName', '')} {user.get('localizedLastName', '')}</h4>
            <p style="color: #666;">{user.get('localizedHeadline', '')}</p>
        </div>
        """, unsafe_allow_html=True)

# Main App
def main():
    inject_css()
    display_header()
    
    # Handle LinkedIn callback
    if "code" in st.experimental_get_query_params():
        code = st.experimental_get_query_params()["code"][0]
        access_token = exchange_code_for_token(code)
        if access_token:
            st.session_state.access_token = access_token
            user_profile = get_user_profile(access_token)
            if user_profile:
                st.session_state.user_info = user_profile
                st.session_state.user_id = user_profile.get("id")
                st.session_state.user_name = f"{user_profile.get('localizedFirstName', '')} {user_profile.get('localizedLastName', '')}"
                st.session_state.user_headline = user_profile.get("localizedHeadline", "")
            st.experimental_set_query_params()
            st.experimental_rerun()
    
    # Check authentication
    if display_auth_section():
        # User is authenticated
        display_user_profile()
        
        # Post creation
        content, image = display_post_form()
        
        # Handle post submission
        if content and st.session_state.get("access_token"):
            with st.spinner("Publishing to LinkedIn..."):
                response = post_to_linkedin(st.session_state.access_token, content, image)
                
                if response.status_code == 201:
                    st.markdown("""
                    <div class="success-box">
                        <h4>✅ Post Published Successfully!</h4>
                        <p>Your post is now live on LinkedIn.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error(f"Failed to publish post. Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()


ChatGPT said:
Here's a professional GitHub README.md description for your LinkedIn Post Pro project based on the code you provided:

💼 LinkedIn Post Pro
A modern, secure, and visually sleek Streamlit web app that allows users to compose, preview, and publish posts directly to their LinkedIn profiles via the LinkedIn API. Supports OAuth login, optional image uploads, scheduling UI, and live post previews.

🚀 Features
🔐 OAuth 2.0 Login

Secure authentication via LinkedIn

Automatically fetches user ID and profile info

📝 Create Rich Posts

Write LinkedIn posts with or without images

Add hashtags, tag connections (UI-only), and preview content before posting

🖼 Image Upload

Upload JPEG/PNG images (LinkedIn UGC image handling supported)

📆 Schedule Options (UI)

Schedule section included for future enhancement

🎨 Modern UI

Styled with custom CSS for a native LinkedIn feel

Post previews replicate the LinkedIn feed look

📢 Live Feedback

Spinner, toast messages, balloons, and error handling

Visual success card with publishing confirmation

📸 Preview

(Add your own screenshot of the app here)

🛠️ Tech Stack
Python

Streamlit

LinkedIn API (UGC Posts & Media Upload)

PIL (Pillow) for image handling

requests, base64, dotenv (for secure API use)

⚙️ Setup & Run Locally
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/linkedin-post-pro.git
cd linkedin-post-pro
2. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
3. Set Up LinkedIn App
Visit LinkedIn Developer Portal

Create an app and note:

Client ID

Client Secret

Add OAuth Redirect URI as http://localhost:8501/callback

Add required permissions: r_liteprofile, w_member_social

4. Create a .env file
ini
Copy
Edit
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
💡 Alternatively, use Streamlit’s st.secrets for cloud deployments.

5. Run the App
bash
Copy
Edit
streamlit run linkedin_post_pro.py
🔒 Security Tips
Never expose credentials in public repos

Use .env or st.secrets and add .env to .gitignore

📚 Resources
📘 LinkedIn API Docs

🔧 LinkedIn Auth Guide

🌐 Streamlit Docs

🧠 Future Enhancements
⏰ Full post scheduling support via LinkedIn's API (when enabled)

🏷 Tagging users dynamically

🌍 Multi-account support

🔄 Draft saving and history


