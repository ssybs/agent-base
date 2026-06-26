from src.utils.prompt_manager import prompt_manager
from src.api.schema import ChatHistoryItem
from src.llm.qwen_llm import QwenLLM
import asyncio

async def main():
    print("==== Day5 提示工程模板自测 ====")
    llm = QwenLLM()

    # 1. 测试RAG知识库问答模板
    print("\n1. 测试RAG问答Prompt模板")
    test_history = [
        ChatHistoryItem(role="user", content="什么是RAG？"),
        ChatHistoryItem(role="assistant", content="RAG是检索增强生成技术。")
    ]
    test_docs = """
    RAG全称Retrieval-Augmented Generation，检索增强生成。
    核心流程：文档切片→向量化存入向量库→用户提问检索相关片段→片段+问题送入大模型生成答案。
    作用：缓解大模型幻觉，支持私有企业知识库问答。
    """
    rag_prompt = prompt_manager.build_rag_chat_prompt(
        user_query="RAG有哪些落地优势？",
        context_docs=test_docs,
        history=test_history
    )
    print(f"RAG Prompt总token：{prompt_manager._check_prompt_token(rag_prompt, 3500)}")
    # 调用模型使用自定义模板
    resp_rag = await llm.chat(prompt="RAG有哪些落地优势？", history=test_history, system_prompt=rag_prompt)
    print("RAG问答返回：", resp_rag[:200])

    # 2. 测试CoT思维链推理模板
    print("\n2. 测试CoT思维链模板")
    cot_prompt = prompt_manager.build_cot_reason_prompt(user_query="3家门店分别营收1200、2500、1800，计算平均营收")
    resp_cot = await llm.chat(prompt="3家门店分别营收1200、2500、1800，计算平均营收", system_prompt=cot_prompt)
    print("CoT推理返回：", resp_cot[:300])

    # 3. 测试ReAct工具调用模板
    print("\n3. 测试ReAct工具模板")
    test_tools = [
        {"name": "calculator", "desc": "数学计算器，支持加减乘除", "params": {"num1": "数字", "num2": "数字", "op": "运算符"}},
        {"name": "search_doc", "desc": "检索企业知识库", "params": {"query": "查询关键词"}}
    ]
    react_prompt = prompt_manager.build_react_tool_prompt(
        user_query="计算 125 * 36",
        tool_list=test_tools,
        history=None
    )
    resp_react = await llm.chat(prompt="计算 125 * 36", system_prompt=react_prompt)
    print("ReAct工具输出JSON：", resp_react)

    # 4. 结构化提取模板测试
    print("\n4. 结构化文本提取模板")
    schema = '{"name":"用户姓名","phone":"联系电话","company":"公司名称"}'
    extract_prompt = prompt_manager.build_struct_extract_prompt(
        user_text="张三，电话13800138000，就职于AI科技有限公司",
        extract_schema=schema
    )
    resp_extract = await llm.chat(prompt="提取信息", system_prompt=extract_prompt)
    print("结构化提取结果：", resp_extract)

if __name__ == "__main__":
    asyncio.run(main())
