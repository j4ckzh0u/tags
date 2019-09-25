import errno, os
import winreg
# proc_arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
# # proc_arch64 = os.environ['PROCESSOR_ARCHITEW6432'].lower()
#
# # if proc_arch == 'x86' and not proc_arch64:
# #     arch_keys = {0}
# # elif proc_arch == 'x86' or proc_arch == 'amd64':
# if proc_arch == 'x86' or proc_arch == 'amd64':
#     # arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
#     arch_keys = {0}
# else:
#     raise Exception("Unhandled arch: %s" % proc_arch)
#
# for arch_key in arch_keys:
#     key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\FusionInventory-Agent", 0, winreg.KEY_READ | arch_key)
#     for i in range(0, winreg.QueryInfoKey(key)[0]):
#         skey_name = winreg.EnumKey(key, i)
#         skey = winreg.OpenKey(key, skey_name)
#         try:
#             print(winreg.QueryValueEx(skey, 'server')[0])
#         except OSError as e:
#             if e.errno == errno.ENOENT:
#                 # DisplayName doesn't exist in this skey
#                 pass
#         finally:
#             skey.Close()

reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

reg_keys = winreg.OpenKey(reg_conn, r"SOFTWARE\FusionInventory-Agent")

try:
    i = 0
    while True:
        n, v, t = winreg.EnumValue(reg_keys, i)
        # print(n)
        print(repr(n), "=", repr(v))
        # print(v)
        i += 1
except EnvironmentError:
    print("-----------------------")
    print("ALL Keys has been read")

v,t = winreg.QueryValueEx(reg_keys, "server")
print("server:", v)