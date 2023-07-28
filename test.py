#-*- coding:utf-8 -*-
import FaceRecognition
from VectorDatabase import ChromaDB
import os
import numpy as np
import cv2

db = ChromaDB("./resources/ChromaDB")
detector = FaceRecognition.FaceDetector(model_path="./resources/models/face_detection_yunet_2022mar.onnx",
                                            score_threshold=0.9,
                                            nms_threshold=0.3, top_k=5000)
recognizer = FaceRecognition.FaceRecognizer(model_path="./resources/models/face_recognition_sface_2021dec.onnx")

def test1():
    db = ChromaDB("./resources/ChromaDB")
    db.insert(embeddings = [[1,2,3,4], [2,3,5,2], [3,4,5,6]], metadatas = [{"name": "第000人"},{"name": "第001人"},{"name": "第002人"}], ids = ["000","001","002"])

    #results = db.search(query_embeddings=[2,3,4,2], num=4)
    #print(db.getEmbeddingById(results["ids"][0][0]))
    #print(db.collection.get(ids=results["ids"][0][0],include=["embeddings"]))
    print(db.getEmbeddingById("001"))
    results = db.deleteDataByIds("001")
    print(results)
    print(db.getEmbeddingById("001"))
    db.clearDatabase()

def test2():
    db = ChromaDB("./resources/ChromaDB")
    db.clearDatabase()

def get_face_feature_from_pics(imgpath):
    img = cv2.imread(imgpath)
    faces = detector.detectFacesFromImg(img)
    # Draw results on the input image
    if faces[1] is not None:
        for idx, face in enumerate(faces[1]):
            face_feature = recognizer.generateFeatureFromImg(img, face)
            return face_feature

def test3():
    path = "D:/BaiduNetdiskDownload/64_CASIA-FaceV5"
    # folders = ["CASIA-FaceV5 (000-099)/", "CASIA-FaceV5 (100-199)/", "CASIA-FaceV5 (200-299)/", "CASIA-FaceV5 (300-399)/", "CASIA-FaceV5 (400-499)/"]
    folders = ["CASIA-FaceV5 (100-199)/"]
    nationalID = 40004000

    for folder in folders:
        folder_path = os.path.join(path, folder)
        for imgs_folder in os.listdir(folder_path):
            imgs_path = os.path.join(folder_path, imgs_folder)
            imgs_path += "/"
            # 对每个人的5张照片就行评估，这些照片属于一个人，理论上来说应该分到一个类
            face_features = np.empty((5, 128))
            img_names = os.listdir(imgs_path)  # list
            for i in range(len(img_names)):
                img_name = img_names[i]
                img_path = os.path.join(imgs_path, img_name)
                face_feature = get_face_feature_from_pics(img_path)
                face_features[i, :] = face_feature
            face_feature_list = face_features[0].tolist()
            db.insert(embeddings=face_feature_list, metadatas=[{"nationalID": str(nationalID)}], ids=str(nationalID))
            nationalID += 1

if __name__ == '__main__':
    test3()