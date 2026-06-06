# 医学影像报告检索与肺结节分类系统

Medical Imaging Report Retrieval & Lung Nodule Classification System

基于深度学习的肺部 CT 影像肺结节自动检测与分类系统，支持医生复核纠错、3D 可视化、患者自助查报。

---

## 环境要求

### 操作系统
- Windows 10/11（开发与测试环境）
- Linux / macOS 亦可运行（需自行调整启动方式）

### 后端 (Python)

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | **3.10+** | 推荐 3.11+，开发环境为 3.14 |
| pip | 22.0+ | Python 包管理 |

**核心库**（详见 [requirements.txt](backend/requirements.txt)）：

| 库 | 用途 |
|---|------|
| FastAPI ≥ 0.100 | Web 框架 |
| Uvicorn ≥ 0.23 | ASGI 服务器 |
| SQLAlchemy ≥ 2.0 | ORM，默认使用 SQLite |
| Pydantic ≥ 2.0 | 数据校验与序列化 |
| PyTorch ≥ 2.0 | 深度学习推理（ResNet18 肺结节分类） |
| torchvision ≥ 0.15 | 图像预处理 |
| OpenCV ≥ 4.8 | CT 切片图像处理 |
| bcrypt ≥ 4.0 | 密码哈希 |
| python-jose ≥ 3.3 | JWT 认证 |

### 前端 (Node.js)

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Node.js | **18.0+** | 推荐 20 LTS+，开发环境为 24 |
| npm | 9.0+ | 包管理 |

**核心库**（详见 [package.json](frontend/package.json)）：

| 库 | 用途 |
|---|------|
| Vue 3.5+ | 前端框架 |
| Vite 8+ | 构建工具 |
| TypeScript 6+ | 类型安全 |
| Element Plus 2.14+ | UI 组件库 |
| ECharts 6+ | 统计图表 |
| Three.js 0.184+ | 肺部 3D 可视化 |
| Pinia 3+ | 状态管理 |
| Axios 1.17+ | HTTP 请求 |

### 模型文件

系统使用本地训练的 ResNet18 模型进行肺结节分类。

- 模型路径：`backend/models/resnet18_v1.0.pt`
- 如模型文件不存在，系统将回退到**模拟推理模式**（随机结果），仅用于前端调试
- 模型下载：请联系项目管理员获取，或使用 `model_t/` 中的训练脚本自行训练

### 端口占用

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 API | **8000** | FastAPI + Uvicorn |
| 前端开发服务器 | **5173** | Vite Dev Server |

启动前请确保以上端口未被占用。

---

## 项目结构

```
software_engine/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/routers/        # RESTful 路由
│   │   ├── core/               # 配置、安全、错误码
│   │   ├── db/                 # 数据库初始化与会话
│   │   ├── ml/                 # 模型加载、推理、热力图
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── repositories/       # 数据访问层
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑层
│   │   └── storage/            # 文件存储工具
│   ├── models/                 # 训练好的模型权重
│   ├── data/                   # SQLite 数据库文件
│   ├── uploads/                # CT 切片、热力图上传目录
│   ├── static/                 # 静态资源（3D 模型等）
│   └── requirements.txt        # Python 依赖
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 请求封装
│   │   ├── components/         # 通用组件
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── types/              # TypeScript 类型定义
│   │   └── views/              # 页面组件
│   └── package.json            # Node.js 依赖
├── model_t/                    # 模型训练脚本
├── data/                       # 训练数据集
├── test_ct_slices/             # 测试用 CT 切片图像
├── start.bat                   # Windows 启动脚本（CMD）
├── start.ps1                   # Windows 启动脚本（PowerShell，推荐）
└── README.md
```

---

## 快速开始

### 1. 克隆项目

```bash
cd software_engine
```

### 2. 后端环境配置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows PowerShell）
.\venv\Scripts\Activate.ps1

# 激活虚拟环境（Windows CMD）
venv\Scripts\activate.bat

# 激活虚拟环境（Linux / macOS）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 前端环境配置

```bash
cd frontend

# 安装依赖
npm install
```

### 4. 启动服务

**方式一：一键启动（Windows PowerShell，推荐）**

```powershell
.\start.ps1
```

**方式二：分别启动**

```bash
# 终端 1 — 启动后端
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2 — 启动前端
cd frontend
npx vite --host 0.0.0.0 --port 5173
```

### 5. 访问系统

| 地址 | 说明 |
|------|------|
| http://localhost:5173 | 前端页面 |
| http://localhost:8000 | 后端 API |
| http://localhost:8000/docs | Swagger API 文档（自动生成） |
| http://localhost:8000/api/v1/health | 健康检查 |

### 6. 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin123` | `admin1234` |
| 医生 | 由管理员创建 | — |
| 患者 | 自行注册 | — |

> ⚠️ **生产环境请务必修改默认密码和 JWT SECRET_KEY**（见 [config.py](backend/app/core/config.py)）

---

## 功能概览

| 模块 | 功能 |
|------|------|
| **用户认证** | JWT 登录、角色权限（admin / doctor / patient） |
| **患者管理** | 患者建档、CT 检查记录管理 |
| **CT 切片上传** | 批量上传肺部 CT 切片图像 |
| **AI 推理** | ResNet18 自动检测肺结节（nodule / non_nodule），置信度评分 |
| **热力图** | Grad-CAM 可视化 AI 关注区域 |
| **医生复核** | 确认或纠正 AI 预测结果，纠正时自动更新预测标签 |
| **3D 可视化** | Three.js 肺部三维模型 + 结节标记 |
| **统计面板** | 上传量、阳性率、AI-医生一致率趋势图 |
| **审计日志** | 全操作追踪 |
| **患者门户** | 患者自助查看检查进度和报告 |

---

## 数据来源

- [LUNA16 (Lung Nodule Analysis 2016)](https://luna16.grand-challenge.org/) — 肺结节检测基准数据集
- [LIDC/IDRI](https://wiki.cancerimagingarchive.net/display/Public/LIDC-IDRI) — 肺部 CT 影像标注数据库
- [百度 AI Studio — 肺部 CT 数据集](https://aistudio.baidu.com/)

数据集位于 `data/` 目录（已排除于版本控制，需自行下载）。
