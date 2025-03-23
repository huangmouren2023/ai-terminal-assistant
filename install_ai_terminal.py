#!/usr/bin/env python3
import os
import platform
import sys

def install_shell_function():
    """安装shell函数到用户的配置文件中"""
    # 获取当前脚本的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generate_script = os.path.join(script_dir, "generate_command.py")
    
    system = platform.system()
    
    if system == "Windows":
        # Windows: 安装到PowerShell配置文件
        ps_profile_path = os.path.expanduser("~\\Documents\\WindowsPowerShell\\Microsoft.PowerShell_profile.ps1")
        os.makedirs(os.path.dirname(ps_profile_path), exist_ok=True)
        
        function_code = f"""
function ai {{
    param (
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Query
    )
    
    $fullQuery = $Query -join " "
    
    if ($fullQuery) {{
        # 调用Python脚本生成命令
        $generatedCommand = python "{generate_script}" $fullQuery
        
        if ($generatedCommand) {{
            Write-Host "生成的命令: $generatedCommand" -ForegroundColor Green
            $confirm = Read-Host "是否执行此命令? (y/n)"
            
            if ($confirm -eq "y") {{
                # 在当前PowerShell会话中执行命令
                Invoke-Expression $generatedCommand
            }}
        }}
    }} else {{
        Write-Host "用法: ai <自然语言命令>" -ForegroundColor Yellow
    }}
}}
"""
        
        # 检查函数是否已经存在
        if os.path.exists(ps_profile_path):
            with open(ps_profile_path, 'r') as f:
                if "function ai" in f.read():
                    print("✅ PowerShell函数已存在")
                    return
        
        # 添加函数到配置文件
        with open(ps_profile_path, 'a+') as f:
            f.write(function_code)
        
        print(f"✅ 已安装PowerShell函数到: {ps_profile_path}")
        print("使用方法: 重启PowerShell后，输入 'ai <自然语言命令>' 即可")
    
    else:
        # Linux/macOS: 安装到bash或zsh配置文件
        shells_to_try = []
        
        if os.path.exists(os.path.expanduser("~/.zshrc")):
            shells_to_try.append(("Zsh", "~/.zshrc"))
        
        if os.path.exists(os.path.expanduser("~/.bashrc")):
            shells_to_try.append(("Bash", "~/.bashrc"))
        
        if not shells_to_try:
            shells_to_try.append(("Bash", "~/.bashrc"))  # 默认使用bash
        
        for shell_name, config_file in shells_to_try:
            config_path = os.path.expanduser(config_file)
            
            function_code = f"""
# AI终端助手
ai() {{
    query="$*"
    
    if [ -n "$query" ]; then
        # 调用Python脚本生成命令
        generated_command=$(python3 "{generate_script}" "$query")
        
        if [ -n "$generated_command" ]; then
            echo -e "\\033[32m生成的命令: $generated_command\\033[0m"
            read -p "是否执行此命令? (y/n): " confirm
            
            if [ "$confirm" = "y" ]; then
                # 在当前shell会话中执行命令
                eval "$generated_command"
            fi
        fi
    else
        echo "用法: ai <自然语言命令>"
    fi
}}
"""
            
            # 检查函数是否已经存在
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    if "ai()" in f.read():
                        print(f"✅ {shell_name}函数已存在")
                        continue
            
            # 添加函数到配置文件
            with open(config_path, 'a+') as f:
                f.write(function_code)
            
            print(f"✅ 已安装{shell_name}函数到: {config_path}")
            print(f"使用方法: 运行 'source {config_file}' 或重启终端后，输入 'ai <自然语言命令>' 即可")

if __name__ == "__main__":
    print("🔧 正在安装AI终端助手...")
    install_shell_function()
    print("✨ 安装完成！") 