# 沈阳化工大学自动枪课脚本

## 简介

这是一个用于自动登录并选课的Python脚本。通过读取 `config.json` 配置文件，脚本将自动登录系统，搜索课程，并根据指定的条件（如教师姓名和上课时间）选择课程。

## 环境要求

- Python 3.x
- 安装以下Python库：
  - `requests`
  - `beautifulsoup4`
  - `Pillow`
  - `ddddocr`

你可以使用以下命令安装依赖项：

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 配置 `config.json`

首先，你需要编辑 `config.json` 文件，该文件包含了你的用户信息和所需选择的课程信息。格式如下：

```json
{
  "uid": "你的学号",
  "password": "你的密码",
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

### 2. 运行脚本

确保 `config.json` 文件已正确配置，然后运行 `main.py`
