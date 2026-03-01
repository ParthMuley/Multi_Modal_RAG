import os
import pdfplumber
from PIL import Image
import io
import ollama
import google.generativeai as genai
from config import MODEL_PROVIDER, OLLAMA_VISION_MODEL, GEMINI_MODEL, GEMINI_API_KEY

# Configure Gemini if needed
if MODEL_PROVIDER == "GEMINI" and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def extract_images_from_pdf(pdf_path, output_dir="extracted_images"):
    """
    Extracts all images from a PDF file and saves them to the output directory.
    Returns a list of dictionaries with image path and metadata.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    image_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            for j, image_dict in enumerate(page.images):
                try:
                    bbox = (image_dict['x0'], image_dict['top'], image_dict['x1'], image_dict['bottom'])
                    page_image = page.within_bbox(bbox).to_image(resolution=300)
                    
                    image_filename = f"page_{i+1}_img_{j+1}.png"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    page_image.save(image_path)
                    
                    image_data.append({
                        "path": image_path,
                        "page": i + 1,
                        "index": j + 1
                    })
                    print(f"Saved image: {image_path} (Page {i+1})")
                except Exception as e:
                    print(f"Error extracting image {j} from page {i}: {e}")
                    
    return image_data

def generate_caption(image_path):
    """
    Generates a textual description of an image using the selected provider.
    """
    prompt = "Describe this technical diagram or image in detail. Focus on the architecture, components, and their relationships. If it is a flowchart, explain the process. If it is an architecture diagram, list the services involved."
    
    try:
        if MODEL_PROVIDER == "OLLAMA":
            print(f"Generating caption for {image_path} using Ollama ({OLLAMA_VISION_MODEL})...")
            response = ollama.generate(
                model=OLLAMA_VISION_MODEL,
                prompt=prompt,
                images=[image_path]
            )
            return response['response']
        
        elif MODEL_PROVIDER == "GEMINI":
            print(f"Generating caption for {image_path} using Gemini...")
            model = genai.GenerativeModel(GEMINI_MODEL)
            img = Image.open(image_path)
            response = model.generate_content([prompt, img])
            return response.text
            
    except Exception as e:
        print(f"Error generating caption for {image_path}: {e}")
        return f"Error: Could not generate caption. ({str(e)})"

if __name__ == "__main__":
    # Quick test
    test_image = "extracted_images/page_1_img_1.png"
    if os.path.exists(test_image):
        caption = generate_caption(test_image)
        print("\n--- CAPTION ---")
        print(caption)
    else:
        print(f"Test image {test_image} not found. Run extract_images_from_pdf first.")
