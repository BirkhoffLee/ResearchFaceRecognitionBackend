#基础镜像使用pyhton:3.10
FROM python:3.10
# 作者
MAINTAINER cyt
#将你的项目文件放到docker容器中的/BlockChainBasedSecuritySystem文件夹，这里/BlockChainBasedSecuritySystem是在根目录的，与/root /opt等在一个目录
ADD ./BlockChainBasedSecuritySystem /BlockChainBasedSecuritySystem
# 设置工作目录，也就是下面执行 ENTRYPOINT 后面命令的路径
WORKDIR /BlockChainBasedSecuritySystem
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 libgl1 -y
# VOLUME 指定临时文件目录为/tmp，在主机/var/lib/docker/volumes/{容器id}目录下创建了一个临时文件并链接到容器的/tmp，VOLUME不能申明主机卷的位# 置，只能油系统自动生成，如果用-v挂在了，那么VOLUME则失效。目的是某些动态数据，用户忘记指定其挂载点时，自动分配一个，防止容器内存占用过大 # 以及删除容器导致数据丢失
VOLUME /BlockChainBasedSecuritySystem/resources
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]

