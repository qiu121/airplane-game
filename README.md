# 启动指南
<https://python-poetry.org/docs/basic-usage/>
## 环境配置
- 创建虚拟环境
```zsh
poetry env use python3
```
- 激活虚拟环境
```zsh
poetry shell
```
## 添加并安装依赖
```zsh
# poetry add pymysql panda

poetry install 
```
## 执行脚本
```zsh
poetry run python3 main.py
```
## 导出
```zsh
poetry export --dev -f requirements.txt --without-hashes --output requirements.txt 
```