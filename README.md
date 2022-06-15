# fastapi_tortoise_mysql

#### 介绍
基于 fastapi + tortoise + aerich + mysql

# 使用
## 1. 安装依赖

```shell
pip install -r requirements.txt
```

## 2. 数据库迁移

```shell
1. 创建数据库, 选择 utf8mb4 编码

2. 查看 backend/app/core/conf.py 配置文件, 检查并修改数据库配置信息

3. 执行数据库迁移

cd backend/app/aerich

# demo中直接省略这两步
# aerich init -t env.TORTOISE_ORM  
# aerich init-db

aerich upgrade

# 当更新数据库 model 后，执行下面两个命令进行迁移
aerich migrate

aerich upgrade
```

## 3. 初始化数据

执行 `init_test_data.py` 文件
