# 网站部署说明

## 1. 注册 GitHub

打开 GitHub 官网，使用邮箱注册账号并完成邮箱验证。

## 2. 创建 GitHub 仓库

登录后点击 New repository，填写仓库名称，建议选择 Public。创建完成后进入仓库页面。

## 3. 上传部署目录内容

上传 `streamlit_deploy` 目录里的内容，让仓库根目录直接包含：

- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `components/`
- `core/`
- `assets/`
- `docs/`
- `README.md`

不要上传本地启动脚本、缓存目录、桌面环境配置或大型临时文件。

## 4. 进入 Streamlit Community Cloud

打开 Streamlit Community Cloud，使用 GitHub 账号登录。

## 5. 连接 GitHub

首次使用时授权 Streamlit 访问 GitHub 仓库。授权后可以在 App 创建页面选择仓库。

## 6. 选择 app.py

创建 App 时填写：

- Repository：刚创建的仓库；
- Branch：通常是 `main`；
- Main file path：`app.py`。

## 7. 部署

点击 Deploy。平台会读取 `requirements.txt` 并自动安装依赖，然后启动网站。

## 8. 分享链接

部署成功后，复制 Streamlit 页面顶部或设置页中的 App URL，直接发给朋友即可。

## 9. 查看部署失败日志

如果部署失败，进入 App 管理页面，打开 Logs。优先查看最后一段红色错误信息，通常能定位到缺依赖、入口文件错误或路径错误。

## 10. 常见错误

- `requirements.txt` 缺依赖：日志提示 `ModuleNotFoundError` 时，把缺失包加入依赖清单。
- 路径写死：云端没有本机盘符路径，所有资源必须通过相对路径访问。
- 文件大小太大：删除临时导出文件和无关素材，再重新部署。
- `app.py` 找不到：确认仓库根目录直接存在 `app.py`，或在部署页面正确填写入口路径。
- `assets` 路径错误：确认 `assets/outputs` 存在，导出逻辑使用相对路径。
- 导出文件无法长期保存：云端会话文件可能随重启清空，生成后应立即下载。
