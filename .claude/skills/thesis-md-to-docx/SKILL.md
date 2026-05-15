---
name: thesis-md-to-docx
description: 将本科毕业论文 Markdown 严格转换为 Word .docx 的专用 skill。用户要求把 .md、论文 Markdown、毕业论文草稿、thesis.md 转成 docx/Word/毕业论文模板格式时必须使用，尤其是提到“毕业论文模板.docx”“格式规范.docx”“广东工业大学”“按模板排版”“论文 docx”“Markdown 转 Word”等场景。使用时必须调用 markdown-to-docx skill 的 pandoc/template 转换流程，并以项目中的 模板/毕业论文模板.docx 作为 Word 参考模板、模板/格式规范.docx 作为格式规范依据；转换后必须运行校验并修复明显格式问题。
---

# 毕业论文 Markdown 转 DOCX

把已经写好的 `.md` 毕业论文转换为符合本科毕业论文模板与格式规范的 `.docx` 文件。该 skill 不负责重新写论文正文，重点是转换、套模板、格式校验和必要的 Markdown 预处理。

## 固定模板与规范

默认使用当前项目中的：

- Word 模板：`模板/毕业论文模板.docx`
- 格式规范：`模板/格式规范.docx`
- 转换能力：调用 `markdown-to-docx` skill

除非用户明确指定其他模板，不要换用其他 Word 模板。若模板文件缺失，先提示用户补充，不要用普通空白 Word 文档冒充毕业论文模板。

## 启动流程

1. 确认输入 Markdown 文件路径。
   - 如果用户提供单个 `.md` 文件，转换该文件。
   - 如果用户提供目录，询问是转换目录下所有顶层 `.md`，还是只转换某一个文件。
2. 检查模板文件是否存在：
   - `模板/毕业论文模板.docx`
   - `模板/格式规范.docx`
3. 询问用户是否需要重新扫描 `模板/格式规范.docx`。
   - 如果用户选择重新扫描：提取规范重点后再转换。
   - 如果用户选择不扫描：使用本 skill 的规范摘要。
4. 调用 `markdown-to-docx` skill 的模板转换流程，使用 `毕业论文模板.docx` 作为 reference/template。
5. 转换后运行 `markdown-to-docx` 的 post-check 校验。
6. 如果校验发现明显问题，优先修复 Markdown 或转换参数后重新生成；不要直接交付未检查的 docx。
7. 输出最终 `.docx` 路径，并简要说明使用了哪个 Markdown、哪个模板和校验结果。

## 与 markdown-to-docx skill 的协作

转换时必须遵循 `markdown-to-docx` skill 的流程：

1. 确认 `pandoc` 可用。
2. 使用其脚本进行模板化转换，而不是手写临时转换流程。
3. 对有 Word 模板的任务，优先使用：

```bash
SKILL_DIR="<markdown-to-docx skill 路径>"
"$SKILL_DIR/scripts/render_markdown_with_dotx.sh" \
  "<source-md>" \
  "<output-docx>" \
  "模板/毕业论文模板.docx" \
  "<论文题目或文档标题>" \
  "<resource-root>"
```

4. 转换后运行：

```bash
python3 "$SKILL_DIR/scripts/validate_captions.py" post "<output-docx>"
```

5. 如果 `render_markdown_with_dotx.sh` 无法处理 `.docx` 模板或环境缺依赖，再退回到 pandoc reference-doc 工作流：

```bash
pandoc "<source-md>" \
  -o "<output-docx>" \
  --reference-doc="模板/毕业论文模板.docx" \
  --resource-path="<resource-root>"
```

退回方案也必须说明原因，并尽可能运行可用的后置检查。

## 格式规范摘要

转换输出应尽量满足 `格式规范.docx` 中的要求：

- 页面：A4；上边距 30mm，下边距 25mm，左边距 30mm，右边距 20mm；1.5 倍行距。
- 题目：二号黑体加粗居中。
- 章标题：三号黑体加粗。
- 节标题：小四号黑体加粗。
- 条标题：小四号黑体。
- 正文：小四号宋体。
- 数字和字母：Times New Roman。
- 摘要：中文摘要约 400 字，关键词 3-5 个；英文摘要与中文摘要一致。
- 目录：理工、社科类按 `1`、`1.1`、`1.1.1` 三级标题。
- 图题：图下方，按章编号，如 `图2.1`。
- 表题：表上方，按章编号，如 `表3.1`。
- 公式：按章编号，如 `(1.1)`。
- 参考文献：按 GB/T 7714—2015。
- 附录：用 `附录A`、`附录B` 编号，附录中图表公式独立编号。

Markdown 无法表达的精细排版，应尽量通过 Word 模板和后处理完成；不要在 Markdown 中加入大量 Word 专用说明文字。

## Markdown 预处理要求

转换前检查并必要时提醒用户修正：

- 标题层级应清晰，建议仅一个文档主标题，章节用 `# 1 绪论` 或按模板需要映射。
- 摘要、Abstract、目录、正文、参考文献、致谢、附录应结构完整。
- 图表应有规范题注：`图X.Y 图名`、`表X.Y 表名`。
- 参考文献条目不要使用虚构信息。
- 图片路径应相对 Markdown 文件或 resource-root 可访问。
- 代码块、目录树、长表格可能影响 Word 排版，必要时提示用户人工检查。

## 输出文件规则

- 默认输出到源 Markdown 同目录。
- 默认文件名与源 Markdown 同名，例如 `thesis.md` → `thesis.docx`。
- 如果目标文件已存在，不要无提示覆盖；使用带后缀的新文件名，或询问用户是否覆盖。
- 转换成功后只报告必要信息：输出路径、模板路径、校验是否通过、是否存在需要人工复查的项。

## 常见问题处理

- **缺少 pandoc**：提示用户安装 pandoc，或说明无法继续转换。
- **模板缺失**：提示缺少 `模板/毕业论文模板.docx` 或 `模板/格式规范.docx`。
- **图片丢失**：检查 `--resource-path`，优先把项目根目录、Markdown 所在目录和资源目录都纳入。
- **图表题注缺失**：使用 markdown-to-docx 的 caption 修复/校验能力，必要时要求用户补充图题表题。
- **校验失败**：说明失败项，修复后重新生成；不能修复时明确列为“需人工复查”。

## 交互模板

```text
我会把该 Markdown 按 `模板/毕业论文模板.docx` 和 `模板/格式规范.docx` 转为 Word。是否需要我重新扫描格式规范？另外请确认输出目录是否使用 Markdown 同目录。
```

```text
转换完成：
- 源文件：...
- 输出 DOCX：...
- 使用模板：模板/毕业论文模板.docx
- 格式规范：模板/格式规范.docx
- 校验结果：...
```
