SKIPMOUNT=true
PREFIX=/data/data/com.termux/files/usr
[ "$ARCH" = arm64 ] || abort "This module requires arm64."
[ "$API" -ge 31 ] || abort "This module requires Android API 31 or newer."
[ -x "$PREFIX/bin/python" ] || abort "Termux Python with tomllib is required."
[ -s /data/adb/samba/config.toml ] || abort "Existing private module configuration is required."
"$PREFIX/bin/python" "$MODPATH/validate-config.py" || abort "Invalid Samba or module configuration."
set_perm_recursive "$MODPATH" 0 0 0700 0600
set_perm "$MODPATH/service.sh" 0 0 0700
set_perm "$MODPATH/libheap-untag.so" 0 0 0700
set_perm "$MODPATH/module.prop" 0 0 0644
ui_print "Existing credentials and shared storage are preserved."
ui_print "Starts after first unlock and configured interface IPv4 availability."
ui_print "Reboot after disabling or uninstalling. Termux must remain installed."
