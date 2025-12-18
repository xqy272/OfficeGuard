"""
加密模块
使用 Windows DPAPI 进行数据加密/解密
"""

import base64
import ctypes
from ctypes import wintypes
from .logger import get_logger

logger = get_logger('crypto')

# Windows API
kernel32 = ctypes.windll.kernel32


class DATA_BLOB(ctypes.Structure):
    """DPAPI 数据结构"""
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', ctypes.POINTER(ctypes.c_char))
    ]


def encrypt_data(data_str: str) -> str | None:
    """
    使用 Windows DPAPI 加密数据
    DPAPI 使用用户凭据加密，只有当前用户可以解密
    
    :param data_str: 要加密的字符串
    :return: Base64编码的加密数据，失败返回None
    """
    try:
        # 转换为字节
        data_bytes = data_str.encode('utf-8')
        
        # 输入数据
        blob_in = DATA_BLOB()
        blob_in.cbData = len(data_bytes)
        blob_in.pbData = ctypes.cast(
            ctypes.c_char_p(data_bytes), 
            ctypes.POINTER(ctypes.c_char)
        )
        
        # 输出数据
        blob_out = DATA_BLOB()
        
        # 调用 CryptProtectData
        crypt32 = ctypes.windll.crypt32
        if crypt32.CryptProtectData(
            ctypes.byref(blob_in),
            None,  # 描述
            None,  # 可选熵
            None,  # 保留
            None,  # 提示结构
            0,     # 标志
            ctypes.byref(blob_out)
        ):
            # 获取加密数据
            encrypted_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            # 释放内存
            kernel32.LocalFree(blob_out.pbData)
            # Base64编码
            return base64.b64encode(encrypted_bytes).decode('ascii')
        else:
            logger.error("DPAPI加密失败")
            return None
    except Exception as e:
        logger.error(f"数据加密异常: {e}")
        return None


def decrypt_data(encrypted_str: str) -> str | None:
    """
    使用 Windows DPAPI 解密数据
    
    :param encrypted_str: Base64编码的加密数据
    :return: 解密后的字符串，失败返回None
    """
    try:
        # Base64解码
        encrypted_bytes = base64.b64decode(encrypted_str)
        
        # 输入数据
        blob_in = DATA_BLOB()
        blob_in.cbData = len(encrypted_bytes)
        blob_in.pbData = ctypes.cast(
            ctypes.c_char_p(encrypted_bytes), 
            ctypes.POINTER(ctypes.c_char)
        )
        
        # 输出数据
        blob_out = DATA_BLOB()
        
        # 调用 CryptUnprotectData
        crypt32 = ctypes.windll.crypt32
        if crypt32.CryptUnprotectData(
            ctypes.byref(blob_in),
            None,  # 描述
            None,  # 可选熵
            None,  # 保留
            None,  # 提示结构
            0,     # 标志
            ctypes.byref(blob_out)
        ):
            # 获取解密数据
            decrypted_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            # 释放内存
            kernel32.LocalFree(blob_out.pbData)
            # 转换为字符串
            return decrypted_bytes.decode('utf-8')
        else:
            logger.error("DPAPI解密失败")
            return None
    except Exception as e:
        logger.error(f"数据解密异常: {e}")
        return None
