# FastAPI Project Demo

###### 声明：此仓库仅做为 FastAPI 入门级参考, 开箱即用, 所有接口采用 restful 风格

## 技术栈

- fastapi
- tortoise-orm
- aerich
- mysql
- redis
- docker
- ......

## 下载

### 1. 克隆仓库

 ```shell
 git clone https://gitee.com/wu_cl/fastapi_tortoise_mysql.git
 ```

### 2. 使用 CLI（推荐）

pip 安装:

```shell
pip install fastapi-ccli
```

跳转查看使用说明:

- [PyPI](https://pypi.org/project/fastapi-ccli)
- [Gitee](https://gitee.com/wu_cl/fastapi_ccli)
- [GitHub](https://github.com/wu-clan/fastapi_ccli)

## 安装使用

> ⚠️: 此过程请格外注意端口占用情况, 特别是 8000, 3306, 6379...

### 1: 传统

1. 安装依赖
    ```shell
    pip install -r requirements.txt
    ```

2. 创建数据库 ftm, 选择 utf8mb4 编码
3. 查看 backend/app/core/conf.py 配置文件, 检查并修改数据库配置信息
4. 执行数据库迁移
    ```shell
    cd backend/app/aerich
    
    # demo中可省略两步
    # aerich init -t env.TORTOISE_ORM  
   
    aerich init-db

    aerich upgrade
    
    # 当更新数据库 model 后，执行下面两个命令进行迁移
    aerich migrate
    
    aerich upgrade
    ```

5. 安装启动 redis
6. 查看 backend/app/core/conf.py 配置文件, 检查并修改 redis 配置信息
7. 执行 backend/app/main.py 文件启动服务
8. 浏览器访问: http://127.0.0.1:8000/v1/docs

---

### 2: docker

1. 在 docker-compose.yml 文件所在目录下执行一键启动命令

    ```shell
    docker-compose up -d --build
    ```
2. 等待命令自动执行完成

3. 浏览器访问: http://127.0.0.1:8000/v1/docs

## 初始化测试数据

执行 backend/app/init_test_data.py 文件
