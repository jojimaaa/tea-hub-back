import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from fastapi import UploadFile, File

# Configuration       
cloudinary.config( 
    cloud_name = "dattmfduh", 
    api_key = "129198181975447", 
    api_secret = "T7GOJpMeu-lXuYTTc-V3Wl5Y48Y", # Click 'View API Keys' above to copy your API secret
    secure=True
)

async def upload_image_to_cloudinary(file: UploadFile = File(...)):
    
    # lê o conteúdo do arquivo (bytes)
    conteudo = await file.read()

    # faz o upload dos bytes
    result = cloudinary.uploader.upload(
        conteudo,
        resource_type="auto"
    )

    return result["secure_url"]

# # Optimize delivery by resizing and applying auto-format and auto-quality
# optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
# print(optimize_url)

# # Transform the image: auto-crop to square aspect_ratio
# auto_crop_url, _ = cloudinary_url("shoes", width=500, height=500, crop="auto", gravity="auto")
# print(auto_crop_url)