import json
import os
from typing import Optional, Dict, Any

class Settings:
    """
    配置管理类
    """
    
    def __init__(self):
        """
        初始化配置
        """
        self.config_path = os.path.join(os.path.dirname(__file__), "settings.json")
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """
        加载配置
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception:
            return {}
    
    def save_settings(self) -> bool:
        """
        保存配置
        
        Returns:
            bool: 是否成功
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            Any: 配置值
        """
        # 支持嵌套键，如 "keys.backup_test_key"
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        
        Returns:
            bool: 是否成功
        """
        try:
            # 支持嵌套键，如 "keys.backup_test_key"
            keys = key.split('.')
            settings = self.settings
            
            # 遍历键，创建嵌套字典
            for k in keys[:-1]:
                if k not in settings:
                    settings[k] = {}
                settings = settings[k]
            
            # 设置值
            settings[keys[-1]] = value
            
            # 保存配置
            return self.save_settings()
        except Exception:
            return False
    
    def remove(self, key: str) -> bool:
        """
        删除配置值
        
        Args:
            key: 配置键
        
        Returns:
            bool: 是否成功
        """
        try:
            # 支持嵌套键，如 "keys.backup_test_key"
            keys = key.split('.')
            settings = self.settings
            
            # 遍历键，找到要删除的键的父字典
            for k in keys[:-1]:
                if k not in settings:
                    return False
                settings = settings[k]
            
            # 删除键
            if keys[-1] in settings:
                del settings[keys[-1]]
                # 保存配置
                return self.save_settings()
            else:
                return False
        except Exception:
            return False

# 全局配置实例
settings = Settings()

# 导出常用函数
def get(key: str, default: Any = None) -> Any:
    """
    获取配置值
    
    Args:
        key: 配置键
        default: 默认值
    
    Returns:
        Any: 配置值
    """
    return settings.get(key, default)

def set(key: str, value: Any) -> bool:
    """
    设置配置值
    
    Args:
        key: 配置键
        value: 配置值
    
    Returns:
        bool: 是否成功
    """
    return settings.set(key, value)

def remove(key: str) -> bool:
    """
    删除配置值
    
    Args:
        key: 配置键
    
    Returns:
        bool: 是否成功
    """
    return settings.remove(key)

def save() -> bool:
    """
    保存配置
    
    Returns:
        bool: 是否成功
    """
    return settings.save_settings()
