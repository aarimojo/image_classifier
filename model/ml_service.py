import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image
from loguru import logger

import os

# logger.add("ml_service.log", level="DEBUG")

os.environ['KERAS_HOME'] = '/root/.keras'

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
def get_redis_connection(max_retries=5, retry_delay=5):
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1} of {max_retries} to connect to Redis")
            return redis.Redis(
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB_ID,
                host=settings.REDIS_IP,
            )
        except redis.ConnectionError:
            logger.error("Failed to connect to Redis")
            if attempt == max_retries - 1:
                logger.critical("Failed to connect to Redis after multiple attempts")
                raise
            logger.info(f"Retrying in {retry_delay} seconds")
            time.sleep(retry_delay)
            continue

db = get_redis_connection()
logger.info("Connected to Redis")

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(weights="imagenet")
logger.info("Model loaded")

def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    logger.info(f"Predicting image: {image_name}")
    try:    
        image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
        logger.debug(f"Absolute image path: {os.path.abspath(image_path)}")
        
        if not os.path.exists(image_path):
            logger.error(f"Image not found at {image_path}")
            logger.debug(f"Contents of upload directory: {os.listdir(settings.UPLOAD_FOLDER)}")
            return None, None
        # TODO: Implement the code to predict the class of the image_name

        try:
            prediction = db.get(image_name)
            if prediction:
                logger.info("Prediction found in Redis, returning results...")
                prediction = json.loads(prediction)
                return prediction["class"], prediction["score"]
        except:
            logger.info("Prediction not found in Redis, loading from disk...")
        # Load image
        image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
        logger.info(f"Loading image from path: {image_path}")
        img = image.load_img(image_path, target_size=(224, 224))
        logger.info("Image loaded, applying preprocessing...")
        # Apply preprocessing (convert to numpy array, match model input dimensions (including batch) and use the resnet50 preprocessing)
        img_array = image.img_to_array(img)
        logger.info("Image converted to numpy array, expanding dimensions...")
        img_array = np.expand_dims(img_array, axis=0)
        logger.info("Dimensions expanded, preprocessing...")
        img_array = preprocess_input(img_array)

        # Get predictions using model methods and decode predictions using resnet50 decode_predictions
        predictions = model.predict(img_array)
        logger.info("Predictions made, decoding predictions...")
        logger.info(f"Top 5 predictions: {decode_predictions(predictions, top=5)}")
        _, class_name, pred_probability = decode_predictions(predictions, top=1)[0][0]
        logger.info(f"Predictions decoded, class name: {class_name}, probability: {pred_probability}")

        # Convert probabilities to float and round it
        logger.info("Predictions decoded, converting probabilities to float...")
        pred_probability = round(float(pred_probability), 4)
        logger.info("Probabilities converted to float, returning results...")
        try:
            # store the prediction in Redis in a separate queue that will be used to speed up retrieval in case of a repeated file
            db.set(image_name, json.dumps({"class": class_name, "score": pred_probability}))
        except Exception as e:
            logger.error(f"Error storing prediction in Redis: {e}")
            
        return class_name, pred_probability
    except Exception as e:
        logger.error(f"Error predicting image: {e}")
        return None, None


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    logger.info("Starting classify process...")
    while True:
        try:
            logger.info("Waiting for a new job from Redis...")
            logger.debug(f"Current contents of upload directory: {os.listdir(settings.UPLOAD_FOLDER)}")
            
            job = db.brpop(settings.REDIS_QUEUE)
            logger.debug(f"Raw job data received: {job}")
            
            if not job:
                logger.warning("No job received from Redis")
                time.sleep(settings.SERVER_SLEEP)
                continue
                
            job_data = json.loads(job[1])
            logger.debug(f"Parsed job data: {job_data}")
            
            job_id = job_data[0]
            image_name = job_data[1]
            logger.info(f"Processing job {job_id} for image {image_name}")
            
            # Run the loaded ml model (use the predict() function)
            class_name, pred_probability = predict(image_name)
            logger.info(f"Prediction made: {class_name}, {pred_probability}")
            # Prepare a new JSON with the results
            output = {"prediction": class_name, "score": pred_probability}

            # Store the job results on Redis using the original
            # job ID as the key
            db.set(job_id, json.dumps(output))
            logger.info(f"Results stored in Redis with job ID: {job_id}")
            # Sleep for a bit
            time.sleep(settings.SERVER_SLEEP)
            logger.info(f"Sleeping for {settings.SERVER_SLEEP} seconds")
        except Exception as e:
            logger.exception(f"Error in classify process: {e}")
            time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    logger.info("Launching ML service...")
    classify_process()
