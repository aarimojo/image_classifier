import os
from typing import List

from app import db
from app import settings as config
from app import utils
from app.auth.jwt import get_current_user
from app.model.schema import PredictRequest, PredictResponse
from app.model.services import model_predict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from loguru import logger

router = APIRouter(tags=["Model"], prefix="/model")


@router.post("/predict")
async def predict(file: UploadFile, current_user=Depends(get_current_user)):
    logger.info(f"Predicting image: {file.filename}")
    rpse = {"success": False, "prediction": None, "score": None}
    # To correctly implement this endpoint you should:
    #   1. Check a file was sent and that file is an image, see `allowed_file()` from `utils.py`.
    #   2. Store the image to disk, calculate hash (see `get_file_hash()` from `utils.py`) before
    #      to avoid re-writing an image already uploaded.
    #   3. Send the file to be processed by the `model` service, see `model_predict()` from `services.py`.
    #   4. Update and return `rpse` dict with the corresponding values
    # If user sends an invalid request (e.g. no file provided) this endpoint
    # should return `rpse` dict with default values HTTP 400 Bad Request code
    # TODO
    rpse["success"] = None
    rpse["prediction"] = None
    rpse["score"] = None
    rpse["image_file_name"] = None

    try:
        if not utils.allowed_file(file.filename):
            logger.error(f"File type is not supported: {file.filename}")
            raise HTTPException(status_code=400, detail="File type is not supported.")
        
        file_hash = await utils.get_file_hash(file)
        logger.debug(f"File hash: {file_hash}")
        
        await file.seek(0)
        file_path = os.path.join(config.UPLOAD_FOLDER, file_hash)
        logger.debug(f"Saving file to: {file_path}")
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        logger.info("File saved, sending to model service")
        prediction, score = await model_predict(file_hash)
        logger.info(f"Got prediction: {prediction}, score: {score}")
        
        rpse["prediction"] = prediction
        rpse["score"] = score
        rpse["image_file_name"] = file_hash
        rpse["success"] = True
        
        return PredictResponse(**rpse)
        
    except Exception as e:
        logger.exception(f"Error in predict endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
