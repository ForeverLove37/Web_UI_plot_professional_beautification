import os
import re
import requests
import json
import ast
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 配置区 ---
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

TARGET_PLOT_FUNCTIONS = {
    'title', 'xlabel', 'ylabel', 'suptitle',
    'set_title', 'set_xlabel', 'set_ylabel', 'text', 'legend'
}

# --- 标准论文格式配置 ---
PAPER_FORMATS = {
    'nature': {
        'name': 'Nature',
        'single_column': (3.35, 2.5),  # 85mm width
        'double_column': (7.08, 4.0),  # 180mm width
        'font_family': ['SimHei', 'Microsoft YaHei', 'Arial', 'Helvetica', 'sans-serif'],
        'title_size': 12,
        'label_size': 10,
        'tick_size': 8,
        'legend_size': 8,
        'dpi': 300
    },
    'neurips': {
        'name': 'NeurIPS',
        'single_column': (3.5, 2.6),   # 89mm width
        'double_column': (7.2, 4.2),   # 183mm width
        'font_family': ['SimHei', 'Arial', 'sans-serif'],  # Chinese support first
        'title_size': 11,
        'label_size': 9,
        'tick_size': 8,
        'legend_size': 8,
        'dpi': 300
    },
    'cvpr': {
        'name': 'CVPR',
        'single_column': (3.5, 2.6),   # 89mm width
        'double_column': (7.2, 4.2),   # 183mm width
        'font_family': ['SimHei', 'Arial', 'sans-serif'],  # Chinese support first
        'title_size': 11,
        'label_size': 9,
        'tick_size': 8,
        'legend_size': 8,
        'dpi': 300
    },
    'science': {
        'name': 'Science',
        'single_column': (3.35, 2.5),  # 85mm width
        'double_column': (7.08, 4.0),  # 180mm width
        'font_family': ['SimHei', 'Microsoft YaHei', 'Arial', 'Helvetica', 'sans-serif'],
        'title_size': 12,
        'label_size': 10,
        'tick_size': 8,
        'legend_size': 8,
        'dpi': 300
    },
    'ieee': {
        'name': 'IEEE',
        'single_column': (3.5, 2.6),   # 89mm width
        'double_column': (7.2, 4.2),   # 183mm width
        'font_family': ['SimHei', 'Arial', 'sans-serif'],  # Chinese support first
        'title_size': 10,
        'label_size': 9,
        'tick_size': 8,
        'legend_size': 8,
        'dpi': 300
    }
}

