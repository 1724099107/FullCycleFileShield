#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离线环境维护机制
负责管理离线环境的依赖更新、版本控制和问题反馈
"""

import os
import sys
import json
import logging
import shutil
import datetime
from typing import Dict, List, Optional, Any

# 配置日志
script_dir = os.path.dirname(__file__)
log_file = os.path.join(script_dir, 'offline_maintenance.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_file
)
logger = logging.getLogger('OfflineMaintenance')

class OfflineMaintenanceManager:
    """
    离线环境维护管理器
    负责管理离线环境的依赖更新、版本控制和问题反馈
    """
    
    def __init__(self):
        """
        初始化离线环境维护管理器
        """
        self.project_root = script_dir
        self.dependencies_dir = os.path.join(self.project_root, 'dependencies')
        self.maintenance_config_path = os.path.join(self.project_root, 'offline_maintenance_config.json')
        self.version_history_path = os.path.join(self.dependencies_dir, 'version_history.json')
        self.feedback_path = os.path.join(self.project_root, 'feedback')
        
        # 创建必要的目录
        os.makedirs(self.dependencies_dir, exist_ok=True)
        os.makedirs(self.feedback_path, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        self.version_history = self._load_version_history()
        
        logger.info(f"离线维护管理器初始化完成")
        logger.info(f"项目根目录: {self.project_root}")
        logger.info(f"依赖目录: {self.dependencies_dir}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载维护配置
        
        Returns:
            Dict[str, Any]: 维护配置
        """
        default_config = {
            'dependency_update_interval': '30d',  # 依赖更新间隔
            'version_check_interval': '7d',  # 版本检查间隔
            'backup_retention': 5,  # 备份保留数量
            'auto_cleanup': True,  # 自动清理
            'notification_enabled': True,  # 通知启用
            'feedback_email': '',  # 反馈邮箱
            'last_update_check': None,  # 上次更新检查时间
            'last_version_check': None  # 上次版本检查时间
        }
        
        if os.path.exists(self.maintenance_config_path):
            try:
                with open(self.maintenance_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
                return default_config
        else:
            return default_config
    
    def _save_config(self):
        """
        保存维护配置
        """
        try:
            with open(self.maintenance_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def _load_version_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        加载版本历史
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 版本历史
        """
        if os.path.exists(self.version_history_path):
            try:
                with open(self.version_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载版本历史失败: {e}")
                return {}
        else:
            return {}
    
    def _save_version_history(self):
        """
        保存版本历史
        """
        try:
            with open(self.version_history_path, 'w', encoding='utf-8') as f:
                json.dump(self.version_history, f, indent=2, ensure_ascii=False)
            logger.info("版本历史已保存")
        except Exception as e:
            logger.error(f"保存版本历史失败: {e}")
    
    def check_dependency_updates(self) -> Dict[str, Any]:
        """
        检查依赖更新
        
        Returns:
            Dict[str, Any]: 更新检查结果
        """
        logger.info("开始检查依赖更新...")
        
        # 检查上次更新时间
        last_update = self.config.get('last_update_check')
        if last_update:
            last_date = datetime.datetime.fromisoformat(last_update)
            days_since = (datetime.datetime.now() - last_date).days
            if days_since < int(self.config['dependency_update_interval'].replace('d', '')):
                logger.info(f"更新检查间隔未到，上次检查时间: {last_update}")
                return {
                    'status': 'skipped',
                    'reason': '更新检查间隔未到',
                    'last_check': last_update
                }
        
        # 检查依赖版本
        update_needed = False
        outdated_dependencies = []
        
        # 读取当前依赖清单
        manifest_path = os.path.join(self.dependencies_dir, 'dependency_manifest.json')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                # 模拟检查更新（实际环境中需要联网检查）
                for dep in manifest.get('dependencies', []):
                    # 这里可以添加实际的版本检查逻辑
                    # 例如从PyPI API获取最新版本
                    # 由于是离线环境，这里只是记录检查
                    outdated_dependencies.append({
                        'name': dep['name'],
                        'current_version': dep['version'],
                        'latest_version': dep['version'],  # 模拟，实际需要联网获取
                        'update_available': False
                    })
                
            except Exception as e:
                logger.error(f"检查依赖更新失败: {e}")
        
        # 更新检查时间
        self.config['last_update_check'] = datetime.datetime.now().isoformat()
        self._save_config()
        
        result = {
            'status': 'completed',
            'check_time': datetime.datetime.now().isoformat(),
            'outdated_dependencies': outdated_dependencies,
            'update_needed': update_needed
        }
        
        logger.info(f"依赖更新检查完成，需要更新: {update_needed}")
        return result
    
    def update_dependencies(self, dependencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        更新依赖
        
        Args:
            dependencies: 要更新的依赖列表，None表示更新所有
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        logger.info(f"开始更新依赖: {dependencies}")
        
        # 创建备份
        backup_result = self._create_backup()
        if not backup_result['success']:
            return {
                'status': 'failed',
                'reason': '备份失败',
                'backup_result': backup_result
            }
        
        # 模拟依赖更新（实际环境中需要联网下载）
        updated_dependencies = []
        failed_dependencies = []
        
        # 读取当前依赖清单
        manifest_path = os.path.join(self.dependencies_dir, 'dependency_manifest.json')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                for dep in manifest.get('dependencies', []):
                    if dependencies is None or dep['name'] in dependencies:
                        # 模拟更新成功
                        updated_dependencies.append(dep['name'])
                        
                        # 记录版本历史
                        if dep['name'] not in self.version_history:
                            self.version_history[dep['name']] = []
                        
                        self.version_history[dep['name']].append({
                            'version': dep['version'],
                            'update_time': datetime.datetime.now().isoformat(),
                            'status': 'updated'
                        })
                
            except Exception as e:
                logger.error(f"更新依赖失败: {e}")
                failed_dependencies.append(str(e))
        
        # 保存版本历史
        self._save_version_history()
        
        # 清理旧备份
        self._cleanup_backups()
        
        result = {
            'status': 'completed' if not failed_dependencies else 'partial',
            'updated': updated_dependencies,
            'failed': failed_dependencies,
            'backup_created': backup_result['backup_path']
        }
        
        logger.info(f"依赖更新完成，成功: {len(updated_dependencies)}, 失败: {len(failed_dependencies)}")
        return result
    
    def _create_backup(self) -> Dict[str, Any]:
        """
        创建依赖备份
        
        Returns:
            Dict[str, Any]: 备份结果
        """
        logger.info("创建依赖备份...")
        
        backup_dir = os.path.join(self.dependencies_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            # 复制当前依赖到备份目录
            shutil.copytree(os.path.join(self.dependencies_dir, 'production'), 
                           os.path.join(backup_path, 'production'))
            shutil.copytree(os.path.join(self.dependencies_dir, 'development'), 
                           os.path.join(backup_path, 'development'))
            
            # 复制依赖清单
            manifest_path = os.path.join(self.dependencies_dir, 'dependency_manifest.json')
            if os.path.exists(manifest_path):
                shutil.copy2(manifest_path, backup_path)
            
            logger.info(f"备份创建成功: {backup_path}")
            return {
                'success': True,
                'backup_path': backup_path
            }
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _cleanup_backups(self):
        """
        清理旧备份
        """
        backup_dir = os.path.join(self.dependencies_dir, 'backups')
        if not os.path.exists(backup_dir):
            return
        
        try:
            # 获取所有备份
            backups = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) 
                      if os.path.isdir(os.path.join(backup_dir, f))]
            
            # 按创建时间排序
            backups.sort(key=os.path.getctime, reverse=True)
            
            # 保留指定数量的备份
            retention = self.config['backup_retention']
            if len(backups) > retention:
                for backup in backups[retention:]:
                    shutil.rmtree(backup)
                    logger.info(f"清理旧备份: {backup}")
        except Exception as e:
            logger.error(f"清理备份失败: {e}")
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """
        恢复备份
        
        Args:
            backup_path: 备份路径
            
        Returns:
            Dict[str, Any]: 恢复结果
        """
        logger.info(f"开始恢复备份: {backup_path}")
        
        if not os.path.exists(backup_path):
            return {
                'status': 'failed',
                'reason': '备份路径不存在'
            }
        
        try:
            # 停止程序（如果正在运行）
            # 这里可以添加停止程序的逻辑
            
            # 备份当前状态
            temp_backup = self._create_backup()
            
            # 恢复依赖
            production_backup = os.path.join(backup_path, 'production')
            development_backup = os.path.join(backup_path, 'development')
            
            if os.path.exists(production_backup):
                shutil.rmtree(os.path.join(self.dependencies_dir, 'production'), ignore_errors=True)
                shutil.copytree(production_backup, os.path.join(self.dependencies_dir, 'production'))
            
            if os.path.exists(development_backup):
                shutil.rmtree(os.path.join(self.dependencies_dir, 'development'), ignore_errors=True)
                shutil.copytree(development_backup, os.path.join(self.dependencies_dir, 'development'))
            
            # 恢复依赖清单
            backup_manifest = os.path.join(backup_path, 'dependency_manifest.json')
            if os.path.exists(backup_manifest):
                shutil.copy2(backup_manifest, os.path.join(self.dependencies_dir, 'dependency_manifest.json'))
            
            logger.info(f"备份恢复成功: {backup_path}")
            return {
                'status': 'completed',
                'backup_path': backup_path,
                'temp_backup': temp_backup['backup_path'] if temp_backup['success'] else None
            }
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def submit_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        提交反馈
        
        Args:
            feedback: 反馈信息
            
        Returns:
            Dict[str, Any]: 提交结果
        """
        logger.info(f"提交反馈: {feedback.get('type', 'unknown')}")
        
        feedback_id = f"feedback_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        feedback_path = os.path.join(self.feedback_path, f"{feedback_id}.json")
        
        try:
            feedback_data = {
                'id': feedback_id,
                'timestamp': datetime.datetime.now().isoformat(),
                'type': feedback.get('type', 'general'),
                'subject': feedback.get('subject', ''),
                'description': feedback.get('description', ''),
                'severity': feedback.get('severity', 'low'),
                'environment': {
                    'python_version': sys.version,
                    'os': os.name,
                    'platform': sys.platform
                },
                'attachments': feedback.get('attachments', [])
            }
            
            with open(feedback_path, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"反馈提交成功: {feedback_id}")
            return {
                'status': 'completed',
                'feedback_id': feedback_id,
                'path': feedback_path
            }
        except Exception as e:
            logger.error(f"提交反馈失败: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def get_feedback_list(self) -> List[Dict[str, Any]]:
        """
        获取反馈列表
        
        Returns:
            List[Dict[str, Any]]: 反馈列表
        """
        feedback_list = []
        
        try:
            for filename in os.listdir(self.feedback_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.feedback_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            feedback = json.load(f)
                        feedback_list.append(feedback)
                    except Exception as e:
                        logger.error(f"读取反馈文件失败: {filename}, {e}")
            
            # 按时间排序
            feedback_list.sort(key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            logger.error(f"获取反馈列表失败: {e}")
        
        return feedback_list
    
    def run_maintenance(self) -> Dict[str, Any]:
        """
        运行维护任务
        
        Returns:
            Dict[str, Any]: 维护结果
        """
        logger.info("开始运行维护任务...")
        
        tasks = {
            'dependency_update_check': self.check_dependency_updates(),
            'backup_cleanup': self._cleanup_backups(),
            'version_check': self._check_versions()
        }
        
        result = {
            'status': 'completed',
            'run_time': datetime.datetime.now().isoformat(),
            'tasks': tasks
        }
        
        logger.info("维护任务运行完成")
        return result
    
    def _check_versions(self) -> Dict[str, Any]:
        """
        检查版本一致性
        
        Returns:
            Dict[str, Any]: 检查结果
        """
        logger.info("检查版本一致性...")
        
        # 检查上次版本检查时间
        last_check = self.config.get('last_version_check')
        if last_check:
            last_date = datetime.datetime.fromisoformat(last_check)
            days_since = (datetime.datetime.now() - last_date).days
            if days_since < int(self.config['version_check_interval'].replace('d', '')):
                return {
                    'status': 'skipped',
                    'reason': '版本检查间隔未到'
                }
        
        # 检查版本一致性
        issues = []
        
        # 读取依赖清单
        manifest_path = os.path.join(self.dependencies_dir, 'dependency_manifest.json')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                # 检查每个依赖的版本一致性
                for dep in manifest.get('dependencies', []):
                    # 这里可以添加实际的版本检查逻辑
                    # 例如检查本地安装的版本与清单中的版本是否一致
                    pass
                
            except Exception as e:
                logger.error(f"检查版本一致性失败: {e}")
                issues.append(str(e))
        
        # 更新检查时间
        self.config['last_version_check'] = datetime.datetime.now().isoformat()
        self._save_config()
        
        return {
            'status': 'completed',
            'issues': issues,
            'check_time': datetime.datetime.now().isoformat()
        }

# 全局离线维护管理器实例
OFFLINE_MAINTENANCE = OfflineMaintenanceManager()

# 初始化离线维护
def init_offline_maintenance():
    """
    初始化离线维护
    """
    logger.info("初始化离线维护...")
    return OFFLINE_MAINTENANCE

# 运行维护任务
def run_maintenance():
    """
    运行维护任务
    
    Returns:
        Dict[str, Any]: 维护结果
    """
    return OFFLINE_MAINTENANCE.run_maintenance()

# 检查依赖更新
def check_dependency_updates():
    """
    检查依赖更新
    
    Returns:
        Dict[str, Any]: 更新检查结果
    """
    return OFFLINE_MAINTENANCE.check_dependency_updates()

# 更新依赖
def update_dependencies(dependencies=None):
    """
    更新依赖
    
    Args:
        dependencies: 要更新的依赖列表
        
    Returns:
        Dict[str, Any]: 更新结果
    """
    return OFFLINE_MAINTENANCE.update_dependencies(dependencies)

# 提交反馈
def submit_feedback(feedback):
    """
    提交反馈
    
    Args:
        feedback: 反馈信息
        
    Returns:
        Dict[str, Any]: 提交结果
    """
    return OFFLINE_MAINTENANCE.submit_feedback(feedback)

if __name__ == "__main__":
    # 测试离线维护功能
    print("测试离线维护功能...")
    
    # 运行维护任务
    maintenance_result = run_maintenance()
    print(f"维护任务结果: {json.dumps(maintenance_result, indent=2, ensure_ascii=False)}")
    
    # 检查依赖更新
    update_result = check_dependency_updates()
    print(f"依赖更新检查结果: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
    
    # 提交测试反馈
    feedback_result = submit_feedback({
        'type': 'test',
        'subject': '测试反馈',
        'description': '这是一条测试反馈',
        'severity': 'low'
    })
    print(f"反馈提交结果: {json.dumps(feedback_result, indent=2, ensure_ascii=False)}")
    
    print("测试完成")
