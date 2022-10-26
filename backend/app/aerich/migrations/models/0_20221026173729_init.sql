-- upgrade --
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(20) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `uid` VARCHAR(64) NOT NULL UNIQUE COMMENT '用户UID',
    `username` VARCHAR(32) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(256) NOT NULL  COMMENT '密码',
    `email` VARCHAR(64) NOT NULL UNIQUE COMMENT '邮箱',
    `is_active` BOOL NOT NULL  COMMENT '是否激活' DEFAULT 1,
    `is_superuser` BOOL NOT NULL  COMMENT '是否超级管理员' DEFAULT 0,
    `avatar` VARCHAR(256)   COMMENT '头像',
    `mobile_number` VARCHAR(16)   COMMENT '手机号',
    `wechat` VARCHAR(32)   COMMENT '微信',
    `qq` VARCHAR(16)   COMMENT 'QQ',
    `blog_address` VARCHAR(128)   COMMENT '博客地址',
    `introduction` LONGTEXT   COMMENT '自我介绍',
    `last_login` DATETIME(6)   COMMENT '上次登录时间',
    `created_time` DATETIME(6) NOT NULL  COMMENT '注册时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_time` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='用户类';
