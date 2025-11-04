# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
Date: 2024/12/12 18:00
Desc: 工具函数
"""
from functools import lru_cache
import os
import requests


@lru_cache()
def get_latest_version(package: str = "akshare") -> str:
    """
    获取开源库的最新版本
    https://pypi.org/project/akshare/
    :param package: 库名称
    :type package: str
    :return: 版本
    :rtype: str
    """
    url = f"https://pypi.org/pypi/{package}/json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ProxyError:
        return "0.0.0"
    data_json = r.json()
    version = data_json['info']['version']
    return version


def disable_http_proxies() -> None:
    """
    禁用系统级 HTTP/HTTPS 代理环境变量，避免第三方数据源访问受代理影响

    param 无
    return None
    raises None

    说明：
    - Requests 默认会读取环境变量中的代理配置（如 HTTP_PROXY/HTTPS_PROXY/ALL_PROXY）
    - 在企业网络或系统设置了全局代理情况下，可能导致外网 API 请求失败（如 ProxyError）
    - 该函数在应用启动时调用，统一屏蔽代理并设置 NO_PROXY，确保外部数据请求直连
    """
    proxy_keys = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ]
    for key in proxy_keys:
        os.environ.pop(key, None)
    # 最大化禁止代理影响；'*' 表示所有域名均不走代理
    os.environ["NO_PROXY"] = "*"
