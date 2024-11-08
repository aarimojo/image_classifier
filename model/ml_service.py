import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

import os

os.environ['KERAS_HOME'] = '/root/.keras'

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
# db = redis.Redis(
#     port=settings.REDIS_PORT,
#     db=settings.REDIS_DB_ID,
#     host=settings.REDIS_IP,
# )
db = None

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(weights="imagenet")


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
    print(f"Predicting image: {image_name}")
    try:    
        class_name = None
        pred_probability = None
        # TODO: Implement the code to predict the class of the image_name

        # Load image
        image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)
        print(f"Loading image from path: {image_path}")
        img = image.load_img(image_path, target_size=(224, 224))
        print("Image loaded, applying preprocessing...")
        # Apply preprocessing (convert to numpy array, match model input dimensions (including batch) and use the resnet50 preprocessing)
        img_array = image.img_to_array(img)
        print("Image converted to numpy array, expanding dimensions...")
        img_array = np.expand_dims(img_array, axis=0)
        print("Dimensions expanded, preprocessing...")
        img_array = preprocess_input(img_array)

        # Get predictions using model methods and decode predictions using resnet50 decode_predictions
        predictions = model.predict(img_array)
        print("Predictions made, decoding predictions...")
        print(f"Top 5 predictions: {decode_predictions(predictions, top=5)}")
        _, class_name, pred_probability = decode_predictions(predictions, top=1)[0][0]
        print(f"Predictions decoded, class name: {class_name}, probability: {pred_probability}")

        
        # Convert probabilities to float and round it
        print("Predictions decoded, converting probabilities to float...")
        pred_probability = round(float(pred_probability), 4)
        print("Probabilities converted to float, returning results...")
        return class_name, pred_probability
    except Exception as e:
        print(f"Error predicting image: {e}")
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
    print("Starting classify process...")
    while True:
        pass
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO
        # Take a new job from Redis
        
        
        # job = db.brpop(settings.REDIS_QUEUE)
        # # Decode the JSON data for the given job
        # job_data = json.loads(job[1])
        # # Important! Get and keep the original job ID
        # job_id = job_data[0]
        # image_name = job_data[1]
        # # Run the loaded ml model (use the predict() function)
        # class_name, pred_probability = predict(image_name)
        # # Prepare a new JSON with the results
        # output = {"prediction": class_name, "score": pred_probability}

        # # Store the job results on Redis using the original
        # # job ID as the key
        # db.set(job_id, json.dumps(output))
        # # Sleep for a bit
        # time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
