# 项目规划设计与详细内容总结

## 1. 项目概述

- 项目名称：Verilog I2C interface（verilog-i2c-master）
- 项目类型：基于 Verilog HDL 的 FPGA/数字逻辑 I2C 总线接口 IP 设计项目
- 项目目标：实现可综合、可复用的 I2C 主机、从机及多种片上总线封装模块，使 FPGA 或 SoC 系统能够通过 I2C 总线访问外部 EEPROM、时钟芯片、传感器、配置器件等低速外设，并通过 AXI Stream、AXI Lite 或 Wishbone 等接口与上层控制逻辑连接。
- 应用场景：FPGA 外设配置、板级管理、片上系统低速控制通道、I2C 存储器访问、上电初始化序列执行、AXI/Wishbone 总线到 I2C 总线的协议桥接。

本报告依据项目目录 `项目/verilog-i2c-master` 中的 README、RTL 源码和测试平台文件整理。项目 README 明确说明该工程包含 I2C 接口组件，以及基于 MyHDL 的智能总线协同仿真测试平台。源码主要位于 `rtl/`，测试平台和总线行为模型主要位于 `tb/`。

## 2. 项目背景与需求分析

### 2.1 背景说明

I2C（Inter-Integrated Circuit）是一种常见的两线式串行通信总线，通常使用 SCL 时钟线和 SDA 数据线连接多个主设备与从设备。由于 I2C 只需要两根信号线即可完成地址选择、读写控制、应答检测和多字节传输，因此在嵌入式系统、FPGA 板卡、传感器网络、EEPROM 配置、时钟管理芯片配置等场景中应用广泛。

在 FPGA 系统中，若需要访问 I2C 外设，通常有两类实现方式：一类是通过软核 CPU 或硬核处理器运行软件驱动；另一类是在 FPGA 逻辑中实现专用 I2C 控制器。该项目属于第二类方案，其核心价值在于将 I2C 传输过程封装为可复用硬件模块，并提供 AXI Stream、AXI Lite、Wishbone 等接口形式，便于与不同 SoC 或 FPGA 总线结构集成。

项目 README 中列出了 `i2c_master`、`i2c_slave`、`i2c_master_axil`、`i2c_master_wbs_8`、`i2c_master_wbs_16`、`i2c_slave_axil_master`、`i2c_slave_wbm` 和 `i2c_init` 等模块，说明该工程不仅实现基础 I2C 主从通信，还面向多种上层总线和初始化应用场景提供封装。

### 2.2 功能需求

根据 README 和源码注释，项目可归纳出以下功能需求：

1. 支持 I2C 主机功能  
   `i2c_master.v` 通过命令输入、写数据输入和读数据输出接口执行 I2C 读、写、多字节写和停止条件操作。模块需要能够产生 start、repeated start、stop、读写位、ACK/NACK 等 I2C 时序，并在传输中维护 busy、bus_control、bus_active、missed_ack 等状态。

2. 支持 I2C 从机功能  
   `i2c_slave.v` 将 I2C 总线上的读写操作转换为 AXI Stream 数据传输。从机模块需要支持设备地址匹配、地址掩码配置、读写方向判断、数据收发、总线释放以及 busy、bus_address、bus_addressed、bus_active 等状态输出。

3. 支持 AXI Lite 总线封装  
   `i2c_master_axil.v` 将 I2C 主机封装为 32 位 AXI Lite 从设备，向处理器或上层主机暴露 Status、Command、Data、Prescale 等寄存器。`i2c_slave_axil_master.v` 则将 I2C 从机侧访问转换为参数化 AXI Lite master 操作。

4. 支持 Wishbone 总线封装  
   `i2c_master_wbs_8.v`、`i2c_master_wbs_16.v` 和 `i2c_slave_wbm.v` 提供 Wishbone 侧接口，适配 8 位或 16 位数据宽度的 Wishbone 系统。

5. 支持上电初始化序列  
   `i2c_init.v` 是一个 I2C 总线初始化模板模块，可在系统上电后无需通用处理器参与，按 ROM 表中配置的命令序列对一个或多个 I2C 外设执行初始化写入。

