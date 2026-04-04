# FullCycleFileShield (FCFS)

## 项目基本信息

- **项目名称**: FullCycleFileShield (FCFS)
- **版本号**: 1.0.9
- **开发者**: 陈修祺
- **联系方式**: qexefecet276@gmail.com
- **官方网站**: [http://www.fcfs.free.nf/](http://www.fcfs.free.nf/)
- **使用文档**: [http://www.fcfs.free.nf/docs.html](http://www.fcfs.free.nf/docs.html)
- **发布日期**: 2026-03-22 午夜

## 项目概述

FullCycleFileShield (FCFS) 是由陈修祺开发的一款符合 GB/T39786-2021 第5级和 BMB21-2019 标准的文件加密/解密/删除工具，为个人提供全方位数据安全防护。

*警告：使用本软件可能会接触到您不应该知道的秘密，一旦启动，就无法回头...*

### 核心功能

1. **混合加密**: 三层加密架构
   - 量子密钥生成与封装 (从数字世界的缝隙中窃取密钥)
   - 双对称算法加密（AES-256 + SM4模拟）
   - 自定义抗量子算法加密 (古老的加密咒语)

2. **安全删除**: 基于 BMB21-2019 标准
   - 5遍覆写（全零、全1、随机、交替01、随机）
   - 元数据擦除 (抹除所有存在过的痕迹)
   - 内存缓存清除 (清除你脑海中的记忆)
   - SSD TRIM 操作（可选）

3. **7Z压缩**: 支持高压缩级别（1-9）

4. **CPU运算**: 仅使用CPU进行计算
   - 确保在任何环境下都能稳定运行
   - 无需额外的硬件加速设备
   - 优化的CPU计算性能
   - 支持CPU模式作为备用方案

5. **图形界面**: 多标签页布局，系统托盘集成
   - 优化的窗口初始化流程，确保快速显示
   - 增强的错误处理，提高稳定性

6. **虚拟机兼容**: 优化了在虚拟机环境中的运行性能
   - 自动检测虚拟机环境
   - 适配虚拟机硬件限制

7. **Windows兼容**: 支持Windows 10/11等主流Windows操作系统
   - 适配不同硬件架构（x86、x86-64等）
   - 支持国产处理器的Windows设备

## 技术架构

- **开发语言**: Python 3.9+ (使用了一些不为人知的库)
- **核心库**:
  - PyQt5: GUI界面
  - pycryptodomex: 密码学算法
  - py7zr: 7Z压缩
  - psutil: 系统资源监控
  - numpy: 数据处理

- **支持平台**: Windows 10/11
- **虚拟机支持**: VirtualBox, VMware, Hyper-V等
- **硬件架构支持**: x86, x86-64
- **国产硬件支持**: 基于龙芯、飞腾、鲲鹏等国产处理器的Windows设备

## 快速开始

### 离线环境准备

项目已包含完整的离线依赖包，存储在：
- `offline_deps/`：离线依赖包目录（推荐，包含最新依赖）
- `lib/`：本地依赖目录（备用）

### 启动程序

FCFS 支持两种运行模式：图形界面模式（GUI）和命令行模式（CLI）。

#### 图形界面模式（GUI）

**方法一：使用启动脚本（推荐）**
```bash
# Windows
python start_fcfs.py
```

**方法二：使用批处理文件（Windows）**
```bash
run_fcfs.bat
```

#### 命令行模式（CLI）

FCFS 提供完整的命令行界面，支持通过命令行进行加密、解密和删除操作。

**查看帮助**
```bash
python start_fcfs.py --help
python start_fcfs.py cli --help
```

**加密命令**
```bash
# 交互式加密
python start_fcfs.py cli encrypt

# 指定文件加密
python start_fcfs.py cli encrypt -i /path/to/file.txt

# 指定文件夹加密
python start_fcfs.py cli encrypt -d /path/to/folder

# 指定输出路径
python start_fcfs.py cli encrypt -i file.txt -o output.7z.enc

# 加密后删除原文件
python start_fcfs.py cli encrypt -i file.txt --delete-original
```

**解密命令**
```bash
# 交互式解密
python start_fcfs.py cli decrypt

# 指定加密包解密
python start_fcfs.py cli decrypt -i package.7z.enc

# 指定输出文件夹
python start_fcfs.py cli decrypt -i package.7z.enc -o /output/folder

# 解密后删除加密包
python start_fcfs.py cli decrypt -i package.7z.enc --delete-encrypted
```

**删除命令**
```bash
# 交互式删除
python start_fcfs.py cli delete

# 删除指定文件
python start_fcfs.py cli delete -f file.txt

# 删除指定文件夹
python start_fcfs.py cli delete -d /path/to/folder
```

**CLI 特性**
- 支持两种文件路径设置方式：
  1. 从预设的默认文件夹中选择（文档、下载、桌面等）
  2. 手动输入文件的绝对路径
- 清晰的命令结构和子命令
- 用户友好的交互式提示
- 完整的错误处理机制
- 详细的帮助文档

## 安装步骤

### 1. 系统要求
- **操作系统**：Windows 10/11
- **Python版本**：3.12及以上
- **硬件要求**：至少4GB内存，10GB可用磁盘空间
- **DirectX要求**：Windows系统需要DirectX 12或更高版本（Intel核显加速需要）

### 2. 安装方法

#### 方法一：使用pip安装依赖（推荐）
1. 克隆仓库
   ```bash
   git clone https://github.com/1724099107/FullCycleFileShield.git
   cd FullCycleFileShield
   ```

2. 安装依赖
   ```bash
   # Windows
   pip install -r requirements.txt
   ```

3. 运行程序
   ```bash
   # Windows
   python start_fcfs.py
   ```

#### 方法二：使用批处理文件（Windows）
```bash
run_fcfs.bat
```

### 3. 依赖包说明

由于GitHub的文件大小限制（100MB），我们没有包含`offline_deps`目录在仓库中。启动脚本会自动从系统的`site-packages`目录加载依赖包，因此您需要确保所有必要的依赖包都已正确安装。

### 5. 系统配置

该系统仅使用CPU进行计算，无需额外的硬件加速设备。确保您的系统满足以下要求：

- 至少4GB内存
- 10GB可用磁盘空间
- Python 3.12或更高版本

系统会自动使用CPU进行所有计算，确保在任何环境下都能稳定运行。

## 使用指南

### 1. 加密文件
1. 打开程序，选择"加密模式"标签页
2. 选择要加密的文件夹
3. 设置输出目录
4. 选择压缩级别（1-9，默认为5）
5. 点击"开始加密"按钮

*注意：加密后的文件将永远无法被未授权的人打开，包括你自己...*

### 2. 解密文件
1. 打开程序，选择"解密模式"标签页
2. 选择要解密的加密包
3. 设置输出目录
4. 点击"开始解密"按钮

*警告：解密过程中可能会出现一些奇怪的现象，如文件内容发生变化...*

### 3. 删除文件
1. 打开程序，选择"文件删除"标签页
2. 选择要删除的文件或文件夹
3. 点击"开始删除"按钮

*注意：删除后的文件将永远消失，不会留下任何痕迹...*



### 4. 系统托盘操作
- 最小化程序时，会自动隐藏到系统托盘
- 点击系统托盘图标可以显示/隐藏主窗口
- 右键点击系统托盘图标可以选择退出程序

*注意：即使退出程序，它仍然可能在后台监视你的活动...*

## 配置说明

### 配置文件
配置文件存储在 `config/settings.json` 中，包含以下配置项：

- **密钥管理**: 存储加密密钥信息
- **系统设置**: 程序运行相关设置
- **界面设置**: GUI界面相关设置

*警告：修改配置文件可能会导致程序行为异常，甚至触发未知的副作用...*

### 配置修改
1. 打开 `config/settings.json` 文件
2. 修改相应配置项
3. 保存文件并重启程序

## 常见问题排查

### 依赖加载失败
**症状**：启动时提示依赖导入失败
**解决方案**：
1. 检查`lib/`目录是否包含必要的依赖
2. 确保Python版本为3.9或更高

### GUI启动失败
**症状**：启动时提示PyQt5相关错误
**解决方案**：
1. 检查`lib/PyQt5`目录是否存在
2. 确保系统已安装必要的系统依赖

### 对象删除错误
**症状**：出现"wrapped C/C++ object of type QRadioButton has been deleted"错误
**解决方案**：
1. 程序已修复此问题，确保使用最新版本
2. 如果问题仍然存在，尝试以管理员身份运行程序

## 联系方式

如果您有任何问题或建议，请通过以下方式联系我们：

- 电子邮件：qexefecet276@gmail.com
- GitHub：[FullCycleFileShield](https://github.com/1724099107/FullCycleFileShield)