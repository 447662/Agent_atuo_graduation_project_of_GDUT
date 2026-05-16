## 附录 A 项目主要文件结构

```text
verilog-i2c-master/
├── README.md
├── rtl/
│   ├── axis_fifo.v
│   ├── i2c_init.v
│   ├── i2c_master.v
│   ├── i2c_master_axil.v
│   ├── i2c_master_wbs_8.v
│   ├── i2c_master_wbs_16.v
│   ├── i2c_single_reg.v
│   ├── i2c_slave.v
│   ├── i2c_slave_axil_master.v
│   └── i2c_slave_wbm.v
└── tb/
    ├── axil.py
    ├── axis_ep.py
    ├── i2c.py
    ├── wb.py
    ├── test_i2c_master.py
    ├── test_i2c_slave.py
    ├── test_i2c_master_axil.py
    ├── test_i2c_master_wbs_8.py
    ├── test_i2c_master_wbs_16.py
    ├── test_i2c_slave_axil_master.py
    └── test_i2c_slave_wbm.py
```

## 附录 B 典型仿真命令

```bash
cd tb
python test_i2c_master.py
```

测试脚本内部典型编译命令如下：

```bash
iverilog -o test_i2c_master.vvp ../rtl/i2c_master.v test_i2c_master.v
vvp -m myhdl test_i2c_master.vvp -lxt2
```

## 附录 C 待补充材料清单

1. 学校模板中的封面、任务书和个人信息；
2. CNKI 已核验中文参考文献；
3. MyHDL/Icarus Verilog 仿真日志；
4. 关键 I2C 波形截图；
5. FPGA 综合资源报告；
6. 板级外设读写实验记录；
7. 最终 DOCX 或 LaTeX 模板排版结果。
