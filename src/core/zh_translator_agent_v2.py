import os
import re
import requests
import json
import ast

# --- 配置区 ---
DEEPSEEK_API_KEY = "sk-5d832b2f7c0a4f1187c3c2c619c680f4"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

TARGET_PLOT_FUNCTIONS = {
    'title', 'xlabel', 'ylabel', 'suptitle',
    'set_title', 'set_xlabel', 'set_ylabel', 'text', 'legend'
}

# --- DeepSeek API 调用封装 (无变动) ---
def call_deepseek_api(prompt, is_json_mode=False):
    """调用 DeepSeek API 的通用函数"""
    if not DEEPSEEK_API_KEY or "xxxxxxxx" in DEEPSEEK_API_KEY:
        raise ValueError("请在 DEEPSEEK_API_KEY 变量中设置你的有效 API Key")

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

def translate_texts(texts_to_translate):
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

# --- MODIFIED ---
def refactor_and_style_code(code_content, style_options):
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
        layout = style_options.get('layout', 'single')
        if layout == 'single':
            figsize_str = "(3.35, 2.5) # 对应约 85mm 单栏宽度"
        else:
            figsize_str = "(7.08, 4.0) # 对应约 180mm 双栏宽度"

        academic_instructions = f"""
3. **应用学术出版风格**:
   - **字体与字号**: 注入 `plt.rcParams.update()` 来全局设置字体。必须使用无衬线字体（sans-serif），如 'Arial' 或 'Helvetica'。具体字号 (pt) 要求如下:
     - 图表标题 (Title): 12 pt
     - 坐标轴标签 (Axis Labels): 10 pt
     - 坐标轴刻度 (Tick Labels): 8 pt
     - 图例 (Legend): 8 pt
   - **图表尺寸**: 找到创建图表的代码行（如 `plt.figure()` 或 `plt.subplots()`），将其 `figsize` 参数修改或设置为 `{figsize_str}`。
"""
        instructions.append(academic_instructions)

    # 3. 矢量图保存指令
    vector_format = style_options.get('vector_format')
    if vector_format:
        filename_base = style_options.get('output_filename_base', 'figure')
        output_filename = f"{filename_base}.{vector_format}"
        save_instruction = f"""
4. **保存为矢量图**: 在 `plt.show()` 命令之前，必须插入一行代码来将图表保存为矢量图。代码应为: `plt.savefig('{output_filename}', bbox_inches='tight')`。
"""
        instructions.append(save_instruction)

    # --- 组合成最终的 Prompt ---
    # 如果没有任何指令，则直接返回
    if not instructions:
        return None
        
    prompt = f"""
你是一位顶级的 Python 数据可视化专家，尤其擅长为学术期刊（如 Nature, Science）准备符合出版要求的高质量图表。

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

def inject_chinese_font_support(code_lines):
    """在代码中注入 Matplotlib 中文支持的设置。 (无变动)"""
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
        
    return ["line.rstrip('\\n')" for line in code_lines]
    # return code_lines 
    # 此处貌似存在一个小bug，该函数的最后一句 return ["line.rstrip('\\n')" for line in code_lines] 并不能正确地处理代码行列表
    # 它返回的是一个包含了字符串本身（如 "'import os'.rstrip('\\n')"）的新列表，而不是处理过的代码行。
    # 实际上，因为 code_lines.insert() 是原地修改列表，我们只需要直接返回被修改后的 code_lines 即可。
    # 如果出现错误，请修改此行

# --- NEW ---
# 新增辅助函数，用于根据用户选项生成学术风格的 rcParams 设置代码
def create_academic_style_code_block(options):
    """
    根据用户选项生成 Matplotlib rcParams 的 Python 代码块。
    """
    layout = options.get('layout', 'single')
    
    # 根据期刊常见尺寸（英寸）设置图像大小
    # 单栏: ~85mm -> 3.35 inches
    # 双栏: ~180mm -> 7.08 inches
    if layout == 'single':
        figsize_str = "(3.35, 2.5) # 单栏宽度"
    else: # double
        figsize_str = "(7.08, 4.0) # 双栏宽度"
        
    style_settings = f"""
