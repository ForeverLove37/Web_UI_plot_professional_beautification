# AcademicPlot Pro - AI驱动的学术图表美化工具

一个强大的Web应用程序，用于翻译和美化Python matplotlib图表，特别为学术论文出版设计。

## 功能特性

### 🎨 多种学术论文格式支持
- **Nature**: Arial/Helvetica字体，单栏3.35英寸，双栏7.08英寸
- **NeurIPS**: Times New Roman字体，单栏3.5英寸，双栏7.2英寸  
- **CVPR**: Times New Roman字体，单栏3.5英寸，双栏7.2英寸
- **Science**: Arial/Helvetica字体，单栏3.35英寸，双栏7.08英寸
- **IEEE**: Times New Roman字体，单栏3.5英寸，双栏7.2英寸

### 🌐 智能翻译功能
- 自动检测并翻译图表中的英文文本为中文
- 支持标题、坐标轴标签、图例、注释等文本翻译
- 保留代码注释的翻译

### 🎯 AI布局美化
- 智能优化子图布局排列
- 自动调整图表尺寸和比例
- 保持原始数据处理逻辑不变

### ⚙️ 自定义模式
- 自定义字体大小和标题大小
- 灵活调整图表宽度和高度
- 自定义DPI分辨率设置

### 📁 矢量图导出
- 支持PDF、SVG、EPS格式导出
- 高质量300+ DPI输出
- 自动嵌入字体支持

## 安装和运行

### 环境要求
- Python 3.7+
- pip包管理器

### 环境配置

1. **复制环境变量文件**:
   ```bash
   cp .env.example .env
   ```

2. **编辑 .env 文件**:
   - 设置你的 DeepSeek API 密钥: `DEEPSEEK_API_KEY=your_actual_api_key_here`
   - 设置 Flask 密钥 (可选): `FLASK_SECRET_KEY=your_secret_key_here`

3. **获取 DeepSeek API 密钥**:
   - 访问 [DeepSeek 官网](https://platform.deepseek.com/)
   - 注册账号并获取 API 密钥
   - 将密钥添加到 .env 文件中

### 一键安装和启动

**Windows用户**:
1. 双击运行 `install.bat` 安装依赖
2. 双击运行 `start.bat` 启动Web应用
3. 打开浏览器访问：`http://localhost:5000`

**手动安装**:
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py
```

### 项目结构
```
AcademicPlotPro/
├── src/                    # 源代码目录
│   ├── core/              # 核心处理模块
│   │   ├── enhanced_agent.py      # 增强版处理代理
│   │   └── zh_translator_agent_v2.py  # 原始代理
│   └── web/               # Web应用模块
│       ├── app.py         # Flask应用
│       ├── static/        # 静态资源
│       └── templates/     # HTML模板
├── uploads/               # 文件存储
│   ├── temp/             # 临时上传文件
│   └── outputs/          # 处理结果输出
├── main.py               # 主入口点
├── install.bat           # Windows一键安装
├── start.bat            # Windows一键启动
├── check_requirements.py # 依赖检查
└── requirements.txt      # Python依赖
```

## 使用方法

### 基本使用流程

1. **上传文件**: 拖放或点击选择Python绘图脚本文件 (.py)
2. **选择选项**: 
   - 启用AI布局美化
   - 选择学术论文格式和布局
   - 设置矢量图导出格式
   - 或启用自定义参数模式
3. **开始处理**: 点击"开始处理"按钮
4. **下载结果**: 处理完成后下载美化后的Python文件

### 支持的Python代码特征

- `matplotlib.pyplot` 绘图函数
- 英文文本标签和标题
- 多子图布局
- 各种图表类型（折线图、柱状图、散点图等）

## 文件结构

```
├── app.py                 # Flask Web应用程序
├── enhanced_agent.py      # 增强版处理代理
├── zh_translator_agent_v2.py  # 原始代理文件
├── templates/
│   └── index.html        # 主页面模板
├── static/
│   ├── css/
│   │   └── style.css     # 样式文件
│   └── js/
│       └── script.js     # JavaScript交互
├── requirements.txt      # Python依赖
└── test_plot.py         # 测试用例文件
```

## API接口

### POST /process
处理上传的Python文件

**参数**:
- `file`: Python文件
- `beautify`: 是否启用AI布局美化
- `academic_mode`: 是否启用学术模式
- `paper_format`: 论文格式选择
- `layout`: 单栏/双栏布局
- `vector_format`: 矢量图格式
- `custom_mode`: 自定义模式
- 各种自定义参数

**响应**:
```json
{
    "success": true,
    "message": "处理成功",
    "download_url": "/download/filename"
}
```

### GET /download/<filename>
下载处理后的文件

## 技术架构

- **后端**: Flask Web框架
- **AI处理**: DeepSeek API集成
- **前端**: HTML5 + CSS3 + JavaScript
- **图表处理**: matplotlib样式注入

## 注意事项

1. 确保Python文件使用标准的matplotlib语法
2. 处理大量文件时可能需要较长时间
3. 需要有效的DeepSeek API密钥
4. 建议在处理前备份原始文件

## 许可证

本项目仅供学习和研究使用。

## 支持

如有问题或建议，请提交Issue或联系开发团队。