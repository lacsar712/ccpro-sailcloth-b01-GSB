# SailCloth-01 · 帆布浸渍防水台

帆布间布卷与浸渍固化台账基线项目（Django 5 + DRF + Vue 3 SPA）。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 后端 | Django 5 · DRF · SimpleJWT · django-cors-headers · Gunicorn |
| 前端 | Vue 3 · Vite · Pinia · Vue Router |
| 数据库 | PostgreSQL 15 |
| 部署 | Docker Compose · Nginx（前端反代 `/api`） |

## 路径与端口

- **项目路径**：`d:\work\document\bytecode\claudeCodePro\SailCloth\SailCloth-01`
- **前端**：http://localhost:3740
- **API**：http://localhost:8740
- **PostgreSQL**：localhost:6140

## 演示账号

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| `admin` | `123456` | 管理员 |
| `worker` | `123456` | 操作工 |

登录页已预填 `admin` / `123456`。后端 entrypoint 执行 migrate + seed。

## 业务规则

布卷状态不可设为「已固化」（`cured`），除非该卷**最近一条** `DipRun` 的 `cureHours` 已记录且 **≥ 12**。

规则实现：`backend/core/rules.py`

## 克重色带分界

- 全台仅一版分界（singleton）：**轻档上限** `lightMax` 与 **重档下限** `heavyMin`（整数 gsm，且轻档上限 < 重档下限）。
- 晾晒架每条挂签底色按该卷现行克重判定：`gsm ≤ lightMax` → 轻档，`gsm ≥ heavyMin` → 重档，其余 → 中档。
- `GET /api/gsm-bands/`：任何登录用户可读；`PUT /api/gsm-bands/`：仅 `admin` 角色可写（操作工 403）。
- 分界存库（`core_gsmbandsettings` 单行），刷新/重进不丢；改分界不触碰任何布卷的状态或克重；两名主管交叉提交时后写成功的一版覆盖先写的。
- 专页：`/gsm-bands`（顶栏「克重色带」），管理员可改，操作工只读。

## 快速启动

```bash
cd d:\work\document\bytecode\claudeCodePro\SailCloth\SailCloth-01
docker compose up --build
```

浏览器打开 http://localhost:3740

## SPA 信息架构

- **登录** → 进入主工作面
- **`/` 帆布间晾晒架（主）**：按帆布间挂布卷芯片（挂签底色按克重色带：轻/中/重档）；点击打开右侧面板登记 `DipRun`、切换固化状态；架下为浸渍流水次要信息流
- **`/gsm-bands` 克重色带分界专页**：管理员写下轻档上限/重档下限，操作工只读
- **`/rolls` · `/dips`（次要台账）**：保留列表/表单 CRUD，顶栏降级为「台账」入口，非主路径

API 契约不变（JWT、`/api/lofts|rolls|dips|dashboard|gsm-bands/`）。

## 配色

海军蓝（navy）+ 帆布米色（canvas），与温室绿主题区分。
