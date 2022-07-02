# FastAPI Project Demo

###### 声明：此仓库仅做为 FastAPI 入门级参考

📢 开箱即用, 所有接口采用 restful 风格

## 技术栈

- fastapi
- tortoise-orm
- aerich
- mysql
- redis
- docker
- ......

## 下载

1. 克隆

    ```shell
    git clone https://gitee.com/wu_cl/fastapi_tortoise_mysql.git
    ```

2. [点我下载压缩包](https://gitee.com/wu_cl/fastapi_tortoise_mysql/repository/archive/master.zip)

## 使用

> ⚠️: 此过程请格外注意端口占用情况, 特别是 8000, 3306, 6379...

### 1: 传统

1. 安装依赖, *ps: 非 liunx 操作系统请先将 requirements.txt 文件中的 uvloop 包删掉*
    ```shell
    pip install -r requirements.txt
    ```

3. 创建数据库 ftm, 选择 utf8mb4 编码
4. 查看 backend/app/core/conf.py 配置文件, 检查并修改数据库配置信息
5. 执行数据库迁移
    ```shell
    cd backend/app/aerich
    
    # demo中直接省略这两步
    # aerich init -t env.TORTOISE_ORM  
    # aerich init-db
    
    # 执行此命令
    aerich upgrade
    
    # 当更新数据库 model 后，执行下面两个命令进行迁移
    aerich migrate
    
    aerich upgrade
    ```

6. 安装启动 redis
7. 查看 backend/app/core/conf.py 配置文件, 检查并修改 redis 配置信息
8. 执行 backend/app/main.py 文件启动服务
9. 浏览器访问: http://127.0.0.1:8000/v1/docs

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
