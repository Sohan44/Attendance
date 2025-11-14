import os, cv2
import numpy as np
from PIL import Image

def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message, text_to_speech):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(haarcasecade_path)
    faces, Ids = getImagesAndLabels(trainimage_path)
    recognizer.train(faces, np.array(Ids))
    recognizer.save(trainimagelabel_path)
    res = "Image trained successfully"
    message.configure(text=res)
    text_to_speech(res)

def getImagesAndLabels(path):
    imagePaths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                imagePaths.append(os.path.join(root, file))

    faces = []
    Ids = []
    for imagePath in imagePaths:
        img = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        try:
            Id = int(os.path.split(imagePath)[-1].split("_")[1])
            faces.append(img)
            Ids.append(Id)
        except Exception as e:
            print(f"Skipping {imagePath}: {e}")
    return faces, Ids
