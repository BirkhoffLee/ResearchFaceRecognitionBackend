from flask import Flask, request
import cv2
import base64
import numpy as np
from VectorDatabase import ChromaDB
import FaceRecognition
import BlockChain
import hashlib
import time

from flask_cors import CORS, cross_origin



app = Flask(__name__)

###BloackChain Property###
infura_url = "https://sepolia.infura.io/v3/71199b1f00e74f1194a09255d9ce0d44"
# https://sepolia.etherscan.io/address/0x68a53755ab9155713b9c77a2fa8c8c6cbb8a1c07#readContract
abi = [{"inputs":[{"internalType":"string","name":"nationalID","type":"string"}],"name":"destroyIdentityByNationalID","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"nationalID","type":"string"}],"name":"getAllDataByNationalID","outputs":[{"components":[{"internalType":"string","name":"nationalID","type":"string"},{"internalType":"string","name":"name","type":"string"},{"internalType":"bool","name":"isRestrictedPersonnel","type":"bool"},{"internalType":"enum Identity.Gender","name":"gender","type":"uint8"},{"internalType":"string","name":"facialHash","type":"string"},{"internalType":"string","name":"facialFeatures","type":"string"}],"internalType":"struct Identity.IdentityInfo","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getAllFacialFeaturesAndNationalID","outputs":[{"components":[{"internalType":"string","name":"nationalID","type":"string"},{"internalType":"string","name":"facialFeatures","type":"string"}],"internalType":"struct Identity.FacialEntry[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"facialHash","type":"string"}],"name":"getCandidatesFromFacialHash","outputs":[{"components":[{"internalType":"string","name":"nationalID","type":"string"},{"internalType":"string","name":"facialFeatures","type":"string"}],"internalType":"struct Identity.FacialEntry[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"nationalID","type":"string"}],"name":"getFacialFeaturesByNationalID","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"nationalID","type":"string"}],"name":"getGenderByNationalID","outputs":[{"internalType":"enum Identity.Gender","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"nationalID","type":"string"}],"name":"getNameByNationalID","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"nationalID","type":"string"}],"name":"getRestrictionStatusByNationalID","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"nationalID","type":"string"},{"internalType":"string","name":"name","type":"string"},{"internalType":"bool","name":"isRestrictedPersonnel","type":"bool"},{"internalType":"enum Identity.Gender","name":"gender","type":"uint8"},{"internalType":"string","name":"facialFeatures","type":"string"},{"internalType":"string","name":"facialHash","type":"string"}],"name":"newIdentity","outputs":[],"stateMutability":"nonpayable","type":"function"}]
address = "0x8fF2DF99c6Cc7255e6A13f0B8E323BfE6bD90e26"
###BloackChain Property###

db = ChromaDB("./resources/ChromaDB")
detector = FaceRecognition.FaceDetector(model_path="./resources/models/face_detection_yunet_2022mar.onnx", score_threshold=0.9,
                 nms_threshold=0.3, top_k=5000)
recognizer = FaceRecognition.FaceRecognizer(model_path="./resources/models/face_recognition_sface_2021dec.onnx")
ep = BlockChain.EthereumProxy(infura_url=infura_url, abi=abi, address=address)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/identify', methods=['POST'])
@cross_origin(supports_credentials=True)
def identifyFace():

    # 获取传送过来的完整原始图像
    file = request.json.get('image')
    # 图片名称
    # imgName = file.filename
    image_data = base64.b64decode(file.split(',')[1])
    np_array = np.frombuffer(image_data, dtype=np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # 从二进制图片数据中读
    json_str = identifyFaceFromImage(img)
    if json_str is not None:
        return json_str
    else:
        return "{\"success\":false}"

@app.route('/identity/<national_hash>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def deleteIdentity(national_hash):
    ids = [national_hash] #这个需要是list
    if db.getEmbeddingById(ids) is None:
        return "{\"success\":false, \"msg\":\"No such identity with giving national_hash\"}"
    else:
        db.deleteDataByIds(ids)
        # 区块链删除
        #为了让这部分代码不会在中心化的服务器修改，这里在区块链实现
        # 区块链删除
        if db.getEmbeddingById(national_hash) is None:
             return "{\"success\":true}"
        else:
            return "{\"success\":false, \"msg\":\"Deleting failure\"}"

@app.route("/identity/new", methods=["POST"])
@cross_origin(supports_credentials=True)
def insertIdentity():
    if request.content_type.startswith('application/json'):
         # 获取传送过来的完整原始图像
         file = request.json.get('image')
         image_data = base64.b64decode(file.split(',')[1])
         np_array = np.frombuffer(image_data, dtype=np.uint8)
         img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # 从二进制图片数据中读
         face_feature = get_face_feature_from_pics(img)
         face_feature_list = [face_feature[0].tolist()]
         #生成national_hash,sha25查出chromadb的存储字节长度，需要截取一下
         national_hash = generateHash256FromString(str(time.time()))[:30]
         db.insert(embeddings=face_feature_list, metadatas=[{"national_hash": national_hash}], ids=national_hash)
         return "{\"success\":true, \"national_hash\":\"" + national_hash + "\"}"

    # elif request.content_type.startswith('multipart/form-data'):
    #      nationalID = request.form.get('national_id')
    #      if db.getEmbeddingById(nationalID) is not None:
    #          return "{\"success\":false, \"msg\",\"NationalId already exists\"}"
    #      else:
    #          # 获取传送过来的完整原始图像
    #          file = request.files.get('img')
    #          img_byte = file.read()
    #          img_byte = bytearray(img_byte)
    #          img = cv2.imdecode(np.array(img_byte, dtype='uint8'), cv2.IMREAD_UNCHANGED)  # 从二进制图片数据中读
    #          face_feature = get_face_feature_from_pics(img)
    #          face_feature_list = [face_feature[0].tolist()]
    #          # 生成national_hash
    #          national_hash = generateHash256FromString(nationalID + str(time.time()))
    #          db.insert(embeddings=face_feature_list, metadatas=[{"national_hash": national_hash}], ids=national_hash)
    #          return "{\"success\":true, \"national_hash\":" + national_hash + "}"
    else:
        return "{\"success\":false, \"msg\":\"Format is not supported!\"}"


#从img中读取到人脸信息
def identifyFaceFromImage(img):
    faces = detector.detectFacesFromImg(img)
    if faces[1] is not None:
        #检测出不至于一个人脸，只取第0个人人脸识别
        for face_index ,face in enumerate(faces[1]):
            if face_index > 0:
                break
            start = time.time_ns()
            face_feature = recognizer.generateFeatureFromImg(img, face)
            end = time.time_ns()
            print("模型处理时间{}".format(end - start))
            face_embeddings_list = [face_feature[0].tolist()]
            # 查找最接近的5个人脸数据，欧拉距离最短
            start = time.time_ns()
            result_dic = db.search(face_embeddings_list, 5)
            end = time.time_ns()
            print("搜寻时间{}".format(end - start))
            embeddings = result_dic["embeddings"]
            for index, id in enumerate(result_dic["ids"][0]):
                stored_face_feature = embeddings[0][index]
                #chromadb存储的是list类型，需要转换成numpy array
                stored_face_feature = np.array([stored_face_feature]).astype(np.float32)
                if recognizer.isSameFace(face_feature, stored_face_feature):
                    # 去区块链里面查找这个人,返回一个set
                    #userinfo = ep.getCivilianInfoByNationalId(id)
                    #json_userinfo = transferUserinfoToJSONString(userinfo)
                    json_userinfo = "{\"success\":true, \"national_hash\":\"" + id +"\"}"
                    return json_userinfo
    return None

#传入一个userinfo的set对象，转换成JSONString
def transferUserinfoToJSONString(userinfo):
    json_str = ""
    json_str += "{\"nationalID\":" + userinfo[0] + ",\"name\":" + userinfo[1] + ",\"millitaryClearance\":" + str(userinfo[2]) + ",\"gender\":" + str(userinfo[3]) + "}"
    return json_str

def get_face_feature_from_pics(img):
    faces = detector.detectFacesFromImg(img)
    # Draw results on the input image
    if faces[1] is not None:
        for face_index, face in enumerate(faces[1]):
            face_feature = recognizer.generateFeatureFromImg(img, face)
            return face_feature
    return None

'''
    输入一个字符串，根据sha256生成一个16进制数，字符串相同那么生成的数也相同
'''
def generateHash256FromString(string):
    sha256_obj = hashlib.sha256()
    sha256_obj.update(string.encode("utf-8"))
    return sha256_obj.hexdigest()


if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0', port=8080)