# --- DeepSeek API 调用封装 ---
def call_deepseek_api(prompt: str, is_json_mode: bool = False) -> Optional[str]:
    """调用 DeepSeek API 的通用函数"""
    if not DEEPSEEK_API_KEY:
        raise ValueError("请在 .env 文件中设置 DEEPSEEK_API_KEY 环境变量")

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
    }
    if is_json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        result_content = response.json()['choices'][0]['message']['content']
        return result_content
    except requests.exceptions.RequestException as e:
        print(f"调用 DeepSeek API 时发生网络错误: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"解析 DeepSeek API 响应时出错: {e}, 响应内容: {response.text}")
        return None

# --- 核心功能函数 ---

def translate_texts(texts_to_translate: Dict[str, str]) -> Optional[Dict[str, str]]:
    """使用 DeepSeek API 批量翻译文本。"""
    prompt = f"""
    你是一个精准的翻译引擎。请将以下JSON对象中的英文文本翻译成简洁、专业、地道的中文。
    请确保JSON的key保持不变，只翻译value中的字符串。
    请以JSON格式返回结果，不要添加任何额外的解释或说明。

    输入:
    {json.dumps(texts_to_translate, indent=2, ensure_ascii=False)}

    输出:
    """
    
    translated_json_str = call_deepseek_api(prompt, is_json_mode=True)
    if translated_json_str:
        try:
            return json.loads(translated_json_str)
        except json.JSONDecodeError as e:
            print(f"无法解析翻译返回的JSON: {e}")
            print(f"原始字符串: {translated_json_str}")
            return None
    return None

def refactor_and_style_code(code_content: str, style_options: Dict[str, Any]) -> Optional[str]:
    """
    使用 DeepSeek API 对代码进行美化、重构和学术风格应用。
    style_options 是一个包含用户选择的字典。
    """
    
    # --- 根据用户选项动态构建 Prompt 的一部分 ---
    instructions = []
    
    # 1. 布局美化指令
    if style_options.get('beautify_layout'):
        instructions.append(
            "2. **优化子图布局**: 如果代码创建了多个子图（subplots）且它们是垂直或水平排列的（例如 4x1 或 1x4），请将它们重构为更均衡的网格布局（例如 2x2）。目的是让整体视觉更紧凑、专业。"
        )
        
    # 2. 学术风格指令
    if style_options.get('enabled'):
        paper_format = style_options.get('paper_format', 'nature')
        layout = style_options.get('layout', 'single')
        
        format_config = PAPER_FORMATS.get(paper_format, PAPER_FORMATS['nature'])
        
        if layout == 'single':
            figsize = format_config['single_column']
            figsize_str = f"{figsize} # {format_config['name']} 单栏宽度"
        else:
            figsize = format_config['double_column']
            figsize_str = f"{figsize} # {format_config['name']} 双栏宽度"

        academic_instructions = f"""
3. **应用 {format_config['name']} 学术出版风格**:
   - **字体与字号**: 注入 `plt.rcParams.update()` 来全局设置字体。使用支持中文的字体（如 SimHei, Microsoft YaHei）。具体字号 (pt) 要求如下:
     - 图表标题 (Title): {format_config['title_size']} pt
     - 坐标轴标签 (Axis Labels): {format_config['label_size']} pt
     - 坐标轴刻度 (Tick Labels): {format_config['tick_size']} pt
     - 图例 (Legend): {format_config['legend_size']} pt
   - **图表尺寸**: 找到创建图表的代码行（如 `plt.figure()` 或 `plt.subplots()`），将其 `figsize` 参数修改或设置为 `{figsize_str}`。
   - **分辨率**: 设置图像分辨率为 {format_config['dpi']} DPI
   - **重要**: 确保字体设置不会覆盖已有的中文支持配置。如果代码中已有中文字体设置，请保留它们。
"""
        instructions.append(academic_instructions)

    # 3. 自定义模式指令
    if style_options.get('custom_mode'):
        custom_params = style_options.get('custom_params', {})
        custom_instructions = "4. **应用自定义样式**:\n"
        
        for param, value in custom_params.items():
            if param == 'font_size':
                custom_instructions += f"   - 设置全局字体大小为 {value} pt\n"
            elif param == 'title_size':
                custom_instructions += f"   - 设置标题字体大小为 {value} pt\n"
            elif param == 'fig_width':
                custom_instructions += f"   - 设置图表宽度为 {value} 英寸\n"
            elif param == 'fig_height':
                custom_instructions += f"   - 设置图表高度为 {value} 英寸\n"
            elif param == 'dpi':
                custom_instructions += f"   - 设置图像分辨率为 {value} DPI\n"
        
        instructions.append(custom_instructions)

    # 4. 矢量图保存指令
    vector_format = style_options.get('vector_format')
    if vector_format:
        filename_base = style_options.get('output_filename_base', 'figure')
        output_filename = f"{filename_base}.{vector_format}"
        save_instruction = f"""
5. **保存为矢量图**: 在 `plt.show()` 命令之前，必须插入一行代码来将图表保存为矢量图。代码应为: `plt.savefig('{output_filename}', bbox_inches='tight', dpi={style_options.get('dpi', 300)})`。
"""
        instructions.append(save_instruction)

    # --- 组合成最终的 Prompt ---
    # 如果没有任何指令，则直接返回
    if not instructions:
        return None
        
    prompt = f"""
你是一位顶级的 Python 数据可视化专家，尤其擅长为学术期刊准备符合出版要求的高质量图表。

你的任务是：接收一段 Python 绘图脚本，并根据下面的具体要求对其进行重构和优化。

**核心要求**:
1. **保留原始意图**: 必须完整保留原始代码的数据处理逻辑、绘图类型（如折线图、柱状图）以及所有中文标签和注释。你的工作是美化和规范化，而不是改变图表的核心内容。
{"\n".join(instructions)}

**输出规则**:
- **纯代码输出**: 你的回复必须且只能是经过重构和优化后的完整 Python 代码。
- **不要包含任何解释**、前言、结语或任何格式化标记，例如 ```python ... ```。
- 确保代码可以直接运行。

**这是需要你处理的原始 Python 脚本**:

```python
{code_content}
```
"""
    
    print("正在请求 AI 进行代码重构与风格美化...")
    refactored_code = call_deepseek_api(prompt)
    
    # 基本的验证，防止 API 返回非代码内容
    if refactored_code and ('import' in refactored_code or 'plt' in refactored_code):
        return refactored_code
    else:
        print(f"AI 返回内容似乎不是有效的代码，已忽略。返回内容: {refactored_code[:200]}...")
        return None

def inject_chinese_font_support(code_lines: List[str]) -> List[str]:
    """在代码中注入 Matplotlib 中文支持的设置。"""
    matplotlib_import_index = -1
    for i, line in enumerate(code_lines):
        if re.search(r'import\s+matplotlib\.pyplot\s+as\s+plt', line):
            matplotlib_import_index = i
            break
            
    if matplotlib_import_index != -1:
        font_config = [
            "\n# --- 解决中文显示问题 ---",
            "plt.rcParams['font.sans-serif'] = ['SimHei']",
            "plt.rcParams['axes.unicode_minus'] = False",
            "# --------------------------\n"
        ]
        for i, line in enumerate(font_config):
            code_lines.insert(matplotlib_import_index + 1 + i, line)
    else:
        print("警告：未找到 'import matplotlib.pyplot as plt'，无法自动注入中文支持代码。")
        
    return code_lines

def create_academic_style_code_block(options: Dict[str, Any]) -> str:
    """
    根据用户选项生成 Matplotlib rcParams 的 Python 代码块。
    优化字体配置逻辑，避免中文显示冲突。
    """
    paper_format = options.get('paper_format', 'nature')
    layout = options.get('layout', 'single')
    
    format_config = PAPER_FORMATS.get(paper_format, PAPER_FORMATS['nature'])
    
    if layout == 'single':
        figsize = format_config['single_column']
        figsize_str = f"{figsize} # {format_config['name']} 单栏宽度"
    else:
        figsize = format_config['double_column']
        figsize_str = f"{figsize} # {format_config['name']} 双栏宽度"
    
    # 检查是否需要中文支持（如果原始代码包含中文字符）
    # 这里我们假设如果用户选择了学术模式，可能需要中文支持
    # 在实际应用中，可以更精确地检测是否需要中文支持
    needs_chinese_support = True  # 保守起见，默认启用中文支持
    
    # 构建字体配置，优先考虑中文支持
    if needs_chinese_support:
        # 对于需要中文支持的场景，优先使用支持中文的字体
        font_family_config = format_config['font_family']
        # 确保字体族配置不会覆盖中文支持
        font_config = f"'font.family': 'sans-serif',\n    'font.sans-serif': {font_family_config},"
    else:
        # 对于纯英文场景，使用标准配置
        font_config = f"'font.family': 'sans-serif',\n    'font.sans-serif': {format_config['font_family']},"
        
    style_settings = f"""
# --- {format_config['name']} 学术风格注入 ---
# 设置字体和字号以符合出版标准
plt.rcParams.update({{
    {font_config}
    'font.size': {format_config['label_size']},          # 全局基础字号
    'axes.titlesize': {format_config['title_size']},     # 图表标题字号
    'axes.labelsize': {format_config['label_size']},     # 坐标轴标签字号
    'xtick.labelsize': {format_config['tick_size']},     # X轴刻度字号
    'ytick.labelsize': {format_config['tick_size']},     # Y轴刻度字号
    'legend.fontsize': {format_config['legend_size']},   # 图例字号
    'figure.dpi': {format_config['dpi']},                # 图像分辨率
    'figure.figsize': {figsize_str}   # 根据单/双栏设置图像大小
}})
# --------------------
"""
    return style_settings

def inject_savefig_before_show(code_lines: List[str], vector_format: Optional[str], original_filepath: str, dpi: int = 300) -> List[str]:
    """
    在代码中找到 plt.show() 并在其之前插入保存矢量图的命令。
    使用相对路径保存图像，确保用户可以在任何目录运行脚本。
    """
    if not vector_format:
        return code_lines

    show_line_index = -1
    for i, line in enumerate(code_lines):
        # 匹配 plt.show()，允许前面有空格
        if re.search(r'^\s*plt\.show\(\)', line):
            show_line_index = i
            break
            
    if show_line_index != -1:
        # 获取原始文件名（不含路径和扩展名）
        original_filename = os.path.basename(original_filepath)
        base, _ = os.path.splitext(original_filename)
        # 生成相对路径文件名，例如 001_figure.pdf
        output_filename = f"{base}_figure.{vector_format}"
        
        savefig_line = f"\n# 保存为矢量图格式\nplt.savefig('{output_filename}', bbox_inches='tight', dpi={dpi})\n"
        
        # 在 plt.show() 之前插入保存命令
        code_lines.insert(show_line_index, savefig_line)
        print(f"已注入保存矢量图的代码，将保存至相对路径: {output_filename}")
    else:
        print("警告：未找到 'plt.show()'，无法自动注入保存矢量图的代码。")
        
    return code_lines

def process_python_file_streaming(filepath: str, beautify: bool = False, academic_options: Optional[Dict[str, Any]] = None):
    """
    处理单个Python文件：翻译、风格化，并应用备用注入方案。
    返回一个生成器，用于流式传输处理状态。
    """
    yield "开始处理文件..."
    
    if academic_options is None:
        academic_options = {'enabled': False}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_code = f.read()
        yield "文件读取成功"
    except Exception as e:
        yield f"读取文件失败: {e}"
        return

    try:
        tree = ast.parse(original_code)
        yield "代码语法解析成功"
    except SyntaxError as e:
        yield f"Python 代码语法错误，无法解析: {e}"
        return

    texts_to_translate = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr in TARGET_PLOT_FUNCTIONS:
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.strip():
                    texts_to_translate[arg.value] = arg.value
            for kw in node.keywords:
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str) and kw.value.value.strip():
                    texts_to_translate[kw.value.value] = kw.value.value
    code_lines = original_code.split('\n')
    for line in code_lines:
        line_stripped = line.strip()
        if line_stripped.startswith('#'):
            comment_text = line_stripped[1:].strip()
            if comment_text and re.search('[a-zA-Z]', comment_text):
                texts_to_translate[comment_text] = comment_text
    
    translated_code = original_code
    if texts_to_translate:
        yield f"找到 {len(texts_to_translate)} 条需要翻译的文本，正在请求翻译..."
        translation_map = translate_texts(texts_to_translate)
        if not translation_map:
            yield "翻译失败，跳过翻译步骤。"
        else:
            yield "翻译完成，开始重建代码..."
            sorted_eng_texts = sorted(translation_map.keys(), key=len, reverse=True)
            modified_code = original_code
            for eng_text in sorted_eng_texts:
                zh_text = translation_map.get(eng_text, eng_text)
                modified_code = modified_code.replace(f'"{eng_text}"', f'"{zh_text}"')
                modified_code = modified_code.replace(f"'{eng_text}'", f"'{zh_text}'")
                temp_lines = []
                for line in modified_code.split('\n'):
                    stripped_line = line.strip()
                    if stripped_line.startswith(f'# {eng_text}') or stripped_line.startswith(f'#{eng_text}'):
                        temp_lines.append(line.replace(eng_text, zh_text))
                    else:
                        temp_lines.append(line)
                modified_code = '\n'.join(temp_lines)
            translated_code = modified_code
    else:
        yield "未找到需要翻译的英文文本。"

    modified_code_lines = translated_code.split('\n')
    if not any("plt.rcParams['font.sans-serif']" in line for line in modified_code_lines):
        inject_chinese_font_support(modified_code_lines)
        yield "已注入中文字体支持"
    
    final_code_with_font_support = '\n'.join(modified_code_lines)
    final_code = final_code_with_font_support
    
    refactored_result = None
    if beautify or (academic_options and academic_options.get('enabled')):
        base, _ = os.path.splitext(filepath)
        output_filename_base = f"{base}_figure"

        style_options = academic_options if academic_options else {}
        style_options['beautify_layout'] = beautify
        style_options['output_filename_base'] = output_filename_base
        
        yield "开始AI代码重构与风格美化..."
        refactored_result = refactor_and_style_code(final_code_with_font_support, style_options)
        
        if refactored_result:
            final_code = refactored_result
            yield "AI 代码重构与风格美化成功"
        else:
            yield "AI 代码重构失败或跳过"

    if not refactored_result and academic_options and academic_options.get('enabled'):
        yield "正在执行备用方案：直接注入学术风格代码..."
        code_lines = final_code.split('\n')
        
        matplotlib_import_index = -1
        for i, line in enumerate(code_lines):
            if re.search(r'import\s+matplotlib\.pyplot\s+as\s+plt', line):
                matplotlib_import_index = i
                break
        
        if matplotlib_import_index != -1:
            style_code_block = create_academic_style_code_block(academic_options)
            code_lines.insert(matplotlib_import_index + 1, style_code_block)
            yield "已注入字体、字号和尺寸设置"
        else:
            yield "警告：未找到 matplotlib 导入语句，无法注入样式代码"

        vector_format = academic_options.get('vector_format')
        dpi = academic_options.get('dpi', 300)
        code_lines = inject_savefig_before_show(code_lines, vector_format, filepath, dpi)
        
        final_code = '\n'.join(code_lines)

    base, ext = os.path.splitext(filepath)
    new_filepath = f"{base}_zh_revision{ext}"
    
    try:
        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(final_code)
        yield f"处理完成！修改后的文件已保存至: {new_filepath}"
        yield f"SUCCESS:{new_filepath}"
    except Exception as e:
        yield f"保存文件失败: {e}"

