# Samba for Magisk

通过Magisk管理Termux Samba，在指定网卡上提供加密SMB3文件共享。

[下载模块](https://github.com/Mizuno-Sachiko/Samba-Magisk/releases/latest) · [配置示例](config.example.toml) · [GPL-3.0](LICENSE)

需要arm64设备、Android API31+、Magisk，以及Termux中的Samba和Python3.11+。

私有配置保存在`/data/adb/samba/config.toml`，共享规则见[smb.conf示例](smb.conf.example)。

准备好配置、账户库和状态目录后安装模块并重启，首次解锁后模块自动启动；支持Magisk在线更新。

项目采用GPL-3.0许可；安装器来自[Magisk](https://github.com/topjohnwu/Magisk)，许可证全文见[LICENSE](LICENSE)。
