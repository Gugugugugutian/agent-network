from agent_network.base import BaseAgent
from agent_network.exceptions import ReportError


class recommend(BaseAgent):
    def __init__(self, graph, config, logger):
        super().__init__(graph, config, logger)

    def forward(self, messages, **kwargs):
        if error_message := kwargs.get("graph_error_message"):
            prompt = f"错误：{error_message}"
        else:
            subject = kwargs.get("subject")
            chapter = kwargs.get("chapter")
            prompt = f"我需要{subject}学科关于{chapter}章节的知识推荐。"

            if resources_result := kwargs.get("resources_result"):
                prompt += f"\n\n联网搜索的结果为： {resources_result}"

        self.add_message("user", prompt, messages)
        response = self.chat_llm(messages,
                                 api_key="sk-ca3583e3026949299186dcbf3fc34f8c",
                                 base_url="https://api.deepseek.com",
                                 model="deepseek-chat",
                                 response_format={"type": "json_object"}
                                 )
        response_data = response.content

        if "tool_name" in response_data:
            result = {**response_data["tool_args"]}
            return result, response_data["tool_name"]
        elif "result" in response_data:
            result = {
                "result": response_data["result"]
            }
            return result
        else:
            raise ReportError("unknown response format", "recommend")


class resources_tool(BaseAgent):
    def __init__(self, graph, config, logger):
        super().__init__(graph, config, logger)

    def forward(self, messages, **kwargs):
        if error_message := kwargs.get("graph_error_message"):
            prompt = f"错误：{error_message}"
        else:
            subject = kwargs.get("subject")
            chapter = kwargs.get("chapter")
            prompt = f"请给出{subject}学科，{chapter}章节的推荐知识资源。"

        self.add_message("user", prompt, messages)
        response = self.chat_llm(messages,
                                 api_key="sk-ca3583e3026949299186dcbf3fc34f8c",
                                 base_url="https://api.deepseek.com",
                                 model="deepseek-chat",
                                 response_format={"type": "json_object"}
                                 )
        response_data = response.content

        if "resources_result" in response_data:
            result = {
                "resources_result": response_data["resources_result"]
            }
            return result, "recommend"
        else:
            raise ReportError("unknown response format", "recommend")


class worker(BaseAgent):
    def __init__(self, graph, config, logger):
        super().__init__(graph, config, logger)

    def forward(self, messages, **kwargs):
        if error_message := kwargs.get("graph_error_message"):
            prompt = f"错误：{error_message}"
        else:
            task = kwargs.get("task")
            prompt = task

            if ocr_result := kwargs.get("ocr_result"):
                prompt += f"\n\n相关文件的文字识别结果为 {ocr_result}"

        self.add_message("user", prompt, messages)
        response = self.chat_llm(messages,
                                 api_key="sk-ca3583e3026949299186dcbf3fc34f8c",
                                 base_url="https://api.deepseek.com",
                                 model="deepseek-chat",
                                 response_format={"type": "json_object"})

        response_data = response.content

        if "tool_name" in response_data:
            result = {**response_data["tool_args"]}
            return result, response_data["tool_name"]
        elif "result" in response_data:
            result = {
                "result": response_data["result"]
            }
            return result
        else:
            raise ReportError("unknown response format", "worker")


class ocr_tool(BaseAgent):
    def __init__(self, graph, config, logger):
        super().__init__(graph, config, logger)

    def forward(self, messages, **kwargs):
        ocr_file_name = kwargs.get("ocr_file_name")
        if not ocr_file_name:
            raise ReportError("ocr_file_name is not provided", "worker")

        import easyocr
        reader = easyocr.Reader(['ch_sim', 'en'])
        ocr_result = reader.readtext(ocr_file_name, detail=0)
        self.log("assistant", ocr_result)

        result = {
            "ocr_result": ocr_result
        }
        # return result,
        return result, "worker"