6. 支持 FIFO 缓冲与流式数据接口  
   `axis_fifo.v` 提供 AXI4-Stream FIFO，用于命令、写数据或读数据路径中的缓冲。其参数支持数据宽度、深度、tlast、tuser、帧 FIFO、坏帧丢弃等配置。

7. 支持协同仿真验证  
   `tb/` 目录中包含 MyHDL 测试脚本、I2C 行为模型、AXI Stream 端点、AXI Lite BFM、Wishbone 模型等，可通过 Icarus Verilog 与 MyHDL VPI 进行联合仿真。

### 2.3 非功能需求或约束

1. 可综合性约束：RTL 文件采用 Verilog 2001 编写，模块接口和状态机设计应适用于 FPGA 综合。
2. 协议时序约束：I2C 为开漏/三态总线，SCL 和 SDA 输出不能简单直接短接到输入，需要通过三态 I/O 或与逻辑模拟线与关系，以支持时钟拉伸和多设备共享总线。
3. 时钟配置约束：`i2c_master` 和总线封装模块使用 `prescale` 参数配置 I2C 时钟，源码注释给出的关系为 `prescale = Fclk / (FI2Cclk * 4)`。
4. 总线兼容性约束：项目面向 AXI Stream、AXI Lite、Wishbone 和 I2C 多种协议，模块需要在接口握手、寄存器访问、FIFO 状态、总线应答之间保持一致。
5. 测试环境约束：README 说明运行测试平台需要 MyHDL、Icarus Verilog，并正确安装 `myhdl.vpi` 以支持协同仿真。
6. 维护状态约束：README 中说明原仓库已被新的 `taxi` 项目取代，当前项目不再继续维护。作为毕业设计资料使用时，应以当前源码为研究对象，不应假设其仍有后续维护。

## 3. 总体规划与设计思路

### 3.1 总体方案

项目总体方案是围绕 I2C 协议核心构建一组可复用硬件模块：底层由 `i2c_master` 和 `i2c_slave` 完成 I2C 总线时序、数据移位、应答检测、起止条件控制和总线状态监测；中间通过 AXI Stream 作为命令与数据通道；上层再根据系统集成需求封装为 AXI Lite 或 Wishbone 寄存器接口。

主机方向的数据通路可概括为：上层控制逻辑或处理器写入命令和数据，命令经 FIFO 或 AXI Stream 通道进入 I2C 主机状态机，主机状态机根据地址、读写类型、start/stop 控制位驱动 SCL/SDA，完成 I2C 总线传输，并将读回数据或状态信息返回上层。

从机方向的数据通路可概括为：I2C 总线上的外部主机发起访问，从机模块检测 start 条件、接收地址、判断地址是否匹配，再根据读写方向将 I2C 写入字节输出为 AXI Stream 数据，或从 AXI Stream 输入数据中取数并在 I2C 读操作中发送给总线主机。

### 3.2 技术路线

1. 协议核心设计  
   使用有限状态机实现 I2C 读写流程。`i2c_master.v` 中包含命令层状态机和物理层状态机，命令层处理读、写、多字节写、停止等抽象操作，物理层处理 start、repeated start、读位、写位、stop 等底层时序。

2. 标准接口抽象  
   主从核心模块使用 AXI Stream 风格的 ready/valid/tlast 信号表示命令流和数据流，便于与 FIFO 或其他逻辑模块组合。

3. 片上总线封装  
   针对处理器控制场景，项目提供 AXI Lite 和 Wishbone 封装模块。封装模块通过寄存器把状态、命令、数据、分频配置等信息暴露给上层软件或总线主设备。

4. 开漏总线建模  
   I2C 的 SCL/SDA 信号采用 `*_i`、`*_o`、`*_t` 三类端口表达输入、输出和三态控制。源码注释中给出了三态引脚连接方式，也给出了不使用 `*_t` 时利用开漏特性的等效连接方式。

5. 初始化 ROM 表驱动  
   `i2c_init.v` 使用 `init_data` ROM 表描述初始化命令，将启动写、写数据、地址块、数据块、延时和停止等动作编码到 9 位命令字中，通过状态机顺序解释执行。

6. 协同仿真验证  
   测试平台采用 Python MyHDL 生成激励和行为模型，使用 Icarus Verilog 编译 Verilog DUT，再通过 VPI 与 MyHDL 进行联合仿真，验证 RTL 与高层行为模型之间的交互。

