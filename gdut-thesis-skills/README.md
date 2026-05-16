# GDUT Thesis Workflow Skills

这是一个可直接下载并安装到 Claude Code 的毕业论文流程 skills 包，适用于从项目资料生成本科毕业论文、查重/AIGC 报告后进行原创性与自然表达修订、导出 DOCX/TEX，以及生成外文文献翻译的工作流。

## 包含的 skills

- `thesis-orchestrator`：论文全流程编排
- `project-reporter`：项目规划设计与详细内容报告
- `thesis-writer`：基于项目报告生成论文 Markdown/PDF
- `AIGC_down`：基于查重/AIGC 报告进行原创性、引用规范和自然表达修订
- `thesis-md-to-docx`：最终 Markdown 转 DOCX
- `thesis-md-to-tex`：最终 Markdown 转 LaTeX TEX
- `literature-translation-to-tex`：外文文献翻译转 LaTeX
- `markdown-to-docx`：Markdown 到 Word 的基础转换能力
- `cnki-*`：CNKI 检索、导出和下载辅助 skills
- `gs-*`：Google Scholar 检索、引用和全文链接辅助 skills

## 一键安装

### Windows PowerShell

```powershell
git clone -b skills https://github.com/447662/Agent_atuo_graduation_project_of_GDUT.git gdut-thesis-skills
cd gdut-thesis-skills/gdut-thesis-skills
./install.ps1
```

### macOS / Linux / Git Bash

```bash
git clone -b skills https://github.com/447662/Agent_atuo_graduation_project_of_GDUT.git gdut-thesis-skills
cd gdut-thesis-skills/gdut-thesis-skills
bash install.sh
```

## 手动安装

将下面目录中的所有 skill 文件夹复制到 Claude Code 的 skills 目录：

```text
gdut-thesis-skills/plugins/gdut-thesis-workflow/skills/*
```

默认目标目录：

- Windows：`%USERPROFILE%/.claude/skills`
- macOS/Linux：`~/.claude/skills`

安装后重启 Claude Code 或重新加载会话。

## 使用入口

推荐直接请求：

```text
使用 thesis-orchestrator，把项目资料转换成完整本科毕业论文，并最终导出 DOCX 或 TEX。
```

## 注意事项

- `AIGC_down` 只用于原创性、引用规范、重复内容处理和自然表达修订，不承诺规避检测或保证分数下降。
- CNKI、Google Scholar、DOCX/PDF/TEX 转换能力依赖本机环境、浏览器登录状态和合法访问权限。
- LaTeX 导出默认使用 GDUT 模板路径；如果你的项目目录不同，请在使用时指定模板路径。
