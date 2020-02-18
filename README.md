# 安装步骤 
## 1. 安装redis
## 2. 安装mongodb
## 3. 安装elasticsearch
### 3.1 下载 curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.5.1-linux-x86_64.tar.gz 我用的7.5.1
### 3.2 解压 tar 命令解压
### 3.3 安装验证 (1) cd /elasticsearch/bin  (2)./elasticsearch  登录http://localhost:9200/
### 3.4 安装中文分词器 在 /elasticsearch/bin目录里  ./elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.5.1/elasticsearch-analysis-ik-7.5.1.zip
### 3.5 重启elasticsearch 安装python 接口 pip install elasticsearch
## 4. python maneger runserver
## 5. 创建admin时： email 变成 mobile_number
## Describe
### 1. redis现在主要生成验证码， 还没有加入缓存功能和celery任务队列
