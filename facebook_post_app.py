# facebook_post_app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Facebook API configuration
def get_fb_credentials():
    access_token = os.getenv("FB_ACCESS_TOKEN")
    page_id = os.getenv("FB_PAGE_ID")
    return access_token, page_id

# Initialize session state
if 'post_created' not in st.session_state:
    st.session_state.post_created = False
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

# Streamlit app
st.set_page_config(
    page_title="Facebook Post Creator",
    page_icon="📱",
    layout="centered"
)

# Custom CSS styling
st.markdown("""
    <style>
    .header {
        font-size: 2.5rem;
        color: #1877F2;
        text-align: center;
        margin-bottom: 30px;
    }
    .subheader {
        font-size: 1.2rem;
        color: #444;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #1877F2 !important;
        color: white !important;
        font-weight: bold;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    .stTextArea textarea {
        border-radius: 10px;
        padding: 15px;
    }
    .success-box {
        background-color: #e6f7ff;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        border-left: 5px solid #1877F2;
    }
    .image-preview {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .credential-box {
        background-color: #f0f2f5;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# App header
st.markdown('<p class="header">📱 Facebook Post Creator</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Create and publish posts directly to your Facebook Page</p>', unsafe_allow_html=True)

# Sidebar for credentials
with st.sidebar:
    st.subheader("🔐 Facebook API Configuration")
    st.info("Get credentials from the [Facebook Developers Portal](https://developers.facebook.com/)")
    
    use_custom_creds = st.checkbox("Use custom credentials", value=False)
    
    if use_custom_creds:
        access_token = st.text_input("Access Token", type="password")
        page_id = st.text_input("Page ID")
    else:
        access_token, page_id = get_fb_credentials()

# Main content
tab1, tab2 = st.tabs(["📝 Create Post", "ℹ️ Instructions"])

with tab1:
    # Post composition area
    with st.form("post_form"):
        post_content = st.text_area(
            "Post Content", 
            height=200,
            placeholder="What do you want to share?",
            max_chars=5000
        )
        
        # Character counter
        char_count = len(post_content)
        st.caption(f"Characters: {char_count}/5000")
        
        # Post options
        col1, col2 = st.columns(2)
        with col1:
            post_type = st.radio("Post Type", ["Text", "Text with Image"], index=0)
        
        with col2:
            scheduling = st.radio("Post Timing", ["Post Now", "Schedule for later"])
        
        # Image upload
        if post_type == "Text with Image":
            uploaded_file = st.file_uploader(
                "Upload an image", 
                type=["jpg", "jpeg", "png"],
                key="image_uploader"
            )
            
            if uploaded_file is not None:
                try:
                    image = Image.open(uploaded_file)
                    st.session_state.uploaded_image = image
                    st.image(
                        image, 
                        caption="Image Preview",
                        use_column_width=True,
                        output_format="JPEG"
                    )
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")
        
        # Scheduling options
        schedule_time = None
        if scheduling == "Schedule for later":
            schedule_time = st.date_input("Schedule Date") 
            schedule_time = st.time_input("Schedule Time")
        
        # Submit button
        submit_button = st.form_submit_button("🚀 Publish Post")

# Post submission handling
if submit_button:
    if not access_token or not page_id:
        st.error("❌ Please provide valid Facebook credentials")
    elif not post_content:
        st.error("❌ Post content cannot be empty")
    else:
        try:
            with st.spinner("Publishing your post..."):
                # Facebook API endpoint
                url = f"https://graph.facebook.com/{page_id}/feed"
                
                # Prepare parameters
                params = {
                    "access_token": access_token,
                    "message": post_content
                }
                
                # Handle image upload
                files = {}
                if post_type == "Text with Image" and st.session_state.uploaded_image:
                    # Convert PIL image to bytes
                    img_byte_arr = io.BytesIO()
                    st.session_state.uploaded_image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Create payload for photo upload
                    photo_url = f"https://graph.facebook.com/{page_id}/photos"
                    files = {'source': ('image.jpg', img_byte_arr, 'image/jpeg')}
                    photo_response = requests.post(
                        photo_url,
                        params={"access_token": access_token},
                        files=files
                    )
                    photo_data = photo_response.json()
                    
                    if 'id' in photo_data:
                        params['attached_media'] = f"[{{'media_fbid':'{photo_data['id']}'}}]"
                    else:
                        st.warning("⚠️ Image upload failed, posting text only")
                
                # Handle scheduling
                if scheduling == "Schedule for later" and schedule_time:
                    from datetime import datetime
                    scheduled_time = datetime.combine(schedule_time, schedule_time)
                    params['published'] = 'false'
                    params['scheduled_publish_time'] = int(scheduled_time.timestamp())
                
                # Post to Facebook
                if files:
                    response = requests.post(url, params=params, files=files)
                else:
                    response = requests.post(url, params=params)
                
                response_data = response.json()
                
                if 'id' in response_data:
                    st.session_state.post_created = True
                    st.success("✅ Post created successfully!")
                    st.balloons()
                    
                    # Show post details
                    with st.expander("Post Details", expanded=True):
                        st.markdown(f"**Post ID:** `{response_data['id']}`")
                        st.markdown(f"**Content:** {post_content}")
                        if scheduling == "Schedule for later":
                            st.markdown(f"**Scheduled Time:** {schedule_time}")
                        if st.session_state.uploaded_image:
                            st.image(
                                st.session_state.uploaded_image, 
                                caption="Posted Image",
                                width=300
                            )
                else:
                    st.error(f"❌ Failed to create post: {response_data.get('error', {}).get('message', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Success message
if st.session_state.post_created:
    st.markdown("""
    <div class="success-box">
        <h3>🎉 Post Created Successfully!</h3>
        <p>Your content has been published to Facebook.</p>
        <p>Refresh the page to create a new post.</p>
    </div>
    """, unsafe_allow_html=True)

# Instructions tab
with tab2:
    st.subheader("📌 How to Use This App")
    st.markdown("""
    1. **Get Facebook Credentials:**
        - Go to the [Facebook Developers Portal](https://developers.facebook.com/)
        - Create an app and get an access token
        - Make sure your app has the **pages_manage_posts** permission
        - Get your Page ID from your Facebook Page settings
        
    2. **Configure Credentials:**
        - Option 1: Add credentials to `.env` file
        - Option 2: Use the sidebar to input credentials directly
        
    3. **Create Your Post:**
        - Write your post content
        - Choose to add an image if needed
        - Select whether to post immediately or schedule for later
        
    4. **Publish:**
        - Click the "Publish Post" button
        - Your post will appear on your Facebook Page
    """)
    
    st.subheader("🔒 Security Note")
    st.warning("""
    - Never share your access token publicly
    - Store credentials securely using environment variables
    - Add `.env` to your `.gitignore` file if using version control
    """)
    
    st.subheader("⚠️ Troubleshooting")
    st.markdown("""
    - **Invalid Credentials:** Ensure your access token is valid and has the correct permissions
    - **Image Upload Issues:** Use JPG or PNG format, max 10MB
    - **API Errors:** Check the Facebook Graph API documentation for error codes
    """)
    
    st.subheader("📚 Facebook API Documentation")
    st.markdown("[Facebook Graph API Reference](https://developers.facebook.com/docs/graph-api)")
