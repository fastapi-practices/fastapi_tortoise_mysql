# fastapi_mysql

#### 介绍
基于 fastapi + tortoise + aerich + mysql8 demo


# 数据库迁移
```shell
# 默认仓库
cd backend/app/aerich

# demo中直接省略这两步
# aerich init -t env.TORTOISE_ORM  
# aerich init-db

aerich upgrade

# 当更新数据库 model 后，执行下面两个命令进行迁移
aerich migrate

aerich upgrade
```