### 3.3 系统/工程结构

项目主要目录和文件如下：

```text
verilog-i2c-master/
├── README.md / README
├── AUTHORS
├── COPYING
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
    ├── test_i2c.py
    ├── test_i2c_master.py / test_i2c_master.v
    ├── test_i2c_slave.py / test_i2c_slave.v
    ├── test_i2c_master_axil.py / test_i2c_master_axil.v
    ├── test_i2c_master_wbs_8.py / test_i2c_master_wbs_8.v
    ├── test_i2c_master_wbs_16.py / test_i2c_master_wbs_16.v
    ├── test_i2c_slave_axil_master.py / test_i2c_slave_axil_master.v
    └── test_i2c_slave_wbm.py / test_i2c_slave_wbm.v
```

其中 `rtl/` 目录为可综合硬件设计，`tb/` 目录为仿真验证环境。README 中的 Source Files 和 Testbench Files 与实际目录结构基本一致。

## 4. 详细设计

### 4.1 核心模块划分

| 模块 | 文件 | 主要功能 |
|---|---|---|
| AXI Stream FIFO | `rtl/axis_fifo.v` | 为 AXI Stream 数据提供可参数化 FIFO 缓冲 |
| I2C 初始化模块 | `rtl/i2c_init.v` | 按 ROM 表生成 I2C 初始化命令与数据 |
| I2C 主机核心 | `rtl/i2c_master.v` | 生成 I2C 主机读写时序，处理命令和数据流 |
| I2C 主机 AXI Lite 封装 | `rtl/i2c_master_axil.v` | 通过 32 位 AXI Lite 寄存器控制 I2C 主机 |
| I2C 主机 Wishbone 8 位封装 | `rtl/i2c_master_wbs_8.v` | 通过 8 位 Wishbone 寄存器控制 I2C 主机 |
| I2C 主机 Wishbone 16 位封装 | `rtl/i2c_master_wbs_16.v` | 通过 16 位 Wishbone 寄存器控制 I2C 主机 |
| 单寄存器辅助模块 | `rtl/i2c_single_reg.v` | 从文件名和上下文看，用于单寄存器 I2C 访问辅助，具体应用需结合源码进一步展开 |
| I2C 从机核心 | `rtl/i2c_slave.v` | 将 I2C 从机读写转换为 AXI Stream 数据传输 |
| I2C 从机 AXI Lite master 封装 | `rtl/i2c_slave_axil_master.v` | 将 I2C 从机访问映射为 AXI Lite 主机访问 |
| I2C 从机 Wishbone master 封装 | `rtl/i2c_slave_wbm.v` | 将 I2C 从机访问映射为 Wishbone 主机访问 |

### 4.2 模块功能说明

#### 4.2.1 `i2c_master` 主机核心

`i2c_master` 是项目的核心主机模块。其主机侧接口包括：

- 命令输入：`s_axis_cmd_address`、`s_axis_cmd_start`、`s_axis_cmd_read`、`s_axis_cmd_write`、`s_axis_cmd_write_multiple`、`s_axis_cmd_stop`、`s_axis_cmd_valid`、`s_axis_cmd_ready`；
- 写数据输入：`s_axis_data_tdata`、`s_axis_data_tvalid`、`s_axis_data_tready`、`s_axis_data_tlast`；
- 读数据输出：`m_axis_data_tdata`、`m_axis_data_tvalid`、`m_axis_data_tready`、`m_axis_data_tlast`；
- I2C 总线接口：`scl_i`、`scl_o`、`scl_t`、`sda_i`、`sda_o`、`sda_t`；
- 状态输出：`busy`、`bus_control`、`bus_active`、`missed_ack`；
- 配置输入：`prescale`、`stop_on_idle`。

源码注释表明，主机模块支持 read、write、write multiple 和 stop 四类命令。读操作可通过 `start` 强制产生起始条件，通过 `stop` 在读完当前字节后产生停止条件，并通过 `m_axis_data_tlast` 标记末字节。写操作可写单字节或多字节，多字节写通过 `s_axis_data_tlast` 标记结束。

