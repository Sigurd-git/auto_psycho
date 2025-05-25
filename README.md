# Auto Psycho TAT Platform

一个基于AI的在线主题统觉测验(TAT)实验平台，集成OpenAI API进行心理分析。

## 功能特性

- 🧠 **在线TAT实验**: 完整的主题统觉测验实验流程
- 🤖 **AI心理分析**: 使用OpenAI GPT模型进行专业心理分析
- 📊 **数据收集**: 自动收集和存储实验数据
- 📈 **报告生成**: 生成详细的心理分析报告
- 🔒 **隐私保护**: 符合心理学研究伦理要求
- 📱 **响应式设计**: 支持多种设备访问

## 技术栈

- **后端**: Flask + SQLAlchemy
- **AI分析**: OpenAI GPT-4
- **数据库**: SQLite (可扩展到PostgreSQL)
- **前端**: HTML5 + CSS3 + JavaScript
- **部署**: Python 3.8+ + uv

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+和uv包管理器：

```bash
# 安装uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆项目

```bash
git clone https://github.com/Sigurd-git/auto_psycho.git
cd auto_psycho
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 配置环境变量

复制环境变量示例文件并配置：

```bash
cp env.example .env
```

编辑`.env`文件，设置必要的配置：

```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Flask配置
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# 数据库配置
DATABASE_URL=sqlite:///data/tat_experiment.db
```

### 5. 运行应用

```bash
python run.py
```

应用将在 http://localhost:5000 启动。

## 项目结构

```
auto_psycho/
├── src/auto_psycho/           # 主应用包
│   ├── models/                # 数据模型
│   ├── views/                 # 视图控制器
│   ├── templates/             # HTML模板
│   ├── static/                # 静态资源
│   ├── utils/                 # 工具函数
│   ├── analysis/              # AI分析模块
│   ├── config.py              # 配置文件
│   └── app.py                 # Flask应用
├── static/tat_images/         # TAT图片资源
├── data/                      # 数据库文件
├── documents/                 # 项目文档
├── run.py                     # 应用启动文件
├── pyproject.toml             # 项目配置
└── README.md                  # 项目说明
```

## 使用说明

### 参与者流程

1. **访问首页**: 进入平台主页
2. **注册参与**: 填写基本信息并同意知情同意书
3. **阅读指导**: 了解TAT测验说明
4. **进行测验**: 观看TAT图片并编写故事
5. **完成测验**: 提交所有回答
6. **查看结果**: 获取AI生成的心理分析报告

### 管理员功能

- 查看实验统计数据
- 管理参与者信息
- 导出实验数据
- 配置系统参数

## API文档

### 主要端点

- `GET /` - 首页
- `POST /register` - 参与者注册
- `GET /experiment/instructions` - 实验说明
- `POST /experiment/submit` - 提交TAT回答
- `GET /admin/dashboard` - 管理员面板
- `GET /api/analysis/{session_id}` - 获取分析结果

## 开发指南

### 添加新的TAT图片

1. 将图片文件放入 `static/tat_images/` 目录
2. 确保文件名格式为 `tat_01.jpg`, `tat_02.jpg` 等
3. 更新配置文件中的图片数量设置

### 自定义分析提示词

编辑 `src/auto_psycho/analysis/openai_analyzer.py` 中的提示词模板：

```python
def _get_individual_response_prompt(self) -> str:
    return """
    自定义的分析提示词...
    """
```

### 扩展数据模型

在 `src/auto_psycho/models/` 目录下添加新的模型文件，并在 `__init__.py` 中导入。

## 部署

### 生产环境部署

1. 设置环境变量：
```bash
export FLASK_ENV=production
export OPENAI_API_KEY=your_production_key
```

2. 使用WSGI服务器：
```bash
uv add gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "src.auto_psycho.app:create_app('production')"
```

### Docker部署

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
EXPOSE 5000
CMD ["python", "run.py"]
```

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 作者: Sigurd
- 邮箱: sigurd@example.com
- 项目链接: [https://github.com/username/auto_psycho](https://github.com/username/auto_psycho)

## 致谢

- OpenAI提供的GPT模型
- Flask框架社区
- TAT测验理论研究者们