def process_python_file_streaming(filepath: str, output_folder: str, beautify: bool = False, academic_options: Optional[Dict[str, Any]] = None):
    """
    处理单个Python文件：翻译、风格化，并应用备用注入方案。
    返回一个生成器，用于流式传输处理状态。
    """
    yield "开始处理文件..."
    
    if academic_options is None:
        academic_options = {'enabled': False}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_code = f.read()
        yield "文件读取成功"
    except Exception as e:
        yield f"读取文件失败: {e}"
        return

    try:
        tree = ast.parse(original_code)
    except SyntaxError as e:
        yield f"Python 代码语法错误，无法解析: {e}"
        return

    texts_to_translate = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr in TARGET_PLOT_FUNCTIONS:
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.strip():
                    texts_to_translate[arg.value] = arg.value
            for kw in node.keywords:
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str) and kw.value.value.strip():
                    texts_to_translate[kw.value.value] = kw.value.value
    code_lines = original_code.split('\n')
    for line in code_lines:
        line_stripped = line.strip()
        if line_stripped.startswith('#'):
            comment_text = line_stripped[1:].strip()
            if comment_text and re.search('[a-zA-Z]', comment_text):
                texts_to_translate[comment_text] = comment_text
    
    translated_code = original_code
    if texts_to_translate:
        yield f"找到 {len(texts_to_translate)} 条需要翻译的文本，正在请求翻译..."
        translation_map = translate_texts(texts_to_translate)
        if not translation_map:
            yield "翻译失败，跳过翻译步骤。"
        else:
            yield "翻译完成，开始重建代码..."
            sorted_eng_texts = sorted(translation_map.keys(), key=len, reverse=True)
            modified_code = original_code
            for eng_text in sorted_eng_texts:
                zh_text = translation_map.get(eng_text, eng_text)
                modified_code = modified_code.replace(f'"{eng_text}"', f'"{zh_text}"')
                modified_code = modified_code.replace(f"'{eng_text}'", f"'{zh_text}'")
                temp_lines = []
                for line in modified_code.split('\n'):
                    stripped_line = line.strip()
                    if stripped_line.startswith(f'# {eng_text}') or stripped_line.startswith(f'#{eng_text}'):
                        temp_lines.append(line.replace(eng_text, zh_text))
                    else:
                        temp_lines.append(line)
                modified_code = '\n'.join(temp_lines)
            translated_code = modified_code
    else:
        yield "未找到需要翻译的英文文本。"

    modified_code_lines = translated_code.split('\n')
    if not any("plt.rcParams['font.sans-serif']" in line for line in modified_code_lines):
        inject_chinese_font_support(modified_code_lines)
        yield "已注入中文字体支持"
    
    final_code_with_font_support = '\n'.join(modified_code_lines)
    final_code = final_code_with_font_support
    
    refactored_result = None
    if beautify or (academic_options and academic_options.get('enabled')):
        base, _ = os.path.splitext(filepath)
        output_filename_base = f"{base}_figure"

        style_options = academic_options if academic_options else {}
        style_options['beautify_layout'] = beautify
        style_options['output_filename_base'] = output_filename_base
        
        yield "开始AI代码重构与风格美化..."
        refactored_result = refactor_and_style_code(final_code_with_font_support, style_options)
        
        if refactored_result:
            final_code = refactored_result
            yield "AI 代码重构与风格美化成功。"
        else:
            yield "AI 代码重构失败或跳过。"

    if not refactored_result and academic_options and academic_options.get('enabled'):
        yield "正在执行备用方案：直接注入学术风格代码..."
        code_lines = final_code.split('\n')
        
        matplotlib_import_index = -1
        for i, line in enumerate(code_lines):
            if re.search(r'import\s+matplotlib\.pyplot\s+as\s+plt', line):
                matplotlib_import_index = i
                break
        
        if matplotlib_import_index != -1:
            style_code_block = create_academic_style_code_block(academic_options)
            code_lines.insert(matplotlib_import_index + 1, style_code_block)
            yield "已注入字体、字号和尺寸设置。"
        else:
            yield "警告：未找到 matplotlib 导入语句，无法注入样式代码。"

        vector_format = academic_options.get('vector_format')
        dpi = academic_options.get('dpi', 300)
        code_lines = inject_savefig_before_show(code_lines, vector_format, filepath, dpi)
        
        final_code = '\n'.join(code_lines)

    # 使用os.path.basename获取纯文件名，避免路径问题
    original_filename = os.path.basename(filepath)
    base, ext = os.path.splitext(original_filename)

    # 构建指向正确输出目录的完整路径
    new_filename = f"{base}_zh_revision{ext}"
    new_filepath = os.path.join(output_folder, new_filename)
    
    try:
        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(final_code)
        yield f"处理完成！修改后的文件已保存至: {new_filepath}"
        yield f"SUCCESS:{new_filename}"
    except Exception as e:
        yield f"保存文件失败: {e}"

