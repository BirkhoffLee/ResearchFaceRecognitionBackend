# ResearchFaceRecognitionBackend

This is the Python backend POC of unpublished paper "Decentralized Face Identification with Hierarchical Navigable Small World on Blockchain" by Hsiang-Hung Lee and Yi-ting Chen.

## Usage
Upload all the files  to a machine that has installed docker  
All the files are supposed to be moved under the folder named "BlockChainBasedSecuritySystem"  
Copy the "Dockerfile" to upper folder and the folder layer is like below:  
```
--  BlockChainBasedSecuritySystem  
   -- BlockChain  
   -- FaceRecognition  
   -- VectorDatabase  
   -- resources  
   -- Dockerfile  
   -- LICENSE  
   -- README.md  
   -- app.py  
   -- requirements.txt  
   -- test.py  
-- Dockerfile
```
In the upper folder, run the command "docker build -t BlockChainBasedSecuritySystem:latest ." to build the image  
Lasly, run the docker container with the command "docker run -d -n BlockChainBasedSecuritySystem -p 5000:5000 BlockChainBasedSecuritySystem:latest" and the backend service is running and exposes 5000 port.  

## Related Works

* https://github.com/BirkhoffLee/ResearchCustomsInspectionContract
* https://github.com/BirkhoffLee/ResearchCustomsInspectionDApp

## License

This work is licensed under [Apache License 2.0](LICENSE).
