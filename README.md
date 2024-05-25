# FastAPI Tortoise Architecture

作为 FastAPI 框架的一个基础项目，基于 python3.10 开发

## 特征

- [x] FastAPI > 0.100.0
- [x] Async design
- [x] Restful API
- [x] Tortoise-orm > 0.20.0
- [x] Pydantic 2.0
- [x] Docker
- [ ] ......

## 使用

> [!WARNING]
> 此过程请格外注意端口占用情况, 特别是 8000, 3306, 6379...

### 1: 传统

1. 安装依赖项

    ```shell
    pip install -r requirements.txt
    ```

2. 创建一个数据库 `ftm`, 选择 `utf8mb4` 编码
3. 安装启动 Redis
4. 进入 backend 目录

   ```shell
   cd backend
   ```

5. 创建一个 `.env` 文件

   ```shell 
   touch .env
   cp .env.example .env
   ```

6. 按需修改配置文件 `core/conf.py` 和 `.env`
7. 数据库迁移

    ```shell
    # 初始化数据库，生成迁移文件
    aerich init-db
   
    # 执行迁移
    aerich upgrade
   
    # 当更新数据库 model 后，执行下面两个命令进行迁移
    aerich migrate
    aerich upgrade
    ```

8. 启动 fastapi 服务

   ```shell
   # 帮助
   fastapi --help
   
   # 开发模式
   fastapi dev main.py
   ```
   
9. 浏览器访问: http://127.0.0.1:8000/api/v1/docs

---

### 2: docker

1. 进入 `docker-compose.yml` 文件所在目录，创建环境变量文件 `.env`

    ```shell
    dcd deploy/docker-compose/
   
    cp .env.server ../../../backend/.env
    ```

2. 执行一键启动命令

    ```shell
    docker-compose up -d --build
    ```

3. 等待命令自动完成
4. 浏览器访问：http://127.0.0.1:8000/api/v1/docs

## 互动

[WeChat / QQ](https://github.com/wu-clan)

## 赞助

如果此项目能够帮助到你，你可以赞助作者一些咖啡豆表示鼓励：[:coffee: Sponsor :coffee:](https://wu-clan.github.io/sponsor/)

## 许可证

本项目根据 MIT 许可证的条款进行许可
