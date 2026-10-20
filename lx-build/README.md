# LX OriginOS ARM64 构建任务

仅在 `lx-originos-build` 分支 push 时运行；使用 GitHub 标准 `ubuntu-24.04` runner，45 分钟超时，只有 `contents: read` 权限。无部署、仓库写入、专用签名密钥或缓存上传。新提交会取消同组旧构建，避免重叠。

流程读取两个固定官方提交，应用完整应用补丁及播放器依赖补丁，然后运行定向检查和 ARM64 release 构建：

- LX：`fb8480728d875fa5e0da25eebd3a26bb71723aae`（v1.9.1）
- track-player：`bfe33933793460e7588d4d8f38eddf7910806f29`
- Node 20 / Java 17 / Gradle 8.8
- SDK Platform 36 / Build Tools 35.0.0 / NDK 26.1.10909125 / CMake 3.22.1

SDK 包仅在 runner 缺少时安装；用户已同意该构建所需 Android SDK 许可。只使用官方依赖服务，不设置镜像或代理绕过访问限制。

目标包名 `com.luna.music`，版本 `1.9.1-originos-queue1`，ARM64 versionCode `79003`。构建临时使用官方源码公开测试签名，不含最终安装包的专用私钥。产物仅为 APK 和 SHA256，artifact 保留 1 天。需要取回 APK，在原环境重新签名并验证后才适合覆盖已安装版本，不应让用户卸载当前可用应用。

## 验证范围

本地已通过完整补丁在原始固定提交上的应用验证，修改后文件逐字一致；定向队列/选曲/浏览结构测试、shell 语法、workflow 范围检查通过。此前 Metro release 打包与修改文件 ESLint 已通过。完整 TypeScript 检查仍有原始项目错误，不宣称全项目类型检查通过。

此次远端任务尚未运行。原环境原生构建因网络策略限制而未完成；不宣称已产出 APK 或 OriginOS 真机适配成功。

## Actions 锁定来源

2026-10-20 从以下官方仓库 `refs/tags/v4` 读取并固定完整提交：

- https://github.com/actions/checkout → `11d5960a326750d5838078e36cf38b85af677262`
- https://github.com/actions/setup-node → `49933ea5288caeca8642d1e84afbd3f7d6820020`
- https://github.com/actions/setup-java → `cf277c60eb25467037889841efdb72551f06f6c3`
- https://github.com/actions/upload-artifact → `ea165f8d65b6e75b540449e92b4886f43607fa02`

Apache-2.0 许可副本保存在 licenses。发布该任务文件必须先获仓库所有者同意；不要同时发布无关业务代码、构建缓存或签名材料。
