import os
import shutil
import crayons
from subprocess import check_call, check_output

from .adb import commands

BASEDIR = os.path.expanduser('~/.andy')

def root_device(device=None):
    commands.wait_for_device(device)
    check_call(commands.adb(device) + 'root', universal_newlines=True, shell=True)
    check_call(commands.adb(device) + 'remount', universal_newlines=True, shell=True)
    commands.push(os.path.join(BASEDIR, 'binaries/su/x86/su.pie'), '/system/xbin/su', device)
    check_call(commands.adb(device) + 'shell chmod 0755 /system/xbin/su', universal_newlines=True, shell=True)
    check_call(commands.adb(device) + 'shell su --install', universal_newlines=True, shell=True)
    check_call(commands.adb(device) + 'shell su --daemon&', universal_newlines=True, shell=True)
    check_call(commands.adb(device) + 'shell setenforce 0', universal_newlines=True, shell=True)
    commands.reboot(device)


def install_xposed(device=None):
    print(crayons.white('Installing Xposed framework', bold=True))
    installer = {
        19: 'xposed.installer_v33_36570c.apk'
    }
    api = int(commands.get_prop('ro.build.version.sdk', device))
    commands.install(os.path.join(BASEDIR,'framework/xposed/installer/%s' % installer.get(api, 'xposed.installer_3.1.2.apk')), device)
    if api > 19:
        xposed_dir = 'xposed-v88-sdk%s-x86' % api
        commands.push(os.path.join(BASEDIR, 'framework/xposed/sdk/%s' % xposed_dir), '/data/local/tmp/', device)
        check_call(commands.adb(device) + 'shell chmod 0755 /data/local/tmp/%s/flash-script.sh' % xposed_dir, shell=True)
        check_call(commands.adb(device) + 'shell "cd /data/local/tmp/%s/ && ./flash-script.sh"' % xposed_dir, shell=True)


def install_busybox(device=None):
    print(crayons.white('Installing Busybox', bold=True))
    commands.push(os.path.join(BASEDIR, 'binaries/busybox/x86/busybox'), '/system/xbin/', device)
    check_call(commands.adb(device) + 'shell chmod 0755 /system/xbin/busybox', shell=True)
    check_call(commands.adb(device) + 'shell "cd /system/xbin/ && busybox --install /system/xbin/"', shell=True)


def install_frida(device=None):
    print(crayons.white('Installing Frida', bold=True))
    commands.push(os.path.join(BASEDIR, 'binaries/frida/x86/frida-server'), '/data/local/tmp/', device)
    check_call(commands.adb(device) + 'shell chmod 0755 /data/local/tmp/frida-server', shell=True)


def install_apps(device=None):
    print(crayons.white('Installing apps', bold=True))
    for (dirpath, dirnames, filenames) in os.walk(BASEDIR):
        folder = os.path.basename(dirpath)
        if folder in ['apps', 'hooks']:
            for f in filenames:
                print(crayons.white('Installing %s' % crayons.white(f, bold=True), bold=True))
                commands.install(os.path.join(dirpath,f), device)


def bootstrap(device=None):
    commands.wait_for_device(device)
    install_busybox(device)
    install_frida(device)
    install_apps(device)
    install_xposed(device)
    print(crayons.white('All done!', bold=True))


def start_frida(device=None):
    check_call(commands.adb(device) + 'shell ./data/local/tmp/frida-server -D', shell=True)


def stop_frida(device=None):
    check_call(commands.adb(device) + 'shell pkill frida-server', shell=True)
