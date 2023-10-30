from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from bson import ObjectId
from io import BytesIO
from PIL import Image

app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing) to allow requests from any source
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Images']
collection = db['Images']

class ImageUploadResponse(BaseModel):
    id: str

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        img_data = await file.read()
        img_format = file.content_type.split('/')[-1]

        # Store image data as a binary blob in MongoDB
        image_record = {
            'data': img_data,
            'format': img_format
        }
        result = collection.insert_one(image_record)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/retrieve/{image_id}")
async def retrieve_image(image_id: str):
    try:
        image_record = collection.find_one({'_id': ObjectId(image_id)})
        if image_record:
            img_data = image_record['data']
            img_format = image_record['format']

            # Create an image from the binary data
            img_blob = BytesIO(img_data)
            img = Image.open(img_blob)

            # Save the image temporarily and return the file path
            temp_path = f"temp_image.{img_format}"
            img.save(temp_path)

            return FileResponse(temp_path, media_type=f'image/{img_format}')
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
