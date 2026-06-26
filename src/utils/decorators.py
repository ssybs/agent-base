from functools import wraps
from time import time
from src.core.logger import log

# --------------------------知识点分割线---------------------------
# 知识点1：装饰器底层原理
# 本质是接收函数、返回新包装函数的高阶函数；@语法糖简化调用
# wraps(func) 保留原函数名称、文档，否则日志会丢失真实函数名
# 知识点2：通用业务装饰器场景
# 1. cost_time：统计接口/模型调用耗时，优化性能
# 2. exception_catch：统一捕获异常，不用到处写try except
# ----------------------------------------------------------------

def cost_time(func):
    """统计函数执行耗时装饰器，同步/异步函数通用"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time()
        result = await func(*args, **kwargs)
        cost = round((time() - start) * 1000, 2)
        log.info(f"【{func.__name__}】执行耗时: {cost} ms")
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        cost = round((time() - start) * 1000, 2)
        log.info(f"【{func.__name__}】执行耗时: {cost} ms")
        return result

    # 判断函数是否为异步
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

def catch_exception(func):
    """全局异常捕获装饰器，记录堆栈日志"""
    @wraps(func)
    async def async_wrap(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            log.error(f"函数 {func.__name__} 异常: {str(e)}", exc_info=True)
            raise e
    return async_wrap
