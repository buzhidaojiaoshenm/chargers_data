#!/bin/bash

function check_requirements() {
    echo "检查配置文件..."

    # 检查 config/api.token 是否存在
    if [ ! -f "config/api.token" ]; then
        echo "错误：未找到 config/api.token 文件"
        echo "请在 config 目录下创建 api.token 文件并添加您的 API 令牌"
        exit 1
    fi

    # 检查 requirements.txt 是否存在
    if [ ! -f "requirements.txt" ]; then
        echo "错误：未找到 requirements.txt 文件"
        echo "请创建 requirements.txt 文件并添加项目依赖"
        exit 1
    fi

    # 检查 api.token 是否为空
    if [ ! -s "config/api.token" ]; then
        echo "错误：api.token 文件为空"
        echo "请在 api.token 文件中添加您的 API 令牌"
        exit 1
    fi

    # 检查 search_config.json 是否存在
    if [ ! -f "config/search_config.json" ]; then
        echo "错误：未找到 search_config.json 文件"
        echo "请在 config 目录下创建 search_config.json 文件"
        exit 1
    fi

    echo "配置文件检查完成！"
}

function setup_venv() {
    # 检查 venv 目录是否已存在
    if [ -d "venv" ]; then
        echo "虚拟环境目录已存在。是否删除并重新创建？ (y/n)"
        read answer
        if [ "$answer" = "y" ]; then
            rm -rf venv
        else
            echo "操作已取消"
            exit 1
        fi
    fi

    # 创建虚拟环境
    echo "创建虚拟环境..."
    python3 -m venv venv

    # 激活虚拟环境
    source venv/bin/activate

    # 更新 pip
    echo "更新 pip..."
    pip install --upgrade pip

    # 如果 requirements.txt 存在，安装依赖
    echo "安装项目依赖..."
    pip install -r requirements.txt

    echo "虚拟环境创建完成！"
    echo "使用 'source venv/bin/activate' 激活虚拟环境"
    echo "使用 'deactivate' 退出虚拟环境"
}

# 主流程
check_requirements
setup_venv

if [ $? -eq 0 ]; then
    echo "项目初始化完成！"
    echo "您现在可以开始使用项目了"
else
    echo "项目初始化失败，请检查错误信息"
    exit 1
fi 