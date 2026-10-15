#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志统计自动化脚本
功能：统计日志文件中的日志级别（INFO/WARN/ERROR/DEBUG）数量、访问IP频次
适用日志格式示例：
2026-01-04 10:00:00 [INFO] 192.168.1.100 - 用户登录成功
2026-01-04 10:01:00 [ERROR] 192.168.1.101 - 数据库连接失败
"""

def count_logs(log_file_path):
    """
    核心函数：读取日志文件并统计关键信息
    :param log_file_path: 日志文件的路径（如 "./app.log"）
    :return: 统计结果字典
    """
    # 初始化统计字典，默认值为0
    log_level_count = {
        "INFO": 0,
        "WARN": 0,
        "ERROR": 0,
        "DEBUG": 0,
        "UNKNOWN": 0  # 未识别的日志级别
    }
    ip_count = {}  # 统计IP访问频次，key=IP，value=次数
    line_num = 0

    try:
        # 打开日志文件，使用utf-8编码（避免中文乱码），errors='ignore'忽略无法解码的字符
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # 逐行读取日志
            for line_num, line in enumerate(f, start=1):
                # 去除行首行尾的空白字符（空格、换行符等）
                line = line.strip()
                # 跳过空行
                if not line:
                    continue

                # ========== 1. 提取日志级别 ==========
                # 日志级别格式为 [级别]，用字符串切片/分割提取
                level_start = line.find('[')
                level_end = line.find(']')
                if level_start != -1 and level_end != -1:
                    log_level = line[level_start+1:level_end].strip().upper()
                    # 判断是否是已知级别，否则归为UNKNOWN
                    if log_level in log_level_count:
                        log_level_count[log_level] += 1
                    else:
                        log_level_count["UNKNOWN"] += 1
                else:
                    log_level_count["UNKNOWN"] += 1

                # ========== 2. 提取IP地址 ==========
                # IP地址格式：日志级别后紧跟IP（如 [INFO] 192.168.1.100）
                # 先按空格分割行内容，过滤空字符串，找到符合IP格式的部分
                parts = [p for p in line.split() if p]
                ip = None
                # 遍历分割后的部分，判断是否是IP（简单判断：含3个点，且各段为数字）
                for part in parts:
                    if part.count('.') == 3:
                        ip_segments = part.split('.')
                        # 验证每段是否为数字且范围合法（简化版，仅做基础校验）
                        if all(seg.isdigit() and 0 <= int(seg) <= 255 for seg in ip_segments):
                            ip = part
                            break
                # 统计IP频次
                if ip:
                    if ip in ip_count:
                        ip_count[ip] += 1
                    else:
                        ip_count[ip] = 1

        # 整理统计结果
        result = {
            "log_level": log_level_count,
            "ip_count": ip_count,
            "total_lines": line_num  # 文件总行数；空行不计入级别和 IP 统计
        }
        return result

    except FileNotFoundError:
        print(f"错误：未找到日志文件 {log_file_path}")
        return None
    except Exception as e:
        print(f"读取日志文件时出错：{e}（行号：{line_num}）")
        return None

def print_report(result):
    """
    格式化输出统计报告
    :param result: count_logs函数返回的统计结果字典
    """
    if not result:
        print("无统计结果可输出")
        return

    print("=" * 50)
    print("日志统计报告")
    print("=" * 50)
    print(f"日志总行数：{result['total_lines']}")
    print("\n1. 日志级别统计：")
    for level, count in result['log_level'].items():
        print(f"   {level:6} : {count} 条")

    print("\n2. IP访问频次统计（按频次降序）：")
    # 将IP统计结果按频次从高到低排序
    sorted_ips = sorted(result['ip_count'].items(), key=lambda x: x[1], reverse=True)
    if sorted_ips:
        for ip, count in sorted_ips:
            print(f"   {ip:15} : {count} 次")
    else:
        print("   未识别到有效IP地址")
    print("=" * 50)

if __name__ == "__main__":
    # ********** 你需要修改的地方 **********
    # 设置你的日志文件路径（相对路径或绝对路径）
    LOG_FILE = "./app.log"  # 示例：当前目录下的app.log

    # 执行统计并输出报告
    stats_result = count_logs(LOG_FILE)
    print_report(stats_result)
