"""
定时任务调度器 - 实现定时收集和总结功能
"""

import os
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from pathlib import Path


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self, storage_dir: str = './tasks'):
        self.tasks: Dict[str, Dict] = {}
        self.running = False
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.task_file = self.storage_dir / 'scheduled_tasks.json'
        
        # 加载已保存的任务
        self._load_tasks()
    
    def _load_tasks(self):
        """加载已保存的任务"""
        if self.task_file.exists():
            try:
                with open(self.task_file, 'r', encoding='utf-8') as f:
                    saved_tasks = json.load(f)
                    for task_id, task_data in saved_tasks.items():
                        # 只加载未完成的任务
                        if task_data.get('status') != 'completed':
                            self.tasks[task_id] = task_data
            except Exception as e:
                print(f"加载任务失败: {e}")
    
    def _save_tasks(self):
        """保存任务到文件"""
        try:
            with open(self.task_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务失败: {e}")
    
    def schedule_task(
        self,
        task_id: str,
        task_type: str,
        schedule_time: datetime,
        params: Dict,
        repeat: str = 'once',
        callback: Optional[Callable] = None
    ):
        """
        创建定时任务
        
        Args:
            task_id: 任务唯一ID
            task_type: 任务类型 ('collect', 'summarize', 'report')
            schedule_time: 执行时间
            params: 任务参数
            repeat: 重复模式 ('once', 'daily', 'weekly', 'monthly')
            callback: 完成后的回调函数
        """
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'schedule_time': schedule_time.isoformat(),
            'params': params,
            'repeat': repeat,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'next_run': schedule_time.isoformat(),
            'run_count': 0
        }
        
        self.tasks[task_id] = task
        self._save_tasks()
        
        print(f"✓ 任务已创建: {task_id}")
        print(f"  类型: {task_type}")
        print(f"  执行时间: {schedule_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  重复模式: {repeat}")
        
        return task
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            print(f"✓ 任务已取消: {task_id}")
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务详情"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """
        列出任务
        
        Args:
            status: 过滤状态 ('pending', 'running', 'completed', 'failed')
        """
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.get('status') == status]
        
        # 按执行时间排序
        tasks.sort(key=lambda x: x.get('next_run', ''))
        
        return tasks
    
    def _calculate_next_run(self, task: Dict) -> Optional[datetime]:
        """计算下次执行时间"""
        repeat = task.get('repeat', 'once')
        
        if repeat == 'once':
            return None
        
        last_run = datetime.fromisoformat(task['last_run']) if task.get('last_run') else \
                   datetime.fromisoformat(task['schedule_time'])
        
        if repeat == 'daily':
            return last_run + timedelta(days=1)
        elif repeat == 'weekly':
            return last_run + timedelta(weeks=1)
        elif repeat == 'monthly':
            # 简单处理：加30天
            return last_run + timedelta(days=30)
        
        return None
    
    def _execute_task(self, task: Dict):
        """执行任务"""
        task_id = task['task_id']
        task_type = task['task_type']
        params = task.get('params', {})
        
        print(f"\n{'='*60}")
        print(f"开始执行任务: {task_id}")
        print(f"类型: {task_type}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*60)
        
        self.tasks[task_id]['status'] = 'running'
        self._save_tasks()
        
        try:
            if task_type == 'collect':
                # 执行收集任务
                self._run_collect_task(params)
            elif task_type == 'summarize':
                # 执行总结任务
                self._run_summarize_task(params)
            elif task_type == 'report':
                # 执行报告任务
                self._run_report_task(params)
            
            # 更新任务状态
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['last_run'] = datetime.now().isoformat()
            self.tasks[task_id]['run_count'] += 1
            
            # 计算下次执行时间
            next_run = self._calculate_next_run(task)
            if next_run:
                self.tasks[task_id]['next_run'] = next_run.isoformat()
                self.tasks[task_id]['status'] = 'pending'
            
            print(f"\n✓ 任务完成: {task_id}")
            
        except Exception as e:
            print(f"\n✗ 任务失败: {e}")
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['error'] = str(e)
        
        self._save_tasks()
    
    def _run_collect_task(self, params: Dict):
        """运行收集任务"""
        url = params.get('url')
        url_file = params.get('url_file')
        
        if url_file and os.path.exists(url_file):
            # 从文件读取URL
            with open(url_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            # 调用主程序
            cmd = ['python3', 'collector.py', '--file', url_file]
        elif url:
            cmd = ['python3', 'collector.py', '--url', url]
        else:
            raise ValueError("未指定URL或URL文件")
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode != 0:
            raise Exception(result.stderr)
    
    def _run_summarize_task(self, params: Dict):
        """运行总结任务"""
        # 调用总结生成器
        cmd = ['python3', 'summarizer.py']
        
        if params.get('days'):
            cmd.extend(['--days', str(params['days'])])
        
        if params.get('app_token'):
            cmd.extend(['--app-token', params['app_token']])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode != 0:
            raise Exception(result.stderr)
    
    def _run_report_task(self, params: Dict):
        """运行报告任务"""
        # 生成并发送报告
        cmd = ['python3', 'reporter.py']
        
        if params.get('app_token'):
            cmd.extend(['--app-token', params['app_token']])
        
        if params.get('email'):
            cmd.extend(['--email', params['email']])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode != 0:
            raise Exception(result.stderr)
    
    def run(self):
        """启动调度器"""
        self.running = True
        print("定时任务调度器已启动")
        print(f"当前待执行任务数: {len(self.tasks)}")
        
        while self.running:
            try:
                now = datetime.now()
                
                # 检查是否有需要执行的任务
                for task_id, task in list(self.tasks.items()):
                    if task.get('status') != 'pending':
                        continue
                    
                    next_run = datetime.fromisoformat(task.get('next_run', '9999-12-31'))
                    
                    if now >= next_run:
                        # 执行任务
                        self._execute_task(task)
                
                # 每60秒检查一次
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n调度器已停止")
                self.running = False
                break
            except Exception as e:
                print(f"调度器错误: {e}")
                time.sleep(60)
    
    def stop(self):
        """停止调度器"""
        self.running = False


def create_quick_task(
    task_type: str,
    params: Dict,
    delay_minutes: int = 0,
    schedule_time: Optional[datetime] = None,
    repeat: str = 'once'
) -> str:
    """
    快速创建任务的便捷函数
    
    Args:
        task_type: 任务类型
        params: 任务参数
        delay_minutes: 延迟执行分钟数（如果未指定schedule_time）
        schedule_time: 执行时间
        repeat: 重复模式
    
    Returns:
        任务ID
    """
    scheduler = TaskScheduler()
    
    if schedule_time is None:
        schedule_time = datetime.now() + timedelta(minutes=delay_minutes)
    
    task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    scheduler.schedule_task(
        task_id=task_id,
        task_type=task_type,
        schedule_time=schedule_time,
        params=params,
        repeat=repeat
    )
    
    return task_id


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='定时任务管理')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 创建任务
    create_parser = subparsers.add_parser('create', help='创建定时任务')
    create_parser.add_argument('--type', required=True, 
                              choices=['collect', 'summarize', 'report'],
                              help='任务类型')
    create_parser.add_argument('--time', required=True,
                              help='执行时间 (YYYY-MM-DD HH:MM)')
    create_parser.add_argument('--url', help='文章URL')
    create_parser.add_argument('--url-file', help='URL文件')
    create_parser.add_argument('--repeat', default='once',
                              choices=['once', 'daily', 'weekly', 'monthly'],
                              help='重复模式')
    create_parser.add_argument('--days', type=int, help='总结天数')
    
    # 列出任务
    list_parser = subparsers.add_parser('list', help='列出任务')
    list_parser.add_argument('--status', choices=['pending', 'running', 'completed', 'failed'])
    
    # 取消任务
    cancel_parser = subparsers.add_parser('cancel', help='取消任务')
    cancel_parser.add_argument('task_id', help='任务ID')
    
    # 启动调度器
    run_parser = subparsers.add_parser('run', help='启动调度器')
    
    args = parser.parse_args()
    
    scheduler = TaskScheduler()
    
    if args.command == 'create':
        schedule_time = datetime.strptime(args.time, '%Y-%m-%d %H:%M')
        params = {}
        
        if args.url:
            params['url'] = args.url
        if args.url_file:
            params['url_file'] = args.url_file
        if args.days:
            params['days'] = args.days
        
        task_id = f"{args.type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        scheduler.schedule_task(
            task_id=task_id,
            task_type=args.type,
            schedule_time=schedule_time,
            params=params,
            repeat=args.repeat
        )
        
    elif args.command == 'list':
        tasks = scheduler.list_tasks(status=args.status)
        
        if not tasks:
            print("没有找到任务")
            return
        
        print(f"\n共有 {len(tasks)} 个任务:\n")
        print(f"{'任务ID':<30} {'类型':<12} {'状态':<10} {'下次执行':<20} {'重复':<10}")
        print("-" * 90)
        
        for task in tasks:
            print(f"{task['task_id']:<30} "
                  f"{task['task_type']:<12} "
                  f"{task['status']:<10} "
                  f"{task.get('next_run', 'N/A')[:19]:<20} "
                  f"{task['repeat']:<10}")
    
    elif args.command == 'cancel':
        if scheduler.cancel_task(args.task_id):
            print(f"任务已取消: {args.task_id}")
        else:
            print(f"任务不存在: {args.task_id}")
    
    elif args.command == 'run':
        print("启动定时任务调度器...")
        print("按 Ctrl+C 停止\n")
        scheduler.run()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
