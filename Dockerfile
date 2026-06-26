# 基础python镜像
FROM python:3.14-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（asyncpg postgres驱动编译依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 安装uv包管理器
RUN pip install uv

# 复制依赖配置
COPY pyproject.toml .
# 复制依赖配置
COPY pyproject.toml uv.lock ./
# 仅安装依赖，不复制源码缓存
RUN uv sync --extra dev

# 复制全部项目代码
COPY . .

# 暴露服务端口
EXPOSE 8000

# 容器启动命令
CMD ["uv", "run", "python", "main.py"]