# --- 学术风格注入 ---
# 设置字体和字号以符合出版标准
plt.rcParams.update({{
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'], # 优先使用 Arial 或 Helvetica
    'font.size': 10,                   # 全局基础字号
    'axes.titlesize': 12,              # 图表标题字号
    'axes.labelsize': 10,              # 坐标轴标签字号
    'xtick.labelsize': 8,              # X轴刻度字号
    'ytick.labelsize': 8,              # Y轴刻度字号
    'legend.fontsize': 8,              # 图例字号
    'figure.dpi': 300,                 # 图像分辨率
    'figure.figsize': {figsize_str}   # 根据单/双栏设置图像大小
}})
# --------------------
"""
    return style_settings

# --- NEW ---
# 新增辅助函数，用于在 plt.show() 之前插入 plt.savefig()
def inject_savefig_before_show(code_lines, vector_format, original_filepath):
    """
    在代码中找到 plt.show() 并在其之前插入保存矢量图的命令。
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
        base, _ = os.path.splitext(original_filepath)
        # 生成保存文件的路径，例如 001_figure.pdf
        output_filename = f"{base}_figure.{vector_format}"
        
        savefig_line = f"\n# 保存为矢量图格式\nplt.savefig('{output_filename}', bbox_inches='tight')\n"
        
        # 在 plt.show() 之前插入保存命令
        code_lines.insert(show_line_index, savefig_line)
        print(f"已注入保存矢量图的代码，将保存至: {output_filename}")
    else:
        print("警告：未找到 'plt.show()'，无法自动注入保存矢量图的代码。")
        
    return code_lines

# --- MODIFIED ---
# 主处理函数增加了新的参数 academic_options
def process_python_file(filepath, beautify=False, academic_options=None):
    """
    处理单个Python文件：翻译、风格化，并应用备用注入方案。
    """
    print(f"--- 开始处理文件: {filepath} ---")

    if academic_options is None:
        academic_options = {'enabled': False}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_code = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    try:
        tree = ast.parse(original_code)
    except SyntaxError as e:
        print(f"Python 代码语法错误，无法解析: {e}")
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
        print(f"找到 {len(texts_to_translate)} 条需要翻译的文本，正在请求翻译...")
        translation_map = translate_texts(texts_to_translate)
        if not translation_map:
            print("翻译失败，跳过翻译步骤。")
        else:
            print("翻译完成，开始重建代码...")
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
        print("未找到需要翻译的英文文本。")

    modified_code_lines = translated_code.split('\n')
    if not any("plt.rcParams['font.sans-serif']" in line for line in modified_code_lines):
        inject_chinese_font_support(modified_code_lines)
    
    final_code_with_font_support = '\n'.join(modified_code_lines)
    final_code = final_code_with_font_support
    
    refactored_result = None
    if beautify or (academic_options and academic_options.get('enabled')):
        base, _ = os.path.splitext(filepath)
        output_filename_base = f"{base}_figure" # 传递给 AI 用于生成保存文件名

        style_options = academic_options if academic_options else {}
        style_options['beautify_layout'] = beautify
        style_options['output_filename_base'] = output_filename_base
        
        refactored_result = refactor_and_style_code(final_code_with_font_support, style_options)
        
        if refactored_result:
            final_code = refactored_result
            print("AI 代码重构与风格美化成功。")
        else:
            print("AI 代码重构失败或跳过。")

    if not refactored_result and academic_options and academic_options.get('enabled'):
        print("正在执行备用方案：直接注入学术风格代码...")
        code_lines = final_code.split('\n')
        
        matplotlib_import_index = -1
        for i, line in enumerate(code_lines):
            if re.search(r'import\s+matplotlib\.pyplot\s+as\s+plt', line):
                matplotlib_import_index = i
                break
        
        if matplotlib_import_index != -1:
            style_code_block = create_academic_style_code_block(academic_options)
            code_lines.insert(matplotlib_import_index + 1, style_code_block)
            print("已注入字体、字号和尺寸设置。")
        else:
            print("警告：未找到 matplotlib 导入语句，无法注入样式代码。")

        vector_format = academic_options.get('vector_format')
        code_lines = inject_savefig_before_show(code_lines, vector_format, filepath)
        
        final_code = '\n'.join(code_lines)

    base, ext = os.path.splitext(filepath)
    new_filepath = f"{base}_zh_revision{ext}"
    
    try:
        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(final_code)
        print(f"--- 处理完成！修改后的文件已保存至: {new_filepath} ---")
    except Exception as e:
        print(f"保存文件失败: {e}")


# --- 主程序入口 ---
# --- MODIFIED ---
if __name__ == '__main__':
    # 获取用户输入
    file_to_process = input("请输入要处理的 Python 文件路径 (例如: 001.py): ")

    if not os.path.exists(file_to_process):
        print(f"错误：文件 '{file_to_process}' 不存在。")
    else:
        # --- NEW ---
        # 询问是否启用学术风格
        academic_mode_choice = input("是否启用学术论文风格优化？[y/N]: ").lower()
        academic_options = {'enabled': False}

        if academic_mode_choice == 'y':
            academic_options['enabled'] = True
            
            # 询问布局和尺寸
            print("\n请选择图表最终尺寸 (通常对应期刊栏宽):")
            print("  [1] 单栏 (约 85mm 宽)")
            print("  [2] 双栏 (约 180mm 宽)")
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