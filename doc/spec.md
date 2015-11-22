# 接口规范

基于 JSON 的 API，包含以下接口:

1. 握手
1. 注册
1. 登录


## 握手

##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作
agent | string | 客户端类型

#### 请求示例

{"action": "handshake", "agent": "MINET"}

#### 响应示例

{"server": "MIRO"}

#### 异常示例

{"code": "UNKNOWN_AGENT", "message": "Your agent is rejected."}


## 注册


##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作
username | string | 用户名
password | string | 密码
nickname | string | 昵称


#### 请求示例

{"action": "register", "username": "%s", "password": "%s", "nickname": "%s"}

#### 响应示例

{"code":"REGISTER_SUCCESS","message":"success"}

#### 异常示例

{"code":"REGISTER_FAIL","message":"xxx"}

## 登录

##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作
username | string | 用户名
password | string | 密码


#### 请求示例

{"action": "login", "username": "%s", "password": "%s"}

#### 响应示例

{"code":"LOGIN_SUCCESS","message":"success"}

#### 异常示例

{"code":"LOGIN_FAIL","message":"xxx"}