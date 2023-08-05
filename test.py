#-*- coding:utf-8 -*-
import FaceRecognition
from VectorDatabase import ChromaDB
import os
import numpy as np
import cv2
import hashlib

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

#向数据库里面添加数据
def test3():
    path = "E:/face_dataset/wiki_crop/"
    nationalID = 40005000

    for imgs_folder in os.listdir(path):
        imgs_path = os.path.join(path, imgs_folder)
        imgs_path += "/"
        img_names = os.listdir(imgs_path)  # list
        face_feature_list = []
        national_hash_lsit = []
        metadata_list = []
        for i in range(len(img_names)):
            img_name = img_names[i]
            img_path = os.path.join(imgs_path, img_name)
            #print(img_path)
            try:
                face_feature = get_face_feature_from_pics(img_path)
                face_feature_list.append(face_feature.tolist()[0])
                nationalID += 1
                national_hash = generateHash256FromString(str(nationalID))[:30]
                national_hash_lsit.append(national_hash)
                metadata_list.append({"national_hash": national_hash})
                if len(face_feature_list) == 400:
                    print("持久化{}的数据到数据库中...".format(imgs_folder))
                    db.insert(embeddings=face_feature_list, metadatas=metadata_list, ids=national_hash_lsit)
                    print("持久化成功！")
                    face_feature_list.clear()
                    national_hash_lsit.clear()
                    metadata_list.clear()
                #print("nationalID为{}的数据处理成功".format(nationalID))
            except (Exception, BaseException) as e:
                print(e)



import time
def test4():
    now_time = time.time()
    str1 = str(now_time) + "123,42"
    print(str1)
    print(generateHash256FromString(str1))
    time.sleep(1)
    now_time = time.time()
    str2 = str(now_time) + "123,42"
    print(str2)
    print(generateHash256FromString(str2))

#把该文件夹下每个人的第一个人脸数据添加到数据库中
def test5():
    path = "D:/BaiduNetdiskDownload/64_CASIA-FaceV5/CASIA-FaceV5 (000-099)/"
    nationalID = 50000000

    for imgs_folder in os.listdir(path):
        imgs_path = os.path.join(path, imgs_folder)
        imgs_path += "/"
        img_names = os.listdir(imgs_path)  # list
        face_feature_list = []
        national_hash_lsit = []
        metadata_list = []
        for i in range(len(img_names)):
            img_name = img_names[i]
            img_path = os.path.join(imgs_path, img_name)
            # print(img_path)
            try:
                face_feature = get_face_feature_from_pics(img_path)
                face_feature_list.append(face_feature.tolist()[0])
                nationalID += 1
                national_hash = generateHash256FromString(str(nationalID))[:30]
                national_hash_lsit.append(national_hash)
                metadata_list.append({"national_hash": national_hash})
            except (Exception, BaseException) as e:
                print(e)
        try:
            print("{}人的人脸持久化的数据库中".format(imgs_folder))
            db.insert(embeddings=face_feature_list[0:1], metadatas=metadata_list[0:1], ids=national_hash_lsit[0:1])
            print("持久化成功！")
        except:
            print("{}人的人脸持久化失败".format(imgs_folder))
        face_feature_list.clear()
        national_hash_lsit.clear()
        metadata_list.clear()

#测试accuracy
def test6():
    path = "D:/BaiduNetdiskDownload/64_CASIA-FaceV5/CASIA-FaceV5 (000-099)/"
    success = 0
    error = 0

    for imgs_folder in os.listdir(path):
        imgs_path = os.path.join(path, imgs_folder)
        imgs_path += "/"
        img_names = os.listdir(imgs_path)  # list

        for i in range(len(img_names)):
            if i == 0:
                continue
            img_name = img_names[i]
            img_path = os.path.join(imgs_path, img_name)
            # print(img_path)
            try:
                face_feature = get_face_feature_from_pics(img_path)
                face_embeddings_list = [face_feature[0].tolist()]
                # 查找最接近的5个人脸数据，欧拉距离最短
                result_dic = db.search(face_embeddings_list, 5)
                embeddings = result_dic["embeddings"]
                #flag标记有没有识别成功
                flag = 0
                for index, id in enumerate(result_dic["ids"][0]):
                    stored_face_feature = embeddings[0][index]
                    # chromadb存储的是list类型，需要转换成numpy array
                    stored_face_feature = np.array([stored_face_feature]).astype(np.float32)
                    if recognizer.isSameFace(face_feature, stored_face_feature):
                        success += 1
                        flag = 1
                        break
                if flag == 0:
                    print("第{}人，第{}张照片识别失败".format(imgs_folder, i+1))
                    error += 1
            except (Exception, BaseException) as e:
                print(e)
    print("识别成功数{},识别失败数{},测试准确率为{}".format(success, error, float(success)/float(success+error)))

#将向量存储为np.array
def test7():
    path = "E:/face_dataset/wiki_crop/"
    nationalID = 40000000

    for imgs_folder in os.listdir(path):
        imgs_path = os.path.join(path, imgs_folder)
        imgs_path += "/"
        img_names = os.listdir(imgs_path)  # list
        for i in range(len(img_names)):
            img_name = img_names[i]
            img_path = os.path.join(imgs_path, img_name)
            #print(img_path)
            try:
                face_feature = get_face_feature_from_pics(img_path)
                nationalID += 1
                #national_hash = generateHash256FromString(str(nationalID))[:30]
                np.save(f"./resources/features/{nationalID}", face_feature)
                #print("nationalID为{}的数据处理成功".format(nationalID))
            except (Exception, BaseException) as e:
                print(e)


def generateHash256FromString(string):
    sha256_obj = hashlib.sha256()
    sha256_obj.update(string.encode("utf-8"))
    return sha256_obj.hexdigest()

if __name__ == '__main__':
    test7()
    #import numpy as np
    #a = db.collection.query(query_embeddings=np.zeros((1,128)).tolist(), n_results=2)
    #print(a)
    #db.clearDatabase()