状态机方面，模块包含命令层状态如 `STATE_IDLE`、`STATE_ACTIVE_WRITE`、`STATE_ACTIVE_READ`、`STATE_START_WAIT`、`STATE_START`、`STATE_ADDRESS_1`、`STATE_ADDRESS_2`、`STATE_WRITE_1`、`STATE_WRITE_2`、`STATE_WRITE_3`、`STATE_READ`、`STATE_STOP`，并包含物理层状态如 `PHY_STATE_IDLE`、`PHY_STATE_ACTIVE`、`PHY_STATE_REPEATED_START_1`、`PHY_STATE_START_1`、`PHY_STATE_WRITE_BIT_1`、`PHY_STATE_READ_BIT_1`、`PHY_STATE_STOP_1` 等。由此可见，该模块将抽象命令处理与位级 I2C 时序生成分层实现。

#### 4.2.2 `i2c_slave` 从机核心

`i2c_slave` 将 I2C 从机行为转换为 AXI Stream 数据流。其配置接口包括 `enable`、`device_address` 和 `device_address_mask`，其中地址掩码可用于选择比较哪些地址位，若设置为 `7'h7f`，则表示完整匹配单一 7 位地址。

源码注释说明，从机模块会把 I2C 写操作转换为 AXI Stream 输出。为准确标记写事务的最后一个字节，模块会将 I2C 写入字节延迟一个字节时间再输出；当 I2C 主机读取从机时，模块会在 AXI Stream 输入数据未准备好时拉低 SCL，实现时钟拉伸。

从机状态包括 `STATE_IDLE`、`STATE_ADDRESS`、`STATE_ACK`、`STATE_WRITE_1`、`STATE_WRITE_2`、`STATE_READ_1`、`STATE_READ_2`、`STATE_READ_3` 等。模块还设置了 `FILTER_LEN` 参数，对 SCL/SDA 输入进行滤波，以提高边沿检测和起止条件识别的可靠性。

#### 4.2.3 `i2c_master_axil` AXI Lite 主机封装

`i2c_master_axil` 将 I2C 主机模块封装成 32 位 AXI Lite 从设备。该模块参数包括 `DEFAULT_PRESCALE`、`FIXED_PRESCALE`、`CMD_FIFO`、`CMD_FIFO_DEPTH`、`WRITE_FIFO`、`WRITE_FIFO_DEPTH`、`READ_FIFO`、`READ_FIFO_DEPTH` 等，可控制默认分频、是否固定分频以及命令/写/读 FIFO 的配置。

源码注释定义了寄存器映射：

| 地址 | 名称 | 作用 |
|---|---|---|
| `0x00` | Status | busy、bus_cont、bus_act、miss_ack、FIFO 空满和溢出状态 |
| `0x04` | Command | I2C 地址、start、read、write、write_multiple、stop 等命令位 |
| `0x08` | Data | I2C 数据、data_valid、data_last |
| `0x0C` | Prescale | I2C 时钟分频配置 |

这种封装适合在带处理器的 FPGA SoC 中使用，由软件通过 AXI Lite 写寄存器发起 I2C 访问，并读取状态和返回数据。

#### 4.2.4 `i2c_master_wbs_8` 与 `i2c_master_wbs_16`

Wishbone 封装模块提供类似 AXI Lite 封装的寄存器控制方式，但总线协议为 Wishbone。`i2c_master_wbs_8.v` 使用 8 位数据总线，寄存器地址包括 Status、FIFO Status、Cmd Addr、Command、Data、Prescale Low、Prescale High 等。`i2c_master_wbs_16.v` 则面向 16 位 Wishbone 系统，寄存器组织方式与数据宽度相适配。

该设计说明项目具备较强的平台适配性，可在不同开源 SoC、软核处理器或 FPGA 片上总线系统中复用。

#### 4.2.5 `i2c_init` 初始化模块

`i2c_init` 用于在系统启动时自动生成 I2C 初始化序列。README 将其描述为适用于 PLL、抖动衰减器、时钟复用器等外设上电配置的模板模块。源码注释说明该模块可以工作在单设备初始化和多设备初始化两种模式。

