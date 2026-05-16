---
name: project-reporter
description: Use this skill whenever the user wants to summarize a software/hardware project's planning, architecture, design, implementation details, or detailed project content into a Markdown report. Trigger for requests like “总结项目”, “生成项目规划设计文档”, “整理详细设计”, “写项目报告”, “从项目文件夹/GitHub/文字材料总结项目”, or when the user provides a repository, GitHub link, project folder, archive, README, source files, or raw notes and asks for a structured .md project summary. This skill should be used even if the user does not explicitly say “report” when the intent is to explain the project’s goals, design, modules, workflow, technologies, progress, or future plan.
---

# Project Reporter

Use this skill to produce a structured Markdown report that summarizes a project’s planning, design, architecture, and detailed content.

The skill supports three input sources:

1. The current repository’s `项目/` folder.
2. A GitHub link provided by the user.
3. Textual material provided directly by the user.

Your output should be a polished `.md` report in Chinese by default, unless the user requests another language.

## Workflow

### 1. Identify the input source

Determine where the project information should come from:

- If the user mentions the current repository or does not provide another source, inspect the `项目/` folder first.
- If the user provides a GitHub URL, use the available GitHub or web tools to inspect the repository contents. Prefer authenticated/local GitHub tooling if available; otherwise use web access for public repositories.
- If the user provides text, treat it as the primary source and only inspect files if the user asks you to combine sources.

If multiple sources are available, combine them carefully and state which sources were used.

### 2. Gather project evidence

For repository or folder sources, prioritize:

- README, docs, design notes, reports, requirements documents.
- Source code directory names and module boundaries.
- Configuration files that reveal frameworks, build tools, dependencies, or hardware/toolchain requirements.
- Test files, examples, demos, scripts, and CI files.
- Archive files in the `项目/` folder when they appear to contain the actual project.

For GitHub sources, inspect:

- Repository description and README.
- Directory structure.
- Important source files and examples.
- Releases, issues, or docs only when directly relevant to understanding project design.

For textual material, extract:

- Project background and goals.
- Functional requirements.
- Technical route and implementation method.
- Modules, data flow, control flow, interfaces, and constraints.
- Progress, results, limitations, and next steps.

Avoid inventing details. If a section cannot be supported by the source material, either omit it or mark it as “材料中未明确说明”.

### 3. Infer cautiously

You may infer high-level structure from filenames, code organization, dependencies, or README descriptions, but distinguish evidence from inference.

Good phrasing:

- “从目录结构看，项目主要包含……”
- “根据 README 描述，系统目标是……”
- “源码中出现的模块表明……”

Avoid overconfident claims when the evidence is thin.

### 4. Produce Markdown output

Unless the user specifies another structure, use this report template:

```markdown
# 项目规划设计与详细内容总结

## 1. 项目概述
- 项目名称：
- 项目类型：
- 项目目标：
- 应用场景：

## 2. 项目背景与需求分析
### 2.1 背景说明
### 2.2 功能需求
### 2.3 非功能需求或约束

## 3. 总体规划与设计思路
### 3.1 总体方案
### 3.2 技术路线
### 3.3 系统/工程结构

## 4. 详细设计
### 4.1 核心模块划分
### 4.2 模块功能说明
### 4.3 数据流、控制流或业务流程
### 4.4 接口、输入输出或关键参数

## 5. 实现内容
### 5.1 主要实现文件/目录
### 5.2 关键实现逻辑
### 5.3 构建、运行或使用方式

## 6. 测试、验证与结果
### 6.1 测试方式
### 6.2 验证结果
### 6.3 已知问题

## 7. 当前进展与后续计划
### 7.1 当前完成情况
### 7.2 后续优化方向

## 8. 总结
```

Adapt section names when the project type demands it:

- For hardware/FPGA/Verilog projects, include clock/reset, bus protocols, testbench, simulation, synthesis, and timing-related details when available.
- For web/software projects, include frontend/backend split, APIs, database/storage, deployment, and user workflow when available.
- For AI/data projects, include data sources, preprocessing, model or algorithm design, evaluation metrics, and experiment results when available.

### 5. Save or return the report

If the user asks to create a file, write the report as a `.md` file with a clear filename, such as:

- `project-report.md`
- `项目规划设计与详细内容总结.md`
- `<project-name>-report.md`

If the user does not explicitly ask for a file, provide the Markdown content in the response and offer to save it.

## Quality bar

A good report should:

- Be structured enough to use directly in a course project, graduation project, design document, or project archive.
- Explain both “what the project does” and “how it is designed/implemented”.
- Tie claims back to source material instead of guessing.
- Highlight missing information when the sources are incomplete.
- Prefer clear Chinese technical writing over vague promotional language.
- Preserve important technical names exactly, such as module names, filenames, protocols, APIs, commands, or dependencies.

## Common mistakes to avoid

- Do not summarize only the README when source files or project documents are available.
- Do not turn the output into a generic essay unrelated to the project evidence.
- Do not fabricate requirements, test results, performance numbers, or future plans.
- Do not ignore archives in the `项目/` folder if they likely contain the actual project.
- Do not output Word, PDF, or slides unless the user explicitly asks for conversion after the Markdown report is complete.
