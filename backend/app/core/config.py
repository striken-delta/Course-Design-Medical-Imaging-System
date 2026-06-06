import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 数据库配置 - SQLite 文件存放于 backend/data/
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'app.db'}"

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "medical-imaging-system-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8小时

# 文件存储目录
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CT_SLICE_DIR = UPLOAD_DIR / "ct_slices"
CT_SLICE_DIR.mkdir(parents=True, exist_ok=True)
HEATMAP_DIR = UPLOAD_DIR / "heatmaps"
HEATMAP_DIR.mkdir(parents=True, exist_ok=True)

# 静态资源目录
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR = STATIC_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# 默认管理员账号
DEFAULT_ADMIN_USERNAME = "admin123"
DEFAULT_ADMIN_PASSWORD = "admin1234"

# ML 模型配置
ML_MODEL_DIR = BASE_DIR / "models"
ML_MODEL_DIR.mkdir(parents=True, exist_ok=True)
ML_MODEL_PATH = ML_MODEL_DIR / "resnet18_v1.0.pt"    # 本地训练模型权重路径
ML_MODEL_VERSION = "resnet18_v1.0"
ML_INPUT_SIZE = (224, 224)
ML_DEVICE = os.getenv("ML_DEVICE", "cpu")             # cpu 或 cuda
ML_ENABLE_GRAD_CAM = os.getenv("ENABLE_GRAD_CAM", "0") == "1"  # 是否启用热力图

# 分页默认值
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
