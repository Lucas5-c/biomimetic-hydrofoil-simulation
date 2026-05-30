# 仿生分区主动水翼综合仿真平台

这是一个用于展示仿生分区主动水翼流动控制趋势的交互式可视化网站。部署后，用户只需要打开网页链接即可使用，不需要安装 Python、下载项目或运行本地脚本。

## 功能

- 动态水流粒子；
- 压力云图；
- 速度场与流线；
- 空化风险；
- 表面压力曲线；
- A/B/C 分区控制；
- 参数扫描和导出。

## 部署方式

1. 将 `streamlit_deploy` 目录内容上传到 GitHub 仓库。
2. 在 Streamlit Community Cloud 新建 App。
3. 选择仓库、分支和主入口 `app.py`。
4. 平台会自动安装 `requirements.txt` 中的依赖。
5. 部署完成后，将生成的网页链接分享给朋友。

## 本地运行方式

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 注意

- 本系统不是高精度 CFD；
- 结果用于概念展示、专利方案说明和趋势演示；
- 云端导出文件不保证长期保存；
- 如果要保存图片、GIF、CSV、JSON 或报告，请生成后立即下载。
