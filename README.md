# FastAutoTest

#### 介绍
基于 fastapi + tortoise + aerich + mysql8 自动化接口测试平台


# 迁移
```shell
# 默认仓库
cd backend/app/aerich

# aerich init -t env.TORTOISE_ORM  # 这步可省略

aerich init-db

# 修改数据库 model 后:
aerich migrate

aerich upgrade
```
