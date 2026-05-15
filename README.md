# Agent 自动化毕业设计项目

本仓库用于管理广东工业大学毕业设计相关的自动化资料、论文写作辅助流程、Claude Code 技能配置、文档模板、查重/AIGC 检测材料以及参考工程代码。

## 目录结构

- `.claude/`：Claude Code 本项目配置、技能、评测数据和工作区资源。
- `skill存储/`：本地技能压缩包备份。
- `模板/`：毕业论文答辩 PPT 等模板资料。
- `项目/`：毕业设计参考或实验项目代码。
- `test/`：论文、报告、导出文档和技能测试产物。
- `查重/`：查重报告、AIGC 检测报告及相关网页资源。

## 主要内容

- 论文写作与格式转换技能：如 thesis-writer、thesis-md-to-docx、thesis-orchestrator 等。
- 学术检索技能：包括 CNKI、Google Scholar 相关搜索、解析、导出和下载技能。
- 报告生成技能：用于项目报告、科研报告和技术分析文档生成。
- Verilog I2C 相关参考工程及论文材料。

## 使用说明

1. 使用 Claude Code 打开本仓库。
2. 根据任务调用 `.claude/skills/` 下的本地技能。
3. 论文、查重、检测和导出结果统一保存在对应目录中。
4. 推送到 GitHub 前确认没有需要排除的隐私信息或临时大文件。

## GitHub 同步

本项目已配置远程仓库，可通过以下命令同步：

```bash
git pull --rebase origin main
git push origin main
```

如果 GitHub 连接失败，可为当前仓库配置代理后重试：

```bash
git config --local http.proxy http://127.0.0.1:7890
git config --local https.proxy http://127.0.0.1:7890
```