# --- 主程序入口 ---
if __name__ == '__main__':
    # 获取用户输入
    file_to_process = input("请输入要处理的 Python 文件路径 (例如: 001.py): ")

    if not os.path.exists(file_to_process):
        print(f"错误：文件 '{file_to_process}' 不存在。")
    else:
        # 询问是否启用学术风格
        academic_mode_choice = input("是否启用学术论文风格优化？[y/N]: ").lower()
        academic_options = {'enabled': False}

        if academic_mode_choice == 'y':
            academic_options['enabled'] = True
            
            # 选择论文格式
            print("\n请选择论文格式:")
            for i, (key, config) in enumerate(PAPER_FORMATS.items(), 1):
                print(f"  [{i}] {config['name']}")
            format_choice = input("请输入选项 [1]: ")
            format_keys = list(PAPER_FORMATS.keys())
            academic_options['paper_format'] = format_keys[int(format_choice) - 1] if format_choice.isdigit() and 1 <= int(format_choice) <= len(format_keys) else 'nature'
            
            # 询问布局和尺寸
            print("\n请选择图表最终尺寸 (通常对应期刊栏宽):")
            print("  [1] 单栏")
            print("  [2] 双栏")
            layout_choice = input("请输入选项 [1]: ")
            academic_options['layout'] = 'double' if layout_choice == '2' else 'single'

            # 询问矢量图保存格式
            print("\n请选择是否保存为矢量图格式 (推荐用于出版):")
            print("  [1] PDF")
            print("  [2] SVG")
            print("  [3] EPS")
            vector_format_choice = input("请输入选项 (直接回车则不保存): ")
            format_map = {'1': 'pdf', '2': 'svg', '3': 'eps'}
            academic_options['vector_format'] = format_map.get(vector_format_choice, None)
            
            # 在学术模式下，默认开启布局美化
            should_beautify = True
            print("-" * 20)
        else:
            # 如果不使用学术模式，则沿用旧的提问方式
            beautify_choice = input("是否需要进行AI布局美化？(这是一个实验性功能) [y/N]: ").lower()
            should_beautify = beautify_choice == 'y'
        
        process_python_file(
            file_to_process, 
            beautify=should_beautify, 
            academic_options=academic_options
        )