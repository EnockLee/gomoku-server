# 五子棋（局域网版）

这是一个基于 **FastAPI + HTML / CSS / JavaScript** 的局域网五子棋游戏  
支持两名玩家通过浏览器进行对战，并允许第三方观战。

## 功能特点
- 🎮 局域网双人对战
- ♟ 黑白棋自动分配，轮流落子
- 🏆 自动判断胜负与平局
- 👀 观战模式支持
- 🔗 房间号分享即可加入
- 🖼 使用 Canvas 绘制棋盘
- ⚡ FastAPI 轻量级后端

## 项目结构
.
├── frontend
│   ├── index.html
│   ├── style.css
│   └── app.js
├── main.py
└── README.md

## 环境要求
- Python 3.8+
- 现代浏览器（Chrome / Edge / Firefox）

## 安装与运行
1. 克隆项目
git clone <你的仓库地址>
cd <项目目录>

2. 创建并激活虚拟环境
python -m venv venv
Windows：
venv\Scripts\activate
macOS / Linux：
source venv/bin/activate

3. 安装依赖
pip install fastapi uvicorn pydantic

4. 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000

5. 浏览器访问
http://本机局域网IP:8000/

## 游戏玩法
1. 点击“创建房间”
2. 分享房间链接给另一名玩家
3. 第一位为黑棋，第二位为白棋
4. 点击棋盘落子，轮流进行
5. 游戏结束自动显示结果
6. 其余玩家为观战者

## 技术实现
前端：
HTML / CSS / JavaScript  
Canvas 绘制棋盘  
Fetch API 通信  
localStorage 保存玩家 ID  

后端：
Python + FastAPI  
房间与玩家管理  
回合校验  
胜负和平局判断  

## 已知限制
- 房间数据存于内存，重启即丢失
- 使用轮询方式同步状态
- 不支持断线重连

## 后续可扩展
- WebSocket 实时对战
- AI 对战
- 棋谱保存与回放
- 公网部署

## 开源协议
MIT License
