# 自动选课脚本

## 简介

这是一个用于自动登录并选课的 Python 脚本，适用于沈阳化工大学（SYUCT）。通过读取 `config.json` 配置文件，脚本将自动登录系统，搜索课程，并根据指定的条件（如教师姓名和上课时间）选择课程。该脚本也已编译为可执行文件，便于无需安装 Python 环境的用户使用。


## 使用可执行文件

如果你不想安装 Python 环境，可以直接使用编译后的可执行文件。

1. 下载编译后的可执行文件 `main.exe`。
2. 确保 `config.json` 文件与 `main.exe` 位于同一目录下。配置文件应包含你的用户信息和课程选择配置（见下方配置说明）。
3. 双击 `main.exe` 文件运行程序，程序会自动登录并选课。

## 配置文件

在使用脚本之前，你需要配置 `config.json` 文件。该文件包含了你的用户信息和所需选择的课程信息。配置文件的格式如下：

```json
{
  "uid": "你的学号",
  "password": "你的密码",
  "name":"你的名字",
  "lessons": [
    {
      "name": "课程名",
      "teacher_name": "教师姓名",
      "Time": "上课时间"
    },
    {
      "name": "课程名",
      "teacher_name": "教师姓名",
      "Time": "上课时间"
    }
  ]
}
```

确保 `config.json` 文件与可执行文件 `main.exe` 位于同一目录下，程序会自动读取该文件中的配置。

## 使用源代码

如果你希望使用源代码而非可执行文件，请按照以下步骤操作：

### 环境要求

- Python 3.x（如果使用源代码）
- 安装以下 Python 库（如果使用源代码）：
  - `requests`
  - `beautifulsoup4`
  - `Pillow`
  - `ddddocr`

你可以使用以下命令安装依赖项：

```bash
pip install -r requirements.txt
```

### 编译

1. 安装 [PyInstaller](https://www.pyinstaller.org/)：

   ```bash
   pip install pyinstaller
   ```

2. 编译为可执行文件：

    windows
   ```bash
   .\build.ps1
   ```
   linux
   ```ps1
   ./build.sh
   ```

3. 生成的 `.exe` 文件将在 `dist` 文件夹中，双击即可运行。


## 注意事项

- 请确保 `uid` 和 `password` 配置正确，以便成功登录。
- 请确保配置的课程名称、教师姓名和上课时间准确无误。
- 如果使用可执行文件，确保 `config.json` 文件和 `main.exe` 在同一目录下。
