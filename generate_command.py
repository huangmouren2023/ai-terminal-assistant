#!/usr/bin/env python3
import sys
import os
import configparser
import platform
from typing import Tuple, Optional

# 尝试导入OpenAI库
try:
    from openai import OpenAI
except ImportError:
    print("错误: 缺少OpenAI库。请运行 'pip install openai' 安装。")
    sys.exit(1)

def load_api_config() -> Tuple[str, str, str]:
    """加载API配置，返回API密钥、基础URL和模型名称"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.ini")
    
    # 首先尝试从config.ini加载
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        api_key = config["api"]["api_key"]
        api_base = config["api"]["base_url"]
        model = config["model"]["model"]
        return api_key, api_base, model
    except (KeyError, configparser.Error):
        pass
    
    # 然后尝试从.env文件加载
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        # 如果python-dotenv未安装，直接尝试从环境变量获取
        pass
        
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    api_base = os.getenv("BASE_URL")
    model = os.getenv("MODEL")
    
    # 设置默认值
    if not api_base:
        # 通过API密钥推断默认基础URL
        if api_key and api_key.startswith('sk-ant-'):
            api_base = "https://api.anthropic.com"
            if not model:
                model = "claude-3-sonnet-20240229"
        else:
            api_base = "https://api.openai.com/v1"
            if not model:
                model = "gpt-4o"
    
    if not api_key:
        print("错误: 未找到API密钥。请在config.ini文件中设置，或设置环境变量OPENAI_API_KEY或ANTHROPIC_API_KEY。")
        sys.exit(1)
    
    return api_key, api_base, model

def get_system_prompt() -> str:
    """根据当前系统生成适合的系统提示"""
    system = platform.system()
    shell = os.environ.get('SHELL', '') if system != 'Windows' else 'PowerShell'
    
    # 确定shell类型
    shell_type = "PowerShell"
    if system == "Windows":
        shell_type = "PowerShell"
    elif "zsh" in shell:
        shell_type = "Zsh"
    elif "bash" in shell:
        shell_type = "Bash"
    else:
        shell_type = "Shell"
    
    # 生成通用系统提示
    prompt = f"""你是一个专业的命令行助手，负责将自然语言转换为精确的shell命令。

- 当前操作系统: {system}
- 当前Shell: {shell_type}
- 只返回命令本身，不要包含任何解释、引号或Markdown格式
- 避免生成危险或破坏性的命令，尤其是涉及系统文件删除的命令
- 命令应该是可以直接复制粘贴执行的，避免使用需要用户手动替换的占位符
- 处理复杂任务时，可以使用管道和多个命令的组合
- 针对用户的简短查询，优先生成简单的命令而非复杂的脚本
"""

    # 添加特定系统的提示
    if system == "Windows":
        prompt += """
对于Windows PowerShell:
- 使用PowerShell语法而非cmd语法
- 使用标准的PowerShell命令别名，如 ls 而非 dir
- 文件路径使用反斜杠(\\)或标准PowerShell路径格式
- 复杂命令可以使用PowerShell管道(|)和参数
"""
    elif system == "Darwin":  # macOS
        prompt += """
对于macOS:
- 优先使用macOS特有的命令，如open、pbcopy等
- 路径中的空格需要正确转义
- 文件路径使用正斜杠(/)
"""
    elif system == "Linux":
        prompt += """
对于Linux:
- 使用标准GNU/Linux命令集
- 文件路径使用正斜杠(/)
- 可以使用bash特性，如通配符、管道和重定向
"""

    return prompt

def generate_command(query: str) -> Optional[str]:
    """使用AI生成shell命令
    
    Args:
        query: 用户的自然语言查询
        
    Returns:
        生成的shell命令，或None（如果生成失败）
    """
    # 加载配置
    try:
        api_key, api_base, model = load_api_config()
    except Exception as e:
        print(f"加载配置失败: {str(e)}")
        return None
    
    # 初始化客户端
    try:
        client_kwargs = {"api_key": api_key}
        
        # 根据API密钥和base_url确定是OpenAI还是Anthropic
        if "anthropic" in api_base.lower():
            client_kwargs["base_url"] = api_base
            client = OpenAI(**client_kwargs)
            is_anthropic = True
        else:
            if "openai" not in api_base.lower():
                client_kwargs["base_url"] = api_base
            client = OpenAI(**client_kwargs)
            is_anthropic = False
        
    except Exception as e:
        print(f"初始化API客户端失败: {str(e)}")
        return None
    
    # 获取系统提示
    system_prompt = get_system_prompt()
    
    # 构建消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"将以下自然语言指令转换为适合的shell命令。只返回命令本身，不要包含任何解释或额外文本：\n\n{query}"}
    ]
    
    # 调用API
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,  # 低温度，更确定性的输出
            max_tokens=500
        )
        
        # 获取响应文本
        command = response.choices[0].message.content.strip()
        
        # 清理命令（去除可能的引号、Markdown格式等）
        command = command.strip('`')
        if command.startswith('```') and command.endswith('```'):
            command = command[3:-3].strip()
        
        # 去除可能的语言标识
        command_lines = command.split('\n')
        if len(command_lines) > 1 and command_lines[0].strip() in ['bash', 'sh', 'powershell', 'cmd', 'shell']:
            command = '\n'.join(command_lines[1:]).strip()
            
        return command
        
    except Exception as e:
        print(f"调用AI服务失败: {str(e)}")
        return None

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) <= 1:
        print("用法: python generate_command.py <自然语言查询>")
        return
    
    # 获取查询
    query = " ".join(sys.argv[1:])
    
    # 生成命令
    command = generate_command(query)
    
    # 输出结果
    if command:
        print(command)
    else:
        print("无法生成命令，请检查配置或重试。")

if __name__ == "__main__":
    main() 