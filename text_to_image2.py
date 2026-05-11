from huggingface_hub import InferenceClient
from datetime import datetime
from config import HF_API_KEY
from PIL import Image, ImageEnhance, ImageFilter

# MODEL PRIORITY LIST - Primary model first, fallbacks only if it fails
MODELS = [
    "ByteDance/SDXL-Lightning",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "stabilityai/sdxl-turbo",
    "runwayml/stable-diffusion-v1-5", # Fallback 2
]

# Initialize client
client = InferenceClient(api_key=HF_API_KEY)

print(f"Primary model: {MODELS[0]}")
print("Type quit to exit\n")

def post_process_image(image):
    image = ImageEnhance.Brightness(image).enhance(1.2)
    image = ImageEnhance.Contrast(image).enhance(1.3)
    return image.filter(ImageFilter.GaussianBlur(radius=2))

def generate_image_from_text(prompt):
    
    while True:
        prompt = input("Enter prompt:").strip()
        if prompt.lower() in ["quit", "exit", "q"]:
            break
        if not prompt:
            continue
        print("Generating...")
        image = None
    
        for model in MODELS:
            try:
                image = client.text_to_image(prompt, model=model)
                break
            except Exception:
                print("Executing next")
                continue
        if image:
            print("Applying post processing efects...\n")
            processed_image = post_process_image(image)
            processed_image.show()
            print()
            try:
                save_option = input("Do you want to save your image?(Yes/No): ").strip().lower()
                if save_option == "yes":
                    file_name = input("Enter a name for image file without extention: ").strip()
                    processed_image.save(f"{file_name}.png")
                    print(f"Image saved as {file_name}.png\n")
                print("-"*80 + "\n")
            except Exception as e:
                print("An error: ", e)
        else:
            print("Error: All models failed, check your API key!\n")

def main():
    print("Welcome to the magic processing workshop!")
    print("This program generates image form text, and applies post processing efect.")
    print("Type exit to quit.\n")
    
    while True:
        user_input = input("Enter a description for the image (or 'exit' to quit):\n")
        if user_input.lower() == 'exit':
            print("Goodbye~")
            break
        try:
            print("\nGenerating image...")
            image = generate_image_from_text(user_input)
        except Exception as e:
            print(f"An error occurred: {e}\n")


if __name__ == "__main__":
    main()
