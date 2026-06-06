"""
FastAPI 应用入口

启动命令:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import UPLOAD_DIR, STATIC_DIR
from app.core.errors import ErrorCode, ERROR_HTTP_STATUS, ERROR_MESSAGES
from app.core.response import error_response
from app.db.init_db import init_database
from app.api.routers import auth_router, users_router
from app.api.routers.patients import router as patients_router
from app.api.routers.slices import router as slices_router
from app.api.routers.inference import router as inference_router
from app.api.routers.reports import router as reports_router
from app.api.routers.reviews import router as reviews_router
from app.api.routers.statistics import router as statistics_router
from app.api.routers.view3d import router as view3d_router
from app.api.routers.patient_portal import router as patient_portal_router
from app.api.routers.audit import router as audit_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    print("[app] 正在初始化数据库...")
    init_database()
    print("[app] 服务启动完成")
    yield
    print("[app] 服务关闭")


app = FastAPI(
    title="医学影像报告检索与肺结节分类系统",
    description="Medical Imaging Report Retrieval & Lung Nodule Classification System API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件（允许前端开发服务器跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """捕获未处理的异常，返回统一错误响应"""
    return JSONResponse(
        status_code=500,
        content=error_response(ErrorCode.UNKNOWN_ERROR, str(exc)),
    )


# 静态文件服务（上传的切片、热力图、3D 模型等）
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 注册路由
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(patients_router)
app.include_router(slices_router)
app.include_router(inference_router)
app.include_router(reports_router)
app.include_router(reviews_router)
app.include_router(statistics_router)
app.include_router(view3d_router)
app.include_router(patient_portal_router)
app.include_router(audit_router)


@app.get("/")
def root():
    """根路径 - 健康检查"""
    return {"status": "ok", "message": "医学影像系统 API 正在运行"}


@app.get("/api/v1/health")
def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
