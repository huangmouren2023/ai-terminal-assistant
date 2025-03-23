# AI 终端助手 (AI Terminal Assistant)

## 简介

AI 终端助手是一个轻量级工具，让您能够在命令行中使用自然语言描述来执行命令。不需要记住复杂的命令语法，只需描述您想要做什么，AI 就会为您生成并执行相应的命令。

类似于 `thefuck` 工具，但功能更强大，因为它不仅能纠正错误命令，还能从头创建命令。

## 安装要求

- Python 3.6+
- OpenAI 库: `pip install openai`
- python-dotenv (可选): `pip install python-dotenv`

## 安装步骤

1. 将 `install_ai_terminal.py` 和 `generate_command.py` 文件放在同一目录下
2. 准备配置文件 (选择以下任一方式):
   - 创建 `config.ini` 文件 (参考 `config.ini.example`)
   - 创建 `.env` 文件
   - 设置环境变量
3. 运行安装脚本:
   ```bash
   python install_ai_terminal.py
   ```
4. 重启终端或执行配置文件的 source 命令:
   - Windows PowerShell: 重启 PowerShell
   - Bash: `source ~/.bashrc`
   - Zsh: `source ~/.zshrc`

## 配置方法

### 方法 1: config.ini 文件

在脚本同目录创建 `config.ini` 文件:

```ini
[api]
api_key = your_api_key_here
base_url = https://api.anthropic.com  # 或 https://api.openai.com/v1

[model]
model = claude-3-sonnet-20240229  # 或 gpt-4o
```

### 方法 2: .env 文件

在脚本同目录创建 `.env` 文件:

```
ANTHROPIC_API_KEY=your_api_key_here
# 或 OPENAI_API_KEY=your_api_key_here
BASE_URL=https://api.anthropic.com
MODEL=claude-3-sonnet-20240229
```

### 方法 3: 环境变量

直接在系统中设置环境变量。

## 使用方法

安装完成后，在任何目录的终端中使用 `ai` 命令加上自然语言描述:

```bash
ai 列出当前目录下的所有文件按大小排序
```

系统会生成相应命令，询问确认后执行该命令。

## 常见问题

### 1. 重复安装会怎样？

重复安装不会导致问题，脚本会检查配置文件是否已包含 AI 函数，若已存在则不会重复添加。在不同目录下安装时，确保 `generate_command.py` 脚本路径正确，否则会更新为新目录中的脚本。

### 2. 终端重启后的作用范围？

是的，一旦安装完成并重启终端，您可以在系统的任何目录下使用 `ai` 命令，不需要回到安装目录。

### 3. 如何卸载？

卸载步骤:

1. 编辑以下文件，删除 `ai` 函数相关部分:
   - Windows: `~\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`
   - Bash: `~/.bashrc`
   - Zsh: `~/.zshrc`
2. 重启终端或执行配置文件的 source 命令
3. 可以删除 `generate_command.py` 和 `install_ai_terminal.py` 文件

手动卸载示例（适用于 Bash）:
```bash
sed -i '/# AI终端助手/,/^}/d' ~/.bashrc
source ~/.bashrc
```

## 示例命令

- `ai 列出当前目录下最大的5个文件`
- `ai 创建一个名为data的文件夹并进入它`
- `ai 查找所有包含"error"的日志文件`
- `ai 压缩当前目录下的所有图片文件`
- `ai 显示系统信息和内存使用情况`

## 进阶使用

- 使用中括号可以直接执行 shell 命令：`ai [ls -la]`
- 对于复杂任务，尽量详细描述需求
- 可以请求查找、排序、过滤等操作的组合

## 故障排除

- **命令生成失败**: 检查 API 密钥和网络连接
- **执行错误**: 可能是生成的命令不适合您的系统，尝试更详细的描述
- **权限问题**: 某些命令可能需要管理员/root权限
- **路径问题**: 如果遇到"未找到API密钥"错误，请确保使用的是绝对路径来读取配置文件

## 安全提示

- 始终检查 AI 生成的命令再执行，特别是涉及删除、修改系统文件的操作
- 避免将敏感信息作为参数传递给 `ai` 命令
- 不建议在生产环境服务器上使用此工具运行特权命令

## 关于项目

本项目由 Claude 3.7 Sonnet (Anthropic) 协助开发，旨在简化命令行操作，提高工作效率。

## 贡献与反馈

如有问题或建议，请提交 issue 或 pull request。

---

祝您使用愉快！