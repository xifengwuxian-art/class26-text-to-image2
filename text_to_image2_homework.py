# styled_image_creator.py


import time
import requests
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from config import HF_API_KEY

# Same robust HF router setup as your reference script
MODELS = [
    "stabilityai/stable-diffusion-3-medium-diffusers",  # keep your original as primary
    "ByteDance/SDXL-Lightning",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
]

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "image/png"}

def generate_image_from_text(prompt):
    """Generates an image from a text prompt using HF router fallbacks."""
    payload, last_err = {"inputs": prompt}, None

    for model in MODELS:
        url = f"https://router.huggingface.co/hf-inference/models/{model}"

        for _ in range(3):
            r = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            ct = (r.headers.get("content-type") or "").lower()

            # model loading on HF commonly returns 503 + JSON with estimated_time
            if r.status_code == 503 and "application/json" in ct:
                try:
                    wait_s = int(r.json().get("estimated_time", 5))
                except Exception:
                    wait_s = 5
                time.sleep(wait_s + 1)
                continue

            # success (non-json image bytes)
            if r.status_code == 200 and "application/json" not in ct:
                try:
                    return Image.open(BytesIO(r.content)).convert("RGB")
                except Exception as e:
                    last_err = f"Request failed with status code 200: Could not decode image bytes: {e}"
                    break

            # error body
            try:
                body = r.json() if "application/json" in ct else r.text
            except Exception:
                body = r.text
            last_err = f"Request failed with status code {r.status_code}: {body}"
            break

    raise Exception(last_err or "Request failed with status code 500: Unknown error")

def daylight_effect(image):
    image = ImageEnhance.Brightness(image).enhance(1.3)
    image = ImageEnhance.Contrast(image).enhance(1.1)
    return image.filter(ImageFilter.GaussianBlur(radius=1))

def night_mood_effect(image):
    image = ImageEnhance.Brightness(image).enhance(0.9)
    image = ImageEnhance.Contrast(image).enhance(1.4)
    return image.filter(ImageFilter.GaussianBlur(radius=0.5))

def main():
    print("Welcome to the AI Image Stylist Project!")
    prompt = input("Enter your image description:\n").strip()

    try:
        print("Generating your base image...\n")
        image = generate_image_from_text(prompt)

        print("Applying Daylight Edition style...")
        daylight_img = daylight_effect(image)
        daylight_img.show()
        daylight_img.save(f"{prompt.replace(' ', '_')}_daylight.png")
        print("Daylight Edition saved.\n")

        print("Applying Night Mood style...")
        night_img = night_mood_effect(image)
        night_img.show()
        night_img.save(f"{prompt.replace(' ', '_')}_night.png")
        print("Night Mood saved.\n")

    except Exception as e:
        print(f"Something went wrong: {e}")

if __name__ == "__main__":
    main()
