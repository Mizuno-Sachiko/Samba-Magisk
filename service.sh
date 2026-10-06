#!/system/bin/sh
MODDIR=${0%/*}
# Credential-encrypted Termux files and shared storage need the first unlock.
while [ "$(getprop sys.boot_completed)" != "1" ] || \
      [ "$(getprop sys.user.0.ce_available)" != "true" ]; do
    sleep 5
done
[ ! -f "$MODDIR/disable" ] || exit 0
umask 077
exec /data/data/com.termux/files/usr/bin/python -u "$MODDIR/watch.py" \
    > /data/adb/samba/log/module-launch.log 2>&1
