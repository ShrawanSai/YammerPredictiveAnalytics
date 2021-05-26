import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import requests
import io
def set_model_for_image_type():
    
    np.set_printoptions(suppress=True)

    # Load the model
    model = tensorflow.keras.models.load_model('keras_model.h5')
    return model

def get_image_type(model,url):
    
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    try:
            
        try:
            image = Image.open(requests.get(url, stream=True).raw)
        except:
            #print(url)
            r = requests.get(url, stream=True)
            x = r.content
            image = Image.open(io.BytesIO(x))

        #resize the image to a 224x224 with the same strategy as in TM2:
        #resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)

        #turn the image into a numpy array
        image_array = np.asarray(image)


        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # run the inference
        prediction = model.predict(data)
        #print(prediction)
        if prediction[0][0]>prediction[0][1]:
            return 1
        else:
            return -1
    except Exception as e:
        #print('fail')
        return 0