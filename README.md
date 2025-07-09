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

