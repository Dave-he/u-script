#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git代理设置脚本
跨平台的Git代理配置工具，支持设置、查看和取消Git代理
支持HTTP和SOCKS5代理协议
"""

import subprocess
import sys
import os


def run_command(command):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def get_current_proxy():
    """获取当前Git代理设置"""
    http_success, http_proxy, _ = run_command("git config --global --get http.proxy")
    https_success, https_proxy, _ = run_command("git config --global --get https.proxy")
    
    return {
        'http': http_proxy if http_success and http_proxy else None,
        'https': https_proxy if https_success and https_proxy else None
    }


def detect_proxy_protocol(proxy_url):
    """检测代理协议类型"""
    if proxy_url.startswith(('http://', 'https://', 'socks5://', 'socks4://')):
        return proxy_url
    else:
        # 如果没有协议前缀，需要用户选择
        return None


def set_proxy(proxy_url, protocol=None):
    """设置Git代理"""
    # 检测或设置协议
    if not detect_proxy_protocol(proxy_url):
        if protocol is None:
            print("\n🔧 请选择代理协议:")
            print("1. HTTP/HTTPS")
            print("2. SOCKS5")
            
            while True:
                protocol_choice = input("请输入选择 (1-2): ").strip()
                if protocol_choice == "1":
                    protocol = "http"
                    break
                elif protocol_choice == "2":
                    protocol = "socks5"
                    break
                else:
                    print("❌ 无效选择，请输入1-2")
        
        # 添加协议前缀
        if protocol == "http":
            full_proxy_url = f"http://{proxy_url}"
        elif protocol == "socks5":
            full_proxy_url = f"socks5://{proxy_url}"
        else:
            full_proxy_url = f"http://{proxy_url}"  # 默认使用HTTP
    else:
        full_proxy_url = proxy_url
    
    print(f"正在设置Git代理为: {full_proxy_url}")
    
    # 设置HTTP代理
    http_success, _, http_error = run_command(f"git config --global http.proxy '{full_proxy_url}'")
    if not http_success:
        print(f"设置HTTP代理失败: {http_error}")
        return False
    
    # 设置HTTPS代理
    https_success, _, https_error = run_command(f"git config --global https.proxy '{full_proxy_url}'")
    if not https_success:
        print(f"设置HTTPS代理失败: {https_error}")
        return False
    
    print("✅ Git代理设置成功！")
    return True


def unset_proxy():
    """取消Git代理设置"""
    print("正在取消Git代理设置...")
    
    # 取消HTTP代理
    http_success, _, http_error = run_command("git config --global --unset http.proxy")
    # 取消HTTPS代理
    https_success, _, https_error = run_command("git config --global --unset https.proxy")
    
    print("✅ Git代理已取消！")
    return True


def display_current_proxy():
    """显示当前代理设置"""
    proxy_config = get_current_proxy()
    
    print("\n📋 当前Git代理设置:")
    print("-" * 40)
    
    if proxy_config['http'] or proxy_config['https']:
        if proxy_config['http']:
            print(f"HTTP代理:  {proxy_config['http']}")
        if proxy_config['https']:
            print(f"HTTPS代理: {proxy_config['https']}")
    else:
        print("❌ 未设置代理")
    
    print("-" * 40)


def main():
    """主函数"""
    print("🔧 Git代理设置工具")
    print("=" * 50)
    
    # 检查Git是否可用
    git_available, _, _ = run_command("git --version")
    if not git_available:
        print("❌ 错误: 未找到Git，请确保Git已正确安装并添加到PATH环境变量中")
        sys.exit(1)
    
    # 显示当前代理设置
    display_current_proxy()
    
    # 获取当前代理配置
    proxy_config = get_current_proxy()
    has_proxy = proxy_config['http'] or proxy_config['https']
    
    print("\n🎯 请选择操作:")
    if has_proxy:
        print("1. 取消当前代理设置")
        print("2. 重新设置代理")
        print("3. 退出")
        
        while True:
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == "1":
                unset_proxy()
                break
            elif choice == "2":
                print("\n📝 代理地址格式说明:")
                print("  • HTTP代理: http://127.0.0.1:10808 或 127.0.0.1:10808")
                print("  • SOCKS5代理: socks5://127.0.0.1:10808")
                print("  • 如果不指定协议，将提示选择")
                proxy_url = input(f"\n请输入代理地址 (默认: 127.0.0.1:10808): ").strip()
                if not proxy_url:
                    proxy_url = "127.0.0.1:10808"
                set_proxy(proxy_url)
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
                print("  • HTTP代理: http://127.0.0.1:10808 或 127.0.0.1:10808")
                print("  • SOCKS5代理: socks5://127.0.0.1:10808")
                print("  • 如果不指定协议，将提示选择")
                proxy_url = input(f"\n请输入代理地址 (默认: 127.0.0.1:10808): ").strip()
                if not proxy_url:
                    proxy_url = "127.0.0.1:10808"
                set_proxy(proxy_url)
                break
            elif choice == "2":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入1-2")
    
    # 显示最终设置
    print("\n📋 最终Git代理设置:")
    display_current_proxy()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)