from loguru import logger
import sys
import os
from datetime import datetime

# --------------------------知识点分割线---------------------------
# 知识点1：日志分级设计
# trace(调试最细) < debug < info < warning < error < critical
# 生产环境只保留info以上，开发环境开启debug
# 知识点2：文件轮转
# rotation="500 MB" 文件超过500M自动拆分，retention="7 days" 7天日志自动清理
# 知识点3：上下文埋点思路
# 后续接口请求时，每个请求生成唯一request_id，打入日志，排查链路问题
# ----------------------------------------------------------------

# 日志存储路径
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
# 日志文件命名
log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# 移除loguru默认控制台输出
logger.remove()

# 1. 控制台输出（开发环境彩色）
logger.add(
    sink=sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

# 2. 文件持久化输出
logger.add(
    sink=log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="500 MB",
    retention="7 days",
    encoding="utf-8",
    level="INFO"
)

# 对外导出全局日志对象
log = logger
