import importlib
import json

from agent_network.network.graph import Graph
from agent_network.network.route import Route
from agent_network.network.nodes.graph_node import AgentNode
from datetime import datetime
import yaml
from agent_network.network.executable import Executable
from agent_network.utils.llm import chat_llm
import agent_network.pipeline.context as ctx
from abc import abstractmethod

from time import sleep


class BaseAgent(Executable):

    def __init__(self, config, logger):
        super().__init__(config["name"], config["task"], config["description"])
        self.config = config
        self.task = self.config["task"]
        self.title = self.config["name"]
        self.description = self.config["description"]
        self.class_name = self.config["ref_id"]
        self.role = self.config["role"]
        self.description = self.config["description"]

        self.params = self.config["params"]
        self.results = self.config["results"]

        self.model = self.config["model"]
        self.prompts = self.config.get("prompts")
        self.tools = self.config.get("tools")
        self.logger = logger
        self.if_error = False
        self.error = None
        self.history_action = []
        self.append_history_num = 0
        self.runtime_revision_number = 0
        self.cost_history = []
        self.usages = []

        self.messages = []
        self.initial_messages()

    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })
        self.log(role, content, self.__class__.__name__)

    def initial_messages(self):
        pass

    @abstractmethod
    def forward(self, message, **kwargs):
        results = dict()
        return results

    def execute(self, current_task, **kwargs):
        return self.forward(current_task, **kwargs)
    def chat_llm(self, model, message):
        response, usage = chat_llm(model, message)
        self.cur_execution_cost["llm_usage_history"].append(usage)
        return response
    
    def log(self, role, content, class_name=None):
        if class_name is None:
            class_name = self.name
        cur_time = datetime.now()
        if not isinstance(content, str):
            content = json.dumps(content, indent=4, ensure_ascii=False)
        self.logger.log(cur_time, role, content, class_name=class_name)

    def log_messages(self, messages):
        for message in messages:
            self.log(message["role"], message["content"])


class BaseAgentGroup(Executable):
    def __init__(self, graph, config, logger):
        super().__init__(config["name"], config["task"], config["description"])
        self.config = config
        self.name = self.config["name"]
        self.logger = logger

        self.max_step = self.config["max_step"]

        self.agents = []
        self.agent_communication_prompt = dict()
        self.context = dict()

        self.load_graph(graph)
        self.add_routes(graph)

        self.tools = []

    def load_graph(self, graph):
        for agent_item in self.config["agents"]:
            agent_name, agent_config_path = list(agent_item.items())[0]
            with open(agent_config_path, "r", encoding="utf-8") as f:
                agent_config = yaml.safe_load(f)
            agent = self.import_agent(agent_config)
            graph.add_node(agent_name,
                            AgentNode(agent,
                                      agent_config["params"],
                                      agent_config["results"]))
            self.agents.append(agent_name)
    
    def add_routes(self, graph: Graph):
        graph.add_route(self.name, self.config["start_agent"], "system")

        if self.config["routes"]:
            for route in self.config["routes"]:
                graph.add_route(route["source"], route["target"], route["type"])

    def import_agent(self, agent_config):
        if agent_config["load_type"] == "module":
            agent_module = importlib.import_module(agent_config["loadModule"])
            agent_class = getattr(agent_module, agent_config["loadClass"])
            agent_instance = agent_class(agent_config, self.logger)
        else:
            raise Exception("Agent load type must be module!")
        return agent_instance

    def execute(self, message, **kwargs):
        return {
            "message": message,
            "next_agent": self.config["start_agent"]
        }
