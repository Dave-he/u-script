#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统代理设置脚本
跨平台的系统代理配置工具，支持Windows、macOS和Linux
支持设置、查看和取消系统代理
默认使用本地10808端口
"""

import subprocess
import sys
import os
import platform
import json


class SystemProxyManager:
    """系统代理管理器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.default_proxy = "127.0.0.1:10808"
        
    def run_command(self, command, shell=True):
        """执行命令并返回结果"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def get_current_proxy_windows(self):
        """获取Windows当前代理设置"""
        try:
            # 查询注册表获取代理设置
            cmd = 'reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable'
            success, output, _ = self.run_command(cmd)
            
            if success and "0x1" in output:
                # 代理已启用，获取代理服务器
                cmd = 'reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer'
                success, output, _ = self.run_command(cmd)
                if success:
                    proxy_server = output.split()[-1] if output.split() else None
                    return True, proxy_server
            
            return False, None
        except Exception:
            return False, None
    
    def set_proxy_windows(self, proxy_url):
        """设置Windows系统代理"""
        try:
            # 启用代理
            cmd1 = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f'
            success1, _, _ = self.run_command(cmd1)
            
            # 设置代理服务器
            cmd2 = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d "{proxy_url}" /f'
            success2, _, _ = self.run_command(cmd2)
            
            if success1 and success2:
                # 刷新系统设置
                self.run_command('rundll32.exe inetcpl.cpl,LaunchConnectionDialog')
                return True
            return False
        except Exception:
            return False
    
    def unset_proxy_windows(self):
        """取消Windows系统代理"""
        try:
            # 禁用代理
            cmd = 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f'
            success, _, _ = self.run_command(cmd)
            
            if success:
                # 刷新系统设置
                self.run_command('rundll32.exe inetcpl.cpl,LaunchConnectionDialog')
                return True
            return False
        except Exception:
            return False
    
    def get_current_proxy_macos(self):
        """获取macOS当前代理设置"""
        try:
            # 获取当前网络服务
            cmd = "networksetup -listallnetworkservices | grep -v '*'"
            success, output, _ = self.run_command(cmd)
            
            if not success or not output:
                return False, None
            
            services = output.split('\n')
            for service in services:
                if service.strip():
                    # 检查HTTP代理
                    cmd = f'networksetup -getwebproxy "{service.strip()}"'
                    success, proxy_output, _ = self.run_command(cmd)
                    
                    if success and "Enabled: Yes" in proxy_output:
                        lines = proxy_output.split('\n')
                        server = None
                        port = None
                        
                        for line in lines:
                            if line.startswith('Server:'):
                                server = line.split(':', 1)[1].strip()
                            elif line.startswith('Port:'):
                                port = line.split(':', 1)[1].strip()
                        
                        if server and port:
                            return True, f"{server}:{port}"
            
            return False, None
        except Exception:
            return False, None
    
    def set_proxy_macos(self, proxy_url):
        """设置macOS系统代理"""
        try:
            host, port = proxy_url.split(':')
            
            # 获取当前网络服务
            cmd = "networksetup -listallnetworkservices | grep -v '*'"
            success, output, _ = self.run_command(cmd)
            
            if not success:
                return False
            
            services = output.split('\n')
            success_count = 0
            
            for service in services:
                if service.strip():
                    service_name = service.strip()
                    
                    # 设置HTTP代理
                    cmd1 = f'networksetup -setwebproxy "{service_name}" {host} {port}'
                    success1, _, _ = self.run_command(cmd1)
                    
                    # 设置HTTPS代理
                    cmd2 = f'networksetup -setsecurewebproxy "{service_name}" {host} {port}'
                    success2, _, _ = self.run_command(cmd2)
                    
                    if success1 and success2:
                        success_count += 1
            
            return success_count > 0
        except Exception:
            return False
    
    def unset_proxy_macos(self):
        """取消macOS系统代理"""
        try:
            # 获取当前网络服务
            cmd = "networksetup -listallnetworkservices | grep -v '*'"
            success, output, _ = self.run_command(cmd)
            
            if not success:
                return False
            
            services = output.split('\n')
            success_count = 0
            
            for service in services:
                if service.strip():
                    service_name = service.strip()
                    
                    # 关闭HTTP代理
                    cmd1 = f'networksetup -setwebproxystate "{service_name}" off'
                    success1, _, _ = self.run_command(cmd1)
                    
                    # 关闭HTTPS代理
                    cmd2 = f'networksetup -setsecurewebproxystate "{service_name}" off'
                    success2, _, _ = self.run_command(cmd2)
                    
                    if success1 and success2:
                        success_count += 1
            
            return success_count > 0
        except Exception:
            return False
    
    def get_current_proxy_linux(self):
        """获取Linux当前代理设置"""
        try:
            # 检查环境变量
            http_proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
            https_proxy = os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY')
            
            if http_proxy or https_proxy:
                proxy = http_proxy or https_proxy
                # 移除协议前缀
                if proxy.startswith(('http://', 'https://')):
                    proxy = proxy.split('://', 1)[1]
                return True, proxy
            
            return False, None
        except Exception:
            return False, None
    
    def set_proxy_linux(self, proxy_url):
        """设置Linux系统代理（通过环境变量）"""
        try:
            proxy_with_protocol = f"http://{proxy_url}"
            
            # 设置当前会话的环境变量
            os.environ['http_proxy'] = proxy_with_protocol
            os.environ['https_proxy'] = proxy_with_protocol
            os.environ['HTTP_PROXY'] = proxy_with_protocol
            os.environ['HTTPS_PROXY'] = proxy_with_protocol
            
            # 尝试写入到shell配置文件
            shell_configs = [
                os.path.expanduser('~/.bashrc'),
                os.path.expanduser('~/.zshrc'),
                os.path.expanduser('~/.profile')
            ]
            
            proxy_lines = [
                f'export http_proxy="{proxy_with_protocol}"',
                f'export https_proxy="{proxy_with_protocol}"',
                f'export HTTP_PROXY="{proxy_with_protocol}"',
                f'export HTTPS_PROXY="{proxy_with_protocol}"'
            ]
            
            for config_file in shell_configs:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            content = f.read()
                        
                        # 移除旧的代理设置
                        lines = content.split('\n')
                        new_lines = [line for line in lines if not any(
                            proxy_var in line for proxy_var in ['http_proxy=', 'https_proxy=', 'HTTP_PROXY=', 'HTTPS_PROXY=']
                        )]
                        
                        # 添加新的代理设置
                        new_lines.extend(proxy_lines)
                        
                        with open(config_file, 'w') as f:
                            f.write('\n'.join(new_lines))
                        
                        break
                    except Exception:
                        continue
            
            return True
        except Exception:
            return False
    
    def unset_proxy_linux(self):
        """取消Linux系统代理"""
        try:
            # 清除当前会话的环境变量
            for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
                if var in os.environ:
                    del os.environ[var]
            
            # 从shell配置文件中移除
            shell_configs = [
                os.path.expanduser('~/.bashrc'),
                os.path.expanduser('~/.zshrc'),
                os.path.expanduser('~/.profile')
            ]
            
            for config_file in shell_configs:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            content = f.read()
                        
                        # 移除代理设置行
                        lines = content.split('\n')
                        new_lines = [line for line in lines if not any(
                            proxy_var in line for proxy_var in ['http_proxy=', 'https_proxy=', 'HTTP_PROXY=', 'HTTPS_PROXY=']
                        )]
                        
                        with open(config_file, 'w') as f:
                            f.write('\n'.join(new_lines))
                        
                        break
                    except Exception:
                        continue
            
            return True
        except Exception:
            return False
    
    def get_current_proxy(self):
        """获取当前系统代理设置"""
        if self.system == "windows":
            return self.get_current_proxy_windows()
        elif self.system == "darwin":
            return self.get_current_proxy_macos()
        elif self.system == "linux":
            return self.get_current_proxy_linux()
        else:
            return False, None
    
    def set_proxy(self, proxy_url):
        """设置系统代理"""
        if self.system == "windows":
            return self.set_proxy_windows(proxy_url)
        elif self.system == "darwin":
            return self.set_proxy_macos(proxy_url)
        elif self.system == "linux":
            return self.set_proxy_linux(proxy_url)
        else:
            print(f"❌ 不支持的操作系统: {self.system}")
            return False
    
    def unset_proxy(self):
        """取消系统代理设置"""
        if self.system == "windows":
            return self.unset_proxy_windows()
        elif self.system == "darwin":
            return self.unset_proxy_macos()
        elif self.system == "linux":
            return self.unset_proxy_linux()
        else:
            print(f"❌ 不支持的操作系统: {self.system}")
            return False
    
    def display_current_proxy(self):
        """显示当前代理设置"""
        has_proxy, proxy_url = self.get_current_proxy()

        print(f"\n📋 当前系统代理设置 ({platform.system()}):")
        print("-" * 50)
        
        if has_proxy and proxy_url:
            print(f"✅ 代理已启用: {proxy_url}")
        else:
            print("❌ 未设置代理")
        
        print("-" * 50)


def main():
    """主函数"""
    print("🔧 系统代理设置工具")
    print("=" * 60)
    print(f"当前操作系统: {platform.system()}")
    
    # 创建代理管理器
    proxy_manager = SystemProxyManager()
    
    # 显示当前代理设置
    proxy_manager.display_current_proxy()
    
    # 获取当前代理配置
    has_proxy, current_proxy = proxy_manager.get_current_proxy()
    
    print("\n🎯 请选择操作:")
    if has_proxy:
        print("1. 取消当前代理设置")
        print("2. 重新设置代理")
        print("3. 退出")
        
        while True:
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == "1":
                print("正在取消系统代理设置...")
                if proxy_manager.unset_proxy():
                    print("✅ 系统代理已取消！")
                else:
                    print("❌ 取消代理失败")
                break
            elif choice == "2":
                print("\n📝 代理地址格式说明:")
                print("  • 格式: IP:端口 (例如: 127.0.0.1:10808)")
                print("  • 默认使用本地10808端口")
                proxy_url = input(f"\n请输入代理地址 (默认: {proxy_manager.default_proxy}): ").strip()
                if not proxy_url:
                    proxy_url = proxy_manager.default_proxy
                
                print(f"正在设置系统代理为: {proxy_url}")
                if proxy_manager.set_proxy(proxy_url):
                    print("✅ 系统代理设置成功！")
                    if proxy_manager.system == "linux":
                        print("💡 Linux系统提示: 请重新启动终端或执行 'source ~/.bashrc' 使代理生效")
                else:
                    print("❌ 设置代理失败")
                break
            elif choice == "3":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入1-3")
    else:
        print("1. 设置代理")
        print("2. 退出")
        
        while True:
            choice = input("\n请输入选择 (1-2): ").strip()
            
            if choice == "1":
                print("\n📝 代理地址格式说明:")
                print("  • 格式: IP:端口 (例如: 127.0.0.1:10808)")
                print("  • 默认使用本地10808端口")
                proxy_url = input(f"\n请输入代理地址 (默认: {proxy_manager.default_proxy}): ").strip()
                if not proxy_url:
                    proxy_url = proxy_manager.default_proxy
                
                print(f"正在设置系统代理为: {proxy_url}")
                if proxy_manager.set_proxy(proxy_url):
                    print("✅ 系统代理设置成功！")
                    if proxy_manager.system == "linux":
                        print("💡 Linux系统提示: 请重新启动终端或执行 'source ~/.bashrc' 使代理生效")
                else:
                    print("❌ 设置代理失败")
                break
            elif choice == "2":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入1-2")
    
    # 显示最终设置
    print("\n📋 最终系统代理设置:")
    proxy_manager.display_current_proxy()


if __name__ == "__main__":
    try:
        # 检查管理员权限（Windows需要）
        if platform.system().lower() == "windows":
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("⚠️  警告: Windows系统建议以管理员身份运行此脚本以确保代理设置生效")
                print("请右键点击命令提示符，选择'以管理员身份运行'")
                input("\n按回车键继续...")
        
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)