import os, sys
from openai import OpenAI
from mcdreforged.api.all import *

import time

__mcdr_server: PluginServerInterface

help_msg = '''-------- §a ask §r--------
§b!!ask  §f- §c显示帮助消息
§b!!ask <quesetion> §f- §c问AI问题
§b!!askr <quesetion> §f- §c问AI问题（开启推理）
§b!!askall <quesetion> §f- §c问AI问题（公屏广播）
§b!!askallr <quesetion> §f- §c问AI问题（公屏广播，开启推理）
-----------------------------------
'''

class Config(Serializable):
    apikind:str = "zhipuAI"
    # 默认为智谱清言
    apikey:str = "yourapikey"

    model:str = "glm-4-flash"

    systemprompt:str = "你是一个Minecraft服务器助手，对Minecraft游戏知识非常了解，由于输出端无法解析markdown，请不要输出markdown控制字符并减少回车的使用（如换行时只使用一个回车）"

config: Config
CONFIG_FILE = os.path.join('config', 'ask.json')

reasonermodel={'openai':'o3-mini','deepseek':'deepseek-reasoner'}

def waitairesponse(content , model ):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": str(config.systemprompt)},
            {"role": "user", "content": str(content)}
        ]
    )
    return response.choices[0].message.content

def on_load(server: PluginServerInterface, old):

    # 获取存量数据
    global config, __mcdr_server
    __mcdr_server = server
    config = __mcdr_server.load_config_simple(CONFIG_FILE, in_data_folder=False, target_class=Config)
    __mcdr_server.register_help_message('!!ask', '询问AI问题')
    __mcdr_server.register_help_message('!!askall', '询问AI问题，将回答展示给全体玩家')
    global client

    if config.apikind=="zhipuAI":
       client = OpenAI(api_key=config.apikey,base_url="https://open.bigmodel.cn/api/paas/v4/")
    if config.apikind == "openAPI":
        client = OpenAI(api_key=config.apikey)
    if config.apikind == "deepseek":
        client = OpenAI(api_key=config.apikey,base_url="https://api.deepseek.com")
    if config.apikind == "kimi":
        client = OpenAI(api_key=config.apikey,base_url="https://api.moonshot.cn/v1")
    #注册指令
    command_builder = SimpleCommandBuilder()
    command_builder.command('!!ask <question>', get_answer)
    command_builder.command('!!askr <question>', get_answerR)
    command_builder.command('!!askall <question>', get_answerall)
    command_builder.command('!!askallr <question>', get_answerallR)
    command_builder.command('!!ask', help_info)
    command_builder.arg('question', Text)
    command_builder.register(server)

# -------------------------
# command handlers
# -------------------------
def help_info(server):
    for line in help_msg.splitlines():
        server.reply(line)


def get_answer(seldserver, context):
    server.reply("["+config.apikind+"]:"+waitairesponse(context, config.model))


def get_answerR(server, context):
    if(config.apikind=="openai" or config.apikind=="deepseek"):
        server.reply("["+config.apikind+"]:"+waitairesponse(context, reasonermodel[config.apikind]))
    else:
        server.reply("["+config.apikind+"]:"+waitairesponse(context, config.model))


def get_answerall(server, context):
    server.get_server().broadcast("["+config.apikind+"]:"+waitairesponse(context, config.model))

def get_answerallR(server, context):
    if(config.apikind=="openai" or config.apikind=="deepseek"):
        server.get_server().broadcast("[" + config.apikind + "]:" + waitairesponse(context, reasonermodel[config.apikind]))
    else:
        server.get_server().broadcast("[" + config.apikind + "]:" + waitairesponse(context, config.model))
