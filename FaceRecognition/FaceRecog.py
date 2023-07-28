import cv2


class FaceDetector(object):
    def __init__(self, model_path="../resources/models/face_detection_yunet_2022mar.onnx", score_threshold=0.9,
                 nms_threshold=0.3, top_k=5000):
        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold
        self.top_k = top_k
        ## [initialize_FaceDetectorYN]
        self.detector = cv2.FaceDetectorYN.create(
            model_path,
            "",
            (640, 640),
            score_threshold,
            nms_threshold,
            top_k,
        )
        ## [initialize_FaceDetectorYN]

    """
        根据输入图像，检测出人脸，返回一个人脸框tuple，不会对人脸进行crop
    """
    def detectFacesFromImg(self, img):
        img_size = img.shape
        self.detector.setInputSize([img_size[1], img_size[0]])
        faces = self.detector.detect(img)
        return faces

    """
        根据输入视频的一帧，检测出人脸，返回一个人脸框tuple，不会对人脸进行crop
    """
    def detectFacesFromVideoes(self, frame, frameWidth, frameHeight):
        self.detector.setInputSize([frameWidth, frameHeight])
        faces = self.detector.detect(frame)  # faces is a tuple
        return faces


class FaceRecognizer(object):
    def __init__(self, model_path="../resources/models/face_recognition_sface_2021dec.onnx"):
        ## [initialize_FaceRecognizerSF]
        self.recognizer = cv2.FaceRecognizerSF.create(model_path, "")
        ## [initialize_FaceRecognizerSF]

    """
        根据detector从图像中检查出来的faces，来生成相应的features，是个features的list.
        由于输入faces只是标注了每个人脸在原始图像的框，所以还需要原始图像来作为输入参数
    """
    def generateFeaturesFromImg(self, img, faces):
        face_features = []
        for idx, face in enumerate(faces[1]):
            face_feature = self.generateFeatureFromImg(img, face)
            face_features.append(face_feature)
        return face_features

    """
        输入是一个face（人脸框），输出对应的face feature
    """
    def generateFeatureFromImg(self, img, face):
        face_align = self.recognizer.alignCrop(img, face)
        face_feature = self.recognizer.feature(face_align)
        return face_feature

    """
        根据两个输入feature比较是否是相同人脸
    """
    def isSameFace(self, feature1, feature2):
        cosine_score = self.recognizer.match(
            feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE
        )
        l2_score = self.recognizer.match(
            feature1, feature2, cv2.FaceRecognizerSF_FR_NORM_L2
        )
        print("cosine_score={},l2_score={}".format(cosine_score, l2_score))
        #return cosine_score >= 0.83
        #return (cosine_score >= 0.83) or (l2_score <= 0.320)
        return (cosine_score >= 0.363) or (l2_score <= 1.128)
