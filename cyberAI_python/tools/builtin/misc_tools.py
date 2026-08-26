"""
杂项工具族(约15个)
"""
import logging
logger = logging.getLogger(__name__)

def dns_lookup(domain: str, record_type: str = "A") -> str:
    raise NotImplementedError

def whois_query(domain: str) -> str:
    raise NotImplementedError

def port_check(host: str, ports: str) -> str:
    raise NotImplementedError

def json_format(data: str) -> str:
    raise NotImplementedError

__all__ = ["dns_lookup", "whois_query", "port_check", "json_format"]