模块内部使用 `init_data` ROM 表存放 9 位命令字。命令编码包括：停止、退出多设备模式、对当前地址开始写、开始地址块、开始数据块、延时、发送 I2C stop、对指定地址开始写、写 8 位数据等。源码示例包含向 `0x50` 地址设备的 `0x0004` 寄存器写入 `0x11223344`，以及对 `0x50`、`0x51`、`0x52`、`0x53` 多个地址执行同一初始化序列。

#### 4.2.6 `axis_fifo` 流式缓冲模块

`axis_fifo` 是一个参数化 AXI4-Stream FIFO。其参数支持 FIFO 深度、数据宽度、`tkeep`、`tlast`、`tid`、`tdest`、`tuser`、输出流水级数、帧 FIFO 模式、坏帧标记和满时丢弃策略等。该模块可用于 I2C 总线封装中的命令 FIFO、写数据 FIFO 或读数据 FIFO。

源码中使用读写指针判断 full、empty、overflow 等状态，并通过 AXI Stream ready/valid 握手机制控制数据进出。

### 4.3 数据流、控制流或业务流程

#### 4.3.1 I2C 主机写流程

1. 上层逻辑通过命令接口或寄存器接口写入目标 I2C 地址、start、write、stop 等控制位。
2. 若为多字节写，上层继续通过 AXI Stream 写数据通道送入多个字节，并在最后一个字节置位 `tlast`。
3. `i2c_master` 判断总线是否空闲，必要时产生 start 或 repeated start。
4. 模块发送 7 位地址和写方向位，检测从机 ACK。
5. 模块逐字节发送数据，并在每个字节后检测 ACK。
6. 若命令要求停止，则产生 stop 条件；若设置 `stop_on_idle`，在命令输入无效且总线仍处于活动状态时可自动发出 stop。
7. 传输过程中更新 `busy`、`bus_control`、`bus_active` 和 `missed_ack` 等状态。

#### 4.3.2 I2C 主机读流程

1. 上层逻辑写入目标地址以及 read/start/stop 命令。
2. `i2c_master` 产生 start 或 repeated start，发送地址和读方向位。
3. 从机 ACK 后，主机释放 SDA 并在 SCL 时钟下采样数据位。
4. 每接收一个字节，模块通过 `m_axis_data_tdata` 输出，并使用 `m_axis_data_tvalid` 与上层握手。
5. 若读命令带 stop，则最后一个读字节通过 `m_axis_data_tlast` 标记，并产生 stop 条件。

#### 4.3.3 I2C 从机写入流程

1. 外部 I2C 主机产生 start，并发送 7 位地址和写方向位。
2. `i2c_slave` 检测起始条件，采样地址位并与 `device_address` 按 `device_address_mask` 比较。
3. 地址匹配后，从机应答并继续接收数据字节。
4. 接收的字节通过 AXI Stream 输出给本地逻辑。
5. 为准确标记最后一个写入字节，模块在输出时延迟一个字节时间，以便在检测 stop 或新事务边界后设置 `tlast`。

#### 4.3.4 I2C 从机读取流程

1. 外部 I2C 主机发送地址和读方向位。
2. 地址匹配后，`i2c_slave` 从 AXI Stream 输入侧获取待发送字节。
3. 若输入数据尚未准备好，模块通过拉低 SCL 实现时钟拉伸，等待数据有效。
4. 数据准备好后，模块按 I2C 时序逐位驱动 SDA，等待主机 ACK/NACK。
5. 事务结束后更新 `bus_addressed`、`bus_active` 和 `busy` 等状态。

### 4.4 接口、输入输出或关键参数

#### 4.4.1 I2C 总线接口

项目中 I2C 信号普遍采用以下形式：

- `scl_i` / `i2c_scl_i`：SCL 输入采样；
- `scl_o` / `i2c_scl_o`：SCL 输出值；
- `scl_t` / `i2c_scl_t`：SCL 三态控制；
- `sda_i` / `i2c_sda_i`：SDA 输入采样；
- `sda_o` / `i2c_sda_o`：SDA 输出值；
- `sda_t` / `i2c_sda_t`：SDA 三态控制。

源码注释中给出三态引脚连接示例：输入端接引脚，输出端在 `*_t` 有效时置为高阻，否则输出 `*_o`。由于 I2C 是开漏总线，也可在不使用 `*_t` 时用输出值控制是否拉低总线。

#### 4.4.2 AXI Stream 接口

主从核心模块使用 AXI Stream 风格接口传输命令或数据，典型信号包括：

- `tdata`：数据字节或命令字段；
- `tvalid`：发送方声明数据有效；
- `tready`：接收方声明可以接收；
- `tlast`：标记多字节事务末尾。

该接口使 I2C 核心可以与 FIFO、DMA、状态机或其他流式模块组合。

#### 4.4.3 AXI Lite 寄存器接口

`i2c_master_axil` 暴露标准 AXI Lite 通道：`AW`、`W`、`B`、`AR`、`R` 五类信号。其寄存器包括状态、命令、数据和分频。状态寄存器中含有 FIFO 空满、溢出、miss_ack、bus_active、bus_control、busy 等位。

#### 4.4.4 Wishbone 接口

Wishbone 封装模块使用 `wbs_adr_i`、`wbs_dat_i`、`wbs_dat_o`、`wbs_we_i`、`wbs_stb_i`、`wbs_ack_o`、`wbs_cyc_i` 等信号。8 位封装将寄存器拆分为多个 8 位地址，16 位封装则适配更宽数据路径。

#### 4.4.5 关键参数

| 参数/信号 | 含义 |
|---|---|
| `prescale` | I2C 时钟分频配置，关系为 `prescale = Fclk / (FI2Cclk * 4)` |
| `stop_on_idle` | 命令空闲时是否自动发送 stop |
| `FILTER_LEN` | 从机 SCL/SDA 输入滤波长度 |
| `device_address` | 从机 7 位设备地址 |
| `device_address_mask` | 从机地址匹配掩码 |
| `CMD_FIFO_DEPTH` | 命令 FIFO 深度 |
| `WRITE_FIFO_DEPTH` | 写数据 FIFO 深度 |
| `READ_FIFO_DEPTH` | 读数据 FIFO 深度 |
| `DEFAULT_PRESCALE` | 封装模块默认分频值 |
| `FIXED_PRESCALE` | 是否固定分频配置 |

## 5. 实现内容

### 5.1 主要实现文件/目录

1. `rtl/i2c_master.v`  
   实现 I2C 主机核心协议逻辑，是项目主机方向的核心文件。模块负责解析命令、发送地址、读写数据、产生起止条件、检测 ACK、控制 SCL/SDA 以及输出状态。

2. `rtl/i2c_slave.v`  
   实现 I2C 从机核心协议逻辑，负责地址匹配、数据收发、I2C 写入到 AXI Stream 输出、AXI Stream 输入到 I2C 读出，以及时钟拉伸。

3. `rtl/i2c_master_axil.v`  
   实现 AXI Lite 从接口封装，适合处理器通过寄存器访问 I2C 主机控制器。

4. `rtl/i2c_master_wbs_8.v` 与 `rtl/i2c_master_wbs_16.v`  
   实现 8 位和 16 位 Wishbone 从接口封装，适用于 Wishbone 总线系统。

5. `rtl/i2c_slave_axil_master.v` 与 `rtl/i2c_slave_wbm.v`  
   实现从 I2C 从机侧到 AXI Lite master 或 Wishbone master 的桥接功能。

6. `rtl/i2c_init.v`  
   实现基于 ROM 表的 I2C 初始化序列生成器，可用于上电配置外设。

7. `rtl/axis_fifo.v`  
   实现通用 AXI Stream FIFO，为流式命令和数据提供缓冲。

8. `tb/` 目录  
   包含 MyHDL 测试平台、总线行为模型和 Verilog 顶层测试模块，用于对各 RTL 模块进行协同仿真。

### 5.2 关键实现逻辑

#### 5.2.1 分层状态机

`i2c_master` 将 I2C 主机操作拆分为命令层和物理层。命令层关注读写事务、地址、数据方向和 stop 条件；物理层关注 SCL/SDA 的位级时序、start/repeated start/stop 条件以及单个位的读写。分层状态机使模块既能响应上层命令，又能保证 I2C 协议时序的可控性。

#### 5.2.2 开漏输出与三态控制

