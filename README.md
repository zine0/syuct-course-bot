# 自动选课脚本

## 简介

这是一个用于自动登录并选课的 Python 脚本，适用于沈阳化工大学（SYUCT）。通过读取 `config.json` 配置文件，脚本将自动登录系统，搜索课程，并根据指定的条件（如教师姓名和上课时间）选择课程。该脚本也可以编译为可执行文件，便于无需安装 Python 环境的用户使用。

## 环境要求

- Python 3.x
- 安装以下 Python 库：
  - `requests`
  - `beautifulsoup4`
  - `Pillow`
  - `ddddocr`

你可以使用以下命令安装依赖项：

```bash
pip install -r requirements.txt
```

### 生成可执行文件

如果你不想安装 Python 环境，可以直接使用编译后的可执行文件。执行以下步骤将 Python 脚本编译为 `.exe` 文件：

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

## 配置文件

请确保编辑 `config.json` 文件，该文件包含了你的用户信息和所需选择的课程信息。格式如下：

```json
{
  "uid": "你的学号",
  "password": "你的密码",
  "lessons": [
    {
      "name": "课程名",
      "teacher_name": "教师姓名",
      "Time": "上课时间"
    }
  ]
}
```

## 使用方法

1. 确保你已配置好 `config.json` 文件。
2. 运行脚本：

   - 如果是 Python 环境：

     ```bash
     python main.py
     ```

   - 如果是已编译的可执行文件，直接双击 `main.exe` 即可。

## 注意事项

- 请确保输入的 `uid` 和 `password` 正确，以免登录失败。
- 确保所选的课程名称、教师姓名和上课时间准确无误。

---

这样，用户可以选择在本地环境运行 Python 脚本，或者直接使用编译后的可执行文件。
