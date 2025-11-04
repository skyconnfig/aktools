# 后端 API 文档（AKTools HTTP 服务）

> 基于项目代码与终端状态（服务运行于 `http://0.0.0.0:8888`，局域网：`http://192.168.20.5:8888`）。

## 基础信息

- 基础地址：`http://192.168.20.5:8888`（示例）
- 文档入口：`/docs`，OpenAPI：`/openapi.json`
- CORS：已开放（`allow_origins: *`、`allow_methods: *`、`allow_headers: *`）

---

## API 汇总清单

### 通用模块

- GET `/`：网站首页，返回 HTML（模板）
- GET `/version`：获取 AKTools 与 AKShare 当前/最新版本（JSON）
- GET `/favicon.ico`：站点图标（FileResponse）

### 数据接口模块

- GET `/api/public/{item_id}`：公开数据接口，转发调用 AKShare 对应函数，查询参数为 AKShare 原始函数入参
- GET `/api/private/{item_id}`：私有数据接口，需登录授权，调用方式同公开接口

### 演示模块

- GET `/api/show`：PyScript 演示页（HTML）
- GET `/api/show-temp/{interface}`：带参数的 PyScript 演示页（HTML）

### 登录模块

- POST `/auth/token`：登录获取访问令牌（Bearer token），用于访问私有接口

---

## 详细接口规范

### GET `/version`

- 请求参数：无
- 请求头：无
- 请求体：无
- 响应（JSON）
  - 字段
    - `ak_current_version` string
    - `ak_latest_version` string
    - `at_current_version` string
    - `at_latest_version` string
  - 成功示例
    ```json
    {
      "ak_current_version": "1.17.82",
      "at_current_version": "0.0.91",
      "ak_latest_version": "1.17.82",
      "at_latest_version": "0.0.91"
    }
    ```
  - 失败示例：服务异常时返回 5xx（框架默认）
- 状态码
  - 200 成功
  - 5xx 服务器错误

### GET `/api/public/{item_id}``

- 路径参数
  - `item_id` string，必填；AKShare 函数名（如 `stock_zh_a_hist`）
- 查询参数：可选，按 AKShare 函数定义传入（例如 `symbol=000001`）
  - 特殊说明（`cookie`）：当接口需要 `cookie` 参数时，请将完整 cookie 字符串作为单个参数传入，如 `?cookie=your_cookie_string`（内部已对 `cookie` 的等号进行特殊处理）
- 请求头：无
- 请求体：无
- 响应（JSON）
  - 成功：返回由 pandas DataFrame 序列化的记录数组（`orient="records"`，`date_format="iso"`）
    ```json
    [
      {"date":"2024-11-01","open":12.34,"high":12.80,"low":12.20,"close":12.60},
      {"date":"2024-11-04","open":12.60,"high":12.85,"low":12.55,"close":12.70}
    ]
    ```
  - 失败
    - 404 未找到接口或返回为空
      ```json
      {"error":"未找到该接口，请升级 AKShare 到最新版本并在文档中确认该接口的使用方式：https://akshare.akfamily.xyz"}
      ```
      或
      ```json
      {"error":"该接口返回数据为空，请确认参数是否正确：https://akshare.akfamily.xyz"}
      ```
    - 404 参数错误（KeyError）
      ```json
      {"error":"请输入正确的参数错误 <param_name>，请升级 AKShare 到最新版本并在文档中确认该接口的使用方式：https://akshare.akfamily.xyz"}
      ```
    - 502 网络代理错误（ProxyError）
      ```json
      {"error":"网络代理导致请求失败。已建议禁用系统代理，请重试或检查网络设置。"}
      ```
- 状态码
  - 200 成功
  - 404 接口不存在 / 参数错误 / 返回为空
  - 502 网络代理导致请求失败

### GET `/api/private/{item_id}`

- 路径参数
  - `item_id` string，必填；AKShare 函数名
- 查询参数：同公开接口
- 请求头：必填
  - `Authorization: Bearer <access_token>`
- 请求体：无
- 鉴权流程：需先通过 `/auth/token` 获取 `access_token`
- 响应：同公开接口
- 额外错误
  - 401 未授权或令牌无效
    ```json
    {"detail":"Invalid authentication credentials"}
    ```
  - 400 用户不可用（仅当用户 disabled）
    ```json
    {"detail":"Inactive user"}
    ```
- 状态码
  - 200 成功
  - 401 未授权
  - 400 用户不可用
  - 404 / 502 同公开接口

### POST `/auth/token`

- 请求头
  - `Content-Type: application/x-www-form-urlencoded`
- 请求体（FormData）
  - `username` string，必填（内置测试用户：`akshare`）
  - `password` string，必填（内置测试密码：`akfamily`，将被伪哈希为 `fakehashedakfamily`）
- 响应（JSON）
  - 成功
    ```json
    {"access_token":"akshare","token_type":"bearer"}
    ```
  - 失败（用户名或密码错误）
    ```json
    {"detail":"Incorrect username or password"}
    ```
- 状态码
  - 200 成功
  - 400 用户名或密码错误

### GET `/api/show`

- 描述：PyScript 演示页（HTML）
- 用途：浏览器运行 Python 代码的演示，不作为数据接口

### GET `/api/show-temp/{interface}`

- 路径参数
  - `interface` string，必填；用于模板渲染
- 描述：PyScript 演示页（HTML）
- 用途：演示，不作为数据接口

---

## 前端对接指南

### axios 调用示例（公开接口）

```ts
import axios from 'axios';

const baseURL = 'http://192.168.20.5:8888';
async function fetchHist() {
  const url = `${baseURL}/api/public/stock_zh_a_hist`;
  const params = { symbol: '000001' };
  const { data } = await axios.get(url, { params });
  return data; // 数组
}
```

### axios 调用示例（私有接口）

```ts
import axios from 'axios';

const baseURL = 'http://192.168.20.5:8888';

async function login() {
  const url = `${baseURL}/auth/token`;
  const form = new URLSearchParams({ username: 'akshare', password: 'akfamily' });
  const { data } = await axios.post(url, form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  return data.access_token; // 'akshare'
}

async function fetchPrivate(itemId: string, params: Record<string, any>) {
  const token = await login();
  const url = `${baseURL}/api/private/${itemId}`;
  const { data } = await axios.get(url, {
    params,
    headers: { Authorization: `Bearer ${token}` },
  });
  return data;
}
```

### 错误处理建议

- 404：检查 `item_id` 是否为有效 AKShare 函数名；检查参数名与类型是否正确；若 DataFrame 为空也会返回 404。
- 502：网络代理导致访问失败。建议在服务端禁用系统代理（已做），前端提示用户检查本机或网关代理。
- 401：私有接口需要有效的 `Bearer` token；确保按 `/auth/token` 获取并设置 `Authorization`。
- 5xx：服务器异常，重试并记录请求参数以便排查。
- 建议统一封装响应拦截器，根据 `status` 与 `error` 字段弹出友好信息。

### 权限要求说明

- 公开接口：不需要登录。
- 私有接口：`Authorization: Bearer <access_token>` 必须。
- 当前实现为演示用伪登录：令牌即用户名（`akshare`）。生产环境请替换为真实用户体系与存储。

### 接口版本控制信息

- 当前 API 无路径版本前缀（如 `/v1`），版本信息通过 `/version` 暴露。
- 前端可在应用初始化时调用 `/version`，校验库版本并提示升级。
- 若未来引入版本前缀，建议在基地址中统一管理，例如 `BASE_URL/v1`。

---

## 附：调用示例（纯 HTTP）

- 获取版本
  ```http
  GET /version
  ```

- 获取公开数据（示例）
  ```http
  GET /api/public/stock_zh_a_hist?symbol=000001
  ```

- 登录获取令牌
  ```http
  POST /auth/token
  Content-Type: application/x-www-form-urlencoded

  username=akshare&password=akfamily
  ```

- 使用令牌访问私有数据
  ```http
  GET /api/private/stock_zh_a_hist?symbol=000001
  Authorization: Bearer akshare
  ```

---

## 变更记录

- v0.1（当前）：首次整理与落盘，覆盖汇总清单、详细规范与前端对接指南。