I2C 总线要求设备只能主动拉低总线，释放总线后由上拉电阻拉高。因此项目采用 `*_o` 与 `*_t` 配合表达开漏行为。源码注释明确提醒 `scl_o` 不应直接连接到 `scl_i`，否则会破坏时钟拉伸机制。

#### 5.2.3 ACK 与错误状态

主机在发送地址或数据后需要检测从机 ACK。如果没有检测到 ACK，`missed_ack` 状态会被置位或脉冲输出。AXI Lite 和 Wishbone 封装模块也将该状态映射到状态寄存器中，使上层软件能够判断外设是否应答。

#### 5.2.4 FIFO 缓冲与寄存器映射

封装模块通过 FIFO 解耦处理器寄存器访问和 I2C 总线传输时序。命令 FIFO、写 FIFO 和读 FIFO 分别处理控制命令、待发送数据和接收数据。状态寄存器中的 `cmd_empty`、`cmd_full`、`wr_empty`、`wr_full`、`rd_empty`、`rd_full` 等位用于反映 FIFO 状态。

#### 5.2.5 从机时钟拉伸

`i2c_slave` 在 I2C 主机读取数据而本地 AXI Stream 输入尚未提供数据时，可以通过保持 SCL 为低实现 clock stretching。该机制允许从机暂停总线，等待内部数据准备完成。

#### 5.2.6 初始化序列表解释执行

`i2c_init` 将初始化动作编码为 ROM 表项，状态机按顺序读取并解释命令。该设计避免在无 CPU 系统中单独编写软件驱动，使 FPGA 逻辑能够在上电后自动配置外设。

### 5.3 构建、运行或使用方式

根据 README，测试平台运行需要以下工具：

1. Python 环境；
2. MyHDL；
3. Icarus Verilog；
4. 正确安装 `myhdl.vpi` 以支持 MyHDL 与 Verilog 的协同仿真。

以 `tb/test_i2c_master.py` 为例，脚本中通过如下方式构建 Verilog 仿真目标：

```text
iverilog -o test_i2c_master.vvp ../rtl/i2c_master.v test_i2c_master.v
```

随后通过：

```text
vvp -m myhdl test_i2c_master.vvp -lxt2
```

加载 MyHDL VPI 并执行协同仿真。README 说明测试脚本既可以通过 nose、pytest 等 Python 测试运行器执行，也可以直接使用 Python 运行单个测试脚本。

实际集成到 FPGA 项目时，可根据应用场景选择：

- 纯逻辑控制场景：实例化 `i2c_master` 或 `i2c_slave`，使用 AXI Stream 风格接口连接本地状态机；
- 处理器控制场景：实例化 `i2c_master_axil`，通过 AXI Lite 寄存器访问 I2C；
- Wishbone SoC 场景：实例化 `i2c_master_wbs_8` 或 `i2c_master_wbs_16`；
- 无处理器初始化场景：修改 `i2c_init.v` 中的 `init_data` ROM 表，用于上电自动配置 I2C 外设。

## 6. 测试、验证与结果

### 6.1 测试方式

项目测试采用 MyHDL + Icarus Verilog 协同仿真方式。`tb/` 目录中包含以下测试基础组件：

- `tb/i2c.py`：I2C 主机、从机和存储器行为模型；
- `tb/axis_ep.py`：AXI Stream source/sink 端点；
- `tb/axil.py`：AXI4-Lite master 和 memory BFM；
- `tb/wb.py`：Wishbone master 模型和 RAM 模型。

以 `test_i2c_master.py` 为例，测试平台会实例化 AXI Stream 命令源、数据源和数据接收端，同时创建两个 I2C memory 模型，地址分别为 `0x50` 和 `0x51`，其中一个存储器模型设置了额外 latency，用于验证主机在不同响应条件下的读写行为。

测试脚本通过 Icarus Verilog 编译 DUT，再通过 `Cosimulation` 连接 MyHDL 激励与 Verilog 模块，实现软硬件协同仿真。

### 6.2 验证结果

从项目材料可以确认：

1. 每个主要 RTL 模块均有对应测试文件，例如 `test_i2c_master.py/.v`、`test_i2c_slave.py/.v`、`test_i2c_master_axil.py/.v`、`test_i2c_master_wbs_8.py/.v`、`test_i2c_slave_wbm.py/.v` 等。
2. 测试环境覆盖了 I2C 主机、I2C 从机、AXI Lite 封装、Wishbone 封装和初始化模块。
3. 测试方法基于行为模型、总线功能模型和 Verilog RTL 的协同仿真，可验证接口握手、总线时序和数据一致性。

当前报告未实际运行仿真命令，因此不能给出本机环境下的通过率、波形截图或具体性能数据。若用于毕业论文，需要后续在本地安装依赖并运行测试，将仿真日志、波形或关键时序截图作为论文实验章节证据。

### 6.3 已知问题

1. README 中声明原项目已被新项目取代，当前仓库不再维护。因此在工程化应用中需要自行评估兼容性和长期维护风险。
2. 当前材料中未提供综合报告、资源占用、最高工作频率、时序收敛结果等 FPGA 实测数据。
3. 当前材料中未提供板级实物测试结果，验证主要依赖仿真环境。
4. 若使用 MyHDL 协同仿真，需要保证 `myhdl.vpi` 与 Icarus Verilog 版本匹配，否则测试脚本可能无法正常启动。
5. `i2c_init.v` 中的初始化数据是模板示例，实际项目集成时必须根据目标外设手册修改地址、寄存器和值。

## 7. 当前进展与后续计划

### 7.1 当前完成情况

根据项目现有文件，当前工程已经完成以下内容：

1. I2C 主机核心 RTL 设计；
2. I2C 从机核心 RTL 设计；
3. AXI Stream FIFO 支撑模块；
4. AXI Lite 和 Wishbone 主机封装；
5. I2C 从机到 AXI Lite/Wishbone 主接口桥接模块；
6. I2C 初始化模板模块；
7. MyHDL + Icarus Verilog 协同仿真测试平台；
8. README 层面的模块说明、源文件说明和测试环境说明。

### 7.2 后续优化方向

1. 完成本地仿真验证  
   安装 MyHDL、Icarus Verilog 和 `myhdl.vpi`，运行 `tb/` 中全部测试脚本，记录测试通过情况、仿真日志和波形结果。

2. 增加 FPGA 综合实验  
   选择典型 FPGA 开发板，将 `i2c_master_axil` 或 `i2c_master_wbs_8` 集成到 SoC 工程中，统计 LUT、FF、BRAM 等资源占用和最高时钟频率。

3. 结合具体外设完成应用验证  
   选择 EEPROM、温度传感器、RTC 或时钟芯片等 I2C 外设，设计读写实验，验证 I2C 控制器在真实硬件环境中的通信可靠性。

4. 完善错误处理和边界测试  
   针对 NACK、总线被占用、从机时钟拉伸、FIFO 溢出、多主设备仲裁等场景补充测试用例。

5. 补充毕业论文所需材料  
   后续论文写作应补充 I2C 协议原理、模块状态机图、寄存器映射表、仿真波形图、综合结果表和实验分析。

## 8. 总结

`verilog-i2c-master` 是一个结构完整的 Verilog I2C 接口 IP 项目。其设计围绕 I2C 主从通信核心展开，通过 AXI Stream 抽象命令和数据流，并进一步封装为 AXI Lite 与 Wishbone 总线接口，兼顾纯硬件逻辑控制和处理器寄存器控制两类应用场景。项目还提供 `i2c_init` 初始化模板，可用于无处理器参与的上电外设配置。

从工程结构看，该项目具有较好的模块化程度：核心协议、总线封装、FIFO 缓冲、初始化逻辑和测试平台相互分离，便于复用和扩展。从验证角度看，项目提供了 MyHDL 与 Icarus Verilog 协同仿真环境，能够通过行为模型验证 I2C 总线交互和片上接口逻辑。但当前材料缺少本地实际仿真结果、综合资源数据和硬件测试数据，后续若将其发展为完整毕业论文，需要围绕仿真验证、综合分析和应用实验进一步补充证据。

总体而言，该项目适合作为“基于 Verilog 的 I2C 总线控制器设计与验证”类毕业设计的基础工程。论文可围绕 I2C 协议原理、主从控制器状态机设计、AXI/Wishbone 总线封装、FIFO 缓冲机制、协同仿真验证和 FPGA 集成应用展开，形成较完整的硬件设计与验证研究内容。
