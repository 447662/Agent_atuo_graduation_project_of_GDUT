from pathlib import Path
import re

root = Path('g:/My_code/Agent_atuo_graduation_project_of_GDUT')
source = root / 'test' / 'verilog-i2c-thesis_AIGC_down.md'
template = root / '模板' / 'GDUT-Undergraduate-Thesis-LaTeX-Template-main' / '模板.tex'
outdir = root / 'test' / 'latex'
out_tex = outdir / 'verilog-i2c-thesis_AIGC_down.tex'
manifest = outdir / 'conversion_manifest.txt'

outdir.mkdir(parents=True, exist_ok=True)
text = source.read_text(encoding='utf-8')
tpl = template.read_text(encoding='utf-8')
preamble = tpl.split('\\begin{document}', 1)[0].rstrip()
lines = text.splitlines()

def strip_heading_number(s: str) -> str:
    s = s.strip()
    s = re.sub(r'^(第[一二三四五六七八九十百零〇]+章)\s*', '', s)
    s = re.sub(r'^\d+(?:\.\d+)*\s*', '', s)
    return s.strip() or s

def protect(pattern, s, store):
    def repl(m):
        store.append(m.group(0))
        return f'@@KEEP{len(store)-1}@@'
    return re.sub(pattern, repl, s)

def tex_escape(s: str) -> str:
    keep = []
    s = protect(r'\$\$.*?\$\$', s, keep)
    s = protect(r'\$[^$]+\$', s, keep)
    codes = []
    def keep_code(m):
        codes.append(m.group(1))
        return f'@@CODE{len(codes)-1}@@'
    s = re.sub(r'`([^`]+)`', keep_code, s)
    repl = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    out = ''.join(repl.get(ch, ch) for ch in s)
    out = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', out)
    for i, code in enumerate(codes):
        esc = ''.join(repl.get(ch, ch) for ch in code)
        out = out.replace(f'@@CODE{i}@@', r'\texttt{' + esc + '}')
    for i, val in enumerate(keep):
        out = out.replace(f'@@KEEP{i}@@', val)
    return out

cn_abs, en_abs, cn_kw, en_kw = [], [], '', ''
body_start = 0
mode = None
for idx, line in enumerate(lines):
    stripped = line.strip()
    if re.match(r'^#{1,6}\s*摘要\s*$', stripped):
        mode = 'cn'
        continue
    if re.match(r'^#{1,6}\s*Abstract\s*$', stripped, re.I):
        mode = 'en'
        continue
    if stripped.startswith('**关键词') or stripped.startswith('关键词'):
        cn_kw = re.sub(r'^\*\*关键词[:：]\*\*\s*', '', stripped)
        cn_kw = re.sub(r'^关键词[:：]\s*', '', cn_kw)
        mode = None
        continue
    if stripped.startswith('**Key words') or stripped.startswith('**Keywords') or stripped.startswith('Key words') or stripped.startswith('Keywords'):
        en_kw = re.sub(r'^\*\*(Key words|Keywords)[:：]\*\*\s*', '', stripped, flags=re.I)
        en_kw = re.sub(r'^(Key words|Keywords)[:：]\s*', '', en_kw, flags=re.I)
        mode = None
        continue
    if re.match(r'^##\s+\d+\s+', stripped):
        body_start = idx
        break
    if mode == 'cn' and stripped:
        cn_abs.append(stripped)
    elif mode == 'en' and stripped:
        en_abs.append(stripped)

out = []
out.extend([preamble, '', r'\begin{document}', '', r'% 封面', r'\makecover', '', r'% 中英文摘要页（不编页码）', r'\pagenumbering{gobble}', ''])
out.extend([r'% 中文摘要', r'\begin{abstractcn}'])
for p in cn_abs:
    out.append('    ' + tex_escape(p))
    out.append('')
out.append(r'\end{abstractcn}')
if cn_kw:
    out.append(r'\keywords{' + tex_escape(cn_kw).replace('，', ', ') + '}')
out.extend(['', r'\clearpage', '', r'% 英文摘要', r'\begin{abstracten}'])
for p in en_abs:
    out.append('    ' + tex_escape(p))
    out.append('')
out.append(r'\end{abstracten}')
if en_kw:
    out.append(r'\keywordsen{' + tex_escape(en_kw).replace('，', ', ') + '}')
out.extend(['', r'\clearpage', '', r'% 目录', r'\tableofcontents', r'\clearpage', '', r'% 正文开始（从绪论开始编页码）', r'\pagenumbering{arabic}', r'\setcounter{page}{1}', ''])

in_code = False
in_enum = False
in_item = False

def close_lists():
    global in_enum, in_item
    if in_enum:
        out.append(r'\end{enumerate}')
    if in_item:
        out.append(r'\end{itemize}')
    in_enum = False
    in_item = False

for line in lines[body_start:]:
    raw = line.rstrip('\n')
    stripped = raw.strip()
    if stripped.startswith('```'):
        close_lists()
        if not in_code:
            in_code = True
            out.append(r'\begin{lstlisting}')
        else:
            in_code = False
            out.append(r'\end{lstlisting}')
        continue
    if in_code:
        out.append(raw)
        continue
    if not stripped:
        close_lists()
        out.append('')
        continue
    m = re.match(r'^(#{1,6})\s+(.+)$', stripped)
    if m:
        close_lists()
        level = len(m.group(1))
        title = strip_heading_number(m.group(2))
        if level <= 2:
            out.append(r'\clearpage')
            out.append(r'\section{' + tex_escape(title) + '}')
        elif level == 3:
            out.append(r'\subsection{' + tex_escape(title) + '}')
        elif level == 4:
            out.append(r'\subsubsection{' + tex_escape(title) + '}')
        else:
            out.append(r'\paragraph{' + tex_escape(title) + '}')
        continue
    if re.match(r'^[-*+]\s+', stripped):
        if not in_item:
            close_lists()
            out.append(r'\begin{itemize}[leftmargin=2em]')
            in_item = True
        out.append(r'    \item ' + tex_escape(re.sub(r'^[-*+]\s+', '', stripped)))
        continue
    if re.match(r'^\d+[.)]\s+', stripped):
        if not in_enum:
            close_lists()
            out.append(r'\begin{enumerate}[label=\arabic*.,leftmargin=2em]')
            in_enum = True
        out.append(r'    \item ' + tex_escape(re.sub(r'^\d+[.)]\s+', '', stripped)))
        continue
    close_lists()
    out.append(tex_escape(stripped))

close_lists()
out.extend(['', r'\clearpage', r'\phantomsection', r'\addcontentsline{toc}{section}{参考文献}', r'\bibliographystyle{unsrt}', r'\nocite{*}', r'\bibliography{references}', '', r'\end{document}'])
out_tex.write_text('\n'.join(out) + '\n', encoding='utf-8')
(outdir / 'references.bib').write_text('@misc{verilog_i2c_master,\n  title = {verilog-i2c-master project materials},\n  note = {Project materials used for thesis analysis}\n}\n', encoding='utf-8')
manifest.write_text('\n'.join([
    'Markdown to LaTeX test conversion',
    f'Source Markdown: {source}',
    f'Default template: {template}',
    f'Output TEX: {out_tex}',
    'Rules applied:',
    '- Removed numeric prefixes from LaTeX section/subsection titles.',
    '- Kept abstract headings centered through template abstractcn/abstracten environments.',
    '- Inserted \\clearpage before major chapters and major front/back matter.',
]) + '\n', encoding='utf-8')
print(out_tex)
