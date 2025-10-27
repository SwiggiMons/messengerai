from fastapi import FastAPI, Request, Response
import requests
import openai
import os
from dotenv import load_dotenv

# 🔹 Load biến môi trường từ file .env
load_dotenv()

# 🔹 Khai báo các biến cần thiết
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")   # Token Facebook Page
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "aimessengerchatbot")
  # Token để verify webhook

openai.api_key = OPENAI_API_KEY

# 🔹 Khởi tạo FastAPI app
app = FastAPI()

# ✅ Endpoint test server
@app.get("/")
def home():
    return {"message": "🤖 AI Messenger Bot is running and ready to chat!"}


# ✅ Facebook Webhook Verification
@app.get("/webhook")
async def verify_webhook(request: Request):
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        print("🧩 DEBUG Webhook verify:", mode, token, challenge)
        print("VERIFY_TOKEN in server:", VERIFY_TOKEN)

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verified successfully!")
            return Response(content=challenge, media_type="text/plain", status_code=200)
        else:
            print("❌ Verification failed.")
            return Response(content="Verification failed", status_code=403)
    except Exception as e:
        print(f"🔥 Webhook verify error: {e}")
        return Response(content="Internal server error", status_code=500)



# ✅ Xử lý tin nhắn người dùng gửi đến page
@app.post("/webhook")
async def receive_message(request: Request):
    try:
        data = await request.json()

        for entry in data.get("entry", []):
            for message_event in entry.get("messaging", []):
                sender_id = message_event["sender"]["id"]

                # Nếu người dùng gửi tin nhắn text
                if "message" in message_event:
                    user_message = message_event["message"].get("text", "")
                    if user_message:
                        reply = ai_reply(user_message)
                        send_message(sender_id, reply)

        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook message error: {e}")
        return {"status": "error", "detail": str(e)}


# 🔹 Hàm sinh phản hồi bằng AI
def ai_reply(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly AI assistant 💬."},
                {"role": "user", "content": prompt},
            ],
            temperature=1.0,
            max_tokens=200,
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        print(f"AI Error: {e}")  # in ra log Render
        return f"AI error: {e}"
        return "Oops! Something went wrong with the AI response 😅"


# 🔹 Gửi tin nhắn lại cho người dùng qua Facebook Graph API
def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v20.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }

    try:
        response = requests.post(url, params=params, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Send message failed: {e}")
