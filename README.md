# Samba for Magisk

通过Magisk管理Termux Samba，在指定网卡上提供加密SMB3文件共享。

[下载模块](https://github.com/Mizuno-Sachiko/Samba-Magisk/releases/latest) · [配置示例](config.example.toml) · [GPL-3.0](LICENSE)

需要arm64设备、Android API31+、Magisk，以及Termux中的Samba和Python3.11+。

私有配置保存在`/data/adb/samba/config.toml`，共享规则见[smb.conf示例](smb.conf.example)。

准备好配置、账户库和状态目录后安装模块并重启，首次解锁后启动共享。以后可在Magisk内检查并安装更新。

推送`v主版本.次版本.修订版本`标签后，GitHub Actions自动编译、打包并发布Release。

安装器来自[Magisk](https://github.com/topjohnwu/Magisk)，采用GPL-3.0许可；项目许可证全文见[LICENSE](LICENSE)。
