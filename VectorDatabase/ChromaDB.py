import chromadb

class ChromaDB(object):
    def __init__(self, path):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="face_embeddings")
        #self.collection = self.client.create_collection(name="face_embeddings1")
    """
        embeddings为d维向量组成的list，metadatas也是list，每个元素都是一个json格式
    """
    def insert(self, embeddings, metadatas, ids):
        self.collection.add(embeddings=embeddings, metadatas=metadatas, ids=ids)
        return True

    """
        embedding维要查询的向量， num是查询top num个最接近的向量,不加include，chromadb由于性能原因不会显示embedding信息
    """
    def search(self, query_embeddings, num):
        return self.collection.query(query_embeddings=query_embeddings, n_results=num, include=["embeddings"])

    def getEmbeddingById(self, id):
        first_search = self.collection.get(ids=id)
        if len(first_search["ids"]) > 0:
            second_search = self.collection.get(ids=id, include=["embeddings"])
            return second_search
        else:
            return None

    #输入List<String>类型
    def deleteDataByIds(self, ids):
        self.collection.delete(ids=ids)

    def clearDatabase(self):
        self.client.delete_collection(name="face_embeddings")