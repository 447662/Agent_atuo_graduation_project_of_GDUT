from pathlib import Path
import re
import subprocess

root = Path(r"g:/My_code/Agent_atuo_graduation_project_of_GDUT")
md_path = root / "test/verilog-i2c-thesis_final.md"
template_path = root / "模板/GDUT-Undergraduate-Thesis-LaTeX-Template-main/模板.tex"
cover_path = template_path.parent / "论文封面.pdf"
out_path = root / "test/verilog-i2c-thesis_final.tex"
work_dir = root / "test"

md = md_path.read_text(encoding="utf-8")
template = template_path.read_text(encoding="utf-8")
preamble = template.split("\\begin{document}", 1)[0].rstrip()

# Remove initial note blockquote for final TeX body; keep it out of the formal thesis.
md = re.sub(r"\n> 本文为本科毕业论文初稿。.*?标明。\n", "\n", md, count=1)

# Parse main sections by top-level headings.
parts = re.split(r"^# ", md, flags=re.M)
sections = {}
title = "基于 Verilog 的 I2C 总线控制器设计与验证"
for part in parts:
    part = part.strip()
    if not part:
        continue
    first, _, rest = part.partition("\n")
    heading = first.strip()
    content = rest.strip()
    if heading == title:
        continue
    sections[heading] = content

cn_abs = sections.get("摘要", "")
en_abs = sections.get("Abstract", "")
kw_match = re.search(r"\*\*关键词：\*\*\s*(.+)", cn_abs)
cn_keywords = kw_match.group(1).strip() if kw_match else "I2C 总线，Verilog，FPGA，AXI Lite，Wishbone，协同仿真"
cn_abs = re.sub(r"\n?\*\*关键词：\*\*\s*.+", "", cn_abs).strip()
kw_en_match = re.search(r"\*\*Key words:\*\*\s*(.+)", en_abs)
en_keywords = kw_en_match.group(1).strip() if kw_en_match else "I2C bus, Verilog, FPGA, AXI Lite, Wishbone, co-simulation"
en_abs = re.sub(r"\n?\*\*Key words:\*\*\s*.+", "", en_abs).strip()

main_headings = [h for h in sections if re.match(r"^[1-7] ", h)]
main_md = "\n\n".join(f"# {h}\n\n{sections[h]}" for h in main_headings)
refs_md = sections.get("参考文献", "")
thanks_md = sections.get("致谢", "")
appendix_md = sections.get("附录", "")


def md_to_latex(name: str, content: str) -> str:
    tmp_md = work_dir / f"_tex_chunk_{name}.md"
    tmp_tex = work_dir / f"_tex_chunk_{name}.tex"
    tmp_md.write_text(content.strip() + "\n", encoding="utf-8")
    subprocess.run([
        "pandoc", str(tmp_md), "-f", "markdown", "-t", "latex", "--listings", "-o", str(tmp_tex)
    ], check=True)
    return tmp_tex.read_text(encoding="utf-8").strip()


def plain_inline_code(tex: str) -> str:
    tex = re.sub(r"\\passthrough\{\\lstinline!([^!]*)!\}", r"\1", tex)
    tex = re.sub(r"\\lstinline!([^!]*)!", r"\1", tex)
    tex = re.sub(r"\\passthrough\{([^{}]*)\}", r"\1", tex)
    return tex


def fix_heading_numbers(tex: str) -> str:
    for command in ("section", "subsection", "subsubsection"):
        tex = re.sub(
            rf"\\{command}\{{\s*[1-7](?:\\?\.[0-9]+){{0,2}}\s+",
            rf"\\{command}{{",
            tex,
        )
    return tex

cn_abs_tex = md_to_latex("abstract_cn", cn_abs)
en_abs_tex = md_to_latex("abstract_en", en_abs)
main_tex = md_to_latex("main", main_md)
refs_tex = md_to_latex("refs", refs_md)
thanks_tex = md_to_latex("thanks", thanks_md)
appendix_tex = md_to_latex("appendix", appendix_md)

# Remove manually embedded section numbers from headings; LaTeX will number sections.
main_tex = fix_heading_numbers(main_tex)
main_tex = plain_inline_code(main_tex)
refs_tex = plain_inline_code(refs_tex)
thanks_tex = plain_inline_code(thanks_tex)
appendix_tex = plain_inline_code(appendix_tex)

main_tex = main_tex.replace("{\\def\\LTcaptype{none} % do not increment counter\n", "")
main_tex = main_tex.replace("\n\\end{longtable}\n}", "\n\\end{longtable}")

# Convert Markdown reference lines into a simple references list instead of BibTeX.
refs_tex = refs_tex.replace("\\begin{enumerate}\n\\def\\labelenumi{[\\arabic{enumi}]}", "\\begin{enumerate}[label={[\\arabic*]},leftmargin=2.8em]")
refs_tex = refs_tex.replace("\\def\\labelenumi{[\\arabic{enumi}]}", "")
refs_tex = refs_tex.replace("\\tightlist", "")

# Appendix headings: remove duplicated top-level appendix title if generated.
appendix_tex = re.sub(r"^\\section\{附录 A 项目主要文件结构\}", r"\\section{项目主要文件结构}", appendix_tex)
appendix_tex = appendix_tex.replace("\\subsection{附录 A 项目主要文件结构}", "\\section{项目主要文件结构}")
appendix_tex = appendix_tex.replace("\\subsection{附录 B 典型仿真命令}", "\\section{典型仿真命令}")
appendix_tex = appendix_tex.replace("\\subsection{附录 C 待补充材料清单}", "\\section{待补充材料清单}")
appendix_tex = appendix_tex.replace("├", r"\\textbar--")
appendix_tex = appendix_tex.replace("└", r"\\textbar--")
appendix_tex = appendix_tex.replace("│", r"\\textbar")
appendix_tex = appendix_tex.replace("─", "-")

# Add title metadata commands after preamble for easier manual completion.
meta = r'''
% 论文基本信息（请按学校封面要求在最终提交前补充或替换封面 PDF）
\title{基于 Verilog 的 I2C 总线控制器设计与验证}
\author{请填写姓名}
\date{请填写日期}
% Pandoc 兼容命令
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\definecolor{shadecolor}{RGB}{248,248,248}
\newenvironment{Shaded}{}{}
'''

cover_tex_path = str(cover_path).replace("\\", "/")

tex = preamble + meta + r'''

\begin{document}

% 封面：使用默认 GDUT LaTeX 模板目录中的封面 PDF，仅插入第 1 页，避免多页封面 PDF 的异常页导致编译失败。
\includepdf[pages=1]{''' + cover_tex_path + r'''}

\pagenumbering{gobble}

\begin{abstractcn}
\par\indent
''' + cn_abs_tex + r'''
\end{abstractcn}
\keywords{''' + cn_keywords + r'''}

\clearpage

\begin{abstracten}
\par\indent
''' + en_abs_tex + r'''
\end{abstracten}
\keywordsen{''' + en_keywords + r'''}

\clearpage
\tableofcontents
\clearpage

\pagenumbering{arabic}
\setcounter{page}{1}

''' + main_tex + r'''

\clearpage
\phantomsection
\addcontentsline{toc}{section}{参考文献}
\section*{参考文献}
''' + refs_tex + r'''

\clearpage
\section*{致谢}
\addcontentsline{toc}{section}{致谢}
''' + thanks_tex + r'''

\clearpage
\appendix
''' + appendix_tex + r'''

\end{document}
'''

out_path.write_text(tex, encoding="utf-8", newline="\n")
print(out_path)
