import threading

from agent_network.graph.graph import Graph
from flask import Flask, request
from agent_network.constant import network, logger

app = Flask(__name__)


@app.route('/service', methods=['POST'])
def service():
    context = request.json
    print(context)
    assert context['flowId'] is not None, "智能体流程节点未找到"
    assert context['task'] is not None, "智能体任务未找到"
    # 为输入的params参数加上task任务
    _params = context.get('params')
    _params['task'] = context['task']
    # 创建graph
    graph = Graph(logger)
    graph.execute(network, context['flowId'], _params, context.get("results"))
    result = graph.retrieve_results(context.get("results"))
    graph.release()
    return result


@app.route('/recommend', methods=['POST'])
def recommend():
    context = request.json
    print(context)
    assert context['flowId'] is not None, "智能体流程节点未找到"
    assert context['subject'] is not None, "未明确推荐学科"
    assert context['chapter'] is not None, "未明确推荐章节"
    # 为输入的params参数加上subject和chapter两个
    _params = context.get('params')
    _params['subject'] = context.get('subject')
    _params['chapter'] = context.get('chapter')
    # 创建graph
    graph = Graph(logger)
    graph.execute(network, context['flowId'], _params, context.get("results"))
    result = graph.retrieve_results(context.get("results"))
    graph.release()
    return result


def run_web(debug=False):
    app.run(host='0.0.0.0', port=18081, debug=debug)


if __name__ == '__main__':
    web_thread = threading.Thread(target=run_web)
    web_thread.start()
    
"""
Example Request:

{
    "flowId": "worker",
    "task": "学校发了一个新的讲座通知，相关文件在 C:\\Users\\lornd\\Downloads\\FC804E96CF497636909FC43BE21_07186CAC_E21D4.jpg，能告诉我讲座什么时候在哪里举行，是有关于什么的讲座吗？",
    "params": {
        "task": "学校发了一个新的讲座通知，相关文件在 C:\\Users\\lornd\\Downloads\\FC804E96CF497636909FC43BE21_07186CAC_E21D4.jpg，能告诉我讲座什么时候在哪里举行，是有关于什么的讲座吗？",
    },
    "results": {
        "result": "讲座相关信息"
    }
}
"""
