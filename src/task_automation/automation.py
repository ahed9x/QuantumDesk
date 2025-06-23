"""
QuantumDesk Task Automation
Elite task automation and scheduling tools for Windows
"""

import psutil
import subprocess
import os
import time
import threading
import schedule
import json
from pathlib import Path
from datetime import datetime, timedelta
import pyautogui
import keyboard

class TaskAutomation:
    """Elite Task Automation with advanced scheduling and automation tools"""
    
    def __init__(self, log_callback=None):
        """
        Initialize the Task Automation
        
        Args:
            log_callback: Function to call for logging messages
        """
        self.log_callback = log_callback
        self.scheduled_tasks = []
        self.automation_running = False
        self.tasks_file = Path.home() / "QuantumDesk_Tasks.json"
        self.load_tasks()
        
        # Start the task scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        
    def log(self, message):
        """Log a message using the callback if available"""
        if self.log_callback:
            self.log_callback(f"TaskAutomation: {message}")
    
    # ======================
    # SYSTEM AUTOMATION
    # ======================
    
    def schedule_system_restart(self, minutes=60):
        """Schedule a system restart"""
        try:
            subprocess.run(['shutdown', '/r', '/t', str(minutes * 60)], check=True)
            self.log(f"System restart scheduled in {minutes} minutes")
            return {"status": "success", "message": f"System will restart in {minutes} minutes"}
        except Exception as e:
            self.log(f"Failed to schedule restart: {str(e)}")
            return {"status": "error", "message": f"Failed to schedule restart: {str(e)}"}
    
    def schedule_system_shutdown(self, minutes=60):
        """Schedule a system shutdown"""
        try:
            subprocess.run(['shutdown', '/s', '/t', str(minutes * 60)], check=True)
            self.log(f"System shutdown scheduled in {minutes} minutes")
            return {"status": "success", "message": f"System will shutdown in {minutes} minutes"}
        except Exception as e:
            self.log(f"Failed to schedule shutdown: {str(e)}")
            return {"status": "error", "message": f"Failed to schedule shutdown: {str(e)}"}
    
    def cancel_scheduled_shutdown(self):
        """Cancel scheduled shutdown/restart"""
        try:
            subprocess.run(['shutdown', '/a'], check=True)
            self.log("Scheduled shutdown/restart cancelled")
            return {"status": "success", "message": "Scheduled shutdown/restart cancelled"}
        except Exception as e:
            self.log(f"Failed to cancel shutdown: {str(e)}")
            return {"status": "error", "message": f"Failed to cancel: {str(e)}"}
    
    # ======================
    # APPLICATION AUTOMATION
    # ======================
    
    def auto_launch_apps(self, app_list):
        """Automatically launch multiple applications"""
        try:
            launched = []
            failed = []
            
            for app in app_list:
                try:
                    if app.endswith('.exe') or '\\' in app:
                        # Full path or executable
                        subprocess.Popen(app)
                    else:
                        # Try to launch by name
                        subprocess.Popen(app, shell=True)
                    launched.append(app)
                    time.sleep(2)  # Wait between launches
                except Exception as e:
                    failed.append(f"{app}: {str(e)}")
            
            result_text = f"App Launch Results:\n"
            result_text += f"✅ Successfully launched: {len(launched)}\n"
            result_text += f"❌ Failed to launch: {len(failed)}\n\n"
            
            if launched:
                result_text += "Launched Apps:\n"
                result_text += "\n".join(f"• {app}" for app in launched)
                result_text += "\n\n"
            
            if failed:
                result_text += "Failed Apps:\n"
                result_text += "\n".join(f"• {fail}" for fail in failed)
            
            self.log(f"Auto-launched {len(launched)} apps, {len(failed)} failed")
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Auto-launch error: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def close_all_apps(self, exclude_list=None):
        """Close all running applications except excluded ones"""
        try:
            if exclude_list is None:
                exclude_list = ['explorer.exe', 'dwm.exe', 'winlogon.exe', 'csrss.exe']
            
            closed_apps = []
            protected_apps = set(exclude_list)
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if (proc.info['name'].endswith('.exe') and 
                        proc.info['name'].lower() not in [p.lower() for p in protected_apps]):
                        proc.terminate()
                        closed_apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            result_text = f"Closed {len(closed_apps)} applications"
            self.log(f"Closed {len(closed_apps)} applications")
            return {"status": "success", "message": result_text, "closed": closed_apps}
        except Exception as e:
            self.log(f"Close apps error: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    # ======================
    # SCHEDULED TASKS
    # ======================
    
    def create_scheduled_task(self, name, command, schedule_type, schedule_value):
        """Create a new scheduled task"""
        try:
            task = {
                'id': len(self.scheduled_tasks) + 1,
                'name': name,
                'command': command,
                'schedule_type': schedule_type,  # 'daily', 'weekly', 'hourly', 'once'
                'schedule_value': schedule_value,  # time string or interval
                'created': datetime.now().isoformat(),
                'enabled': True,
                'last_run': None
            }
            
            self.scheduled_tasks.append(task)
            self.save_tasks()
            
            # Schedule with the schedule library
            self._schedule_task(task)
            
            self.log(f"Created scheduled task: {name}")
            return {"status": "success", "message": f"Task '{name}' created successfully"}
        except Exception as e:
            self.log(f"Failed to create task: {str(e)}")
            return {"status": "error", "message": f"Failed to create task: {str(e)}"}
    
    def delete_scheduled_task(self, task_id):
        """Delete a scheduled task"""
        try:
            self.scheduled_tasks = [t for t in self.scheduled_tasks if t['id'] != task_id]
            self.save_tasks()
            schedule.clear()  # Reload all schedules
            self._reload_schedules()
            
            self.log(f"Deleted task ID: {task_id}")
            return {"status": "success", "message": f"Task deleted successfully"}
        except Exception as e:
            self.log(f"Failed to delete task: {str(e)}")
            return {"status": "error", "message": f"Failed to delete task: {str(e)}"}
    
    def list_scheduled_tasks(self):
        """List all scheduled tasks"""
        try:
            if not self.scheduled_tasks:
                return {"status": "success", "message": "No scheduled tasks found", "tasks": []}
            
            task_list = []
            for task in self.scheduled_tasks:
                status = "Enabled" if task['enabled'] else "Disabled"
                last_run = task.get('last_run', 'Never')
                if last_run and last_run != 'Never':
                    last_run = datetime.fromisoformat(last_run).strftime('%Y-%m-%d %H:%M')
                
                task_info = f"[{task['id']}] {task['name']} - {task['schedule_type']} at {task['schedule_value']} ({status})"
                task_list.append(task_info)
            
            result_text = f"Scheduled Tasks ({len(self.scheduled_tasks)}):\n"
            result_text += "\n".join(task_list)
            
            return {"status": "success", "message": result_text, "tasks": self.scheduled_tasks}
        except Exception as e:
            self.log(f"Failed to list tasks: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    # ======================
    # MOUSE & KEYBOARD AUTOMATION
    # ======================
    
    def record_mouse_actions(self, duration=30):
        """Record mouse movements and clicks for specified duration"""
        try:
            self.log(f"Recording mouse actions for {duration} seconds...")
            recorded_actions = []
            start_time = time.time()
            
            # This is a simplified recording - in a real implementation,
            # you'd use more sophisticated mouse/keyboard hooks
            while time.time() - start_time < duration:
                pos = pyautogui.position()
                recorded_actions.append({
                    'type': 'move',
                    'x': pos.x,
                    'y': pos.y,
                    'timestamp': time.time() - start_time
                })
                time.sleep(0.1)
            
            result_text = f"Recorded {len(recorded_actions)} mouse actions"
            self.log(f"Mouse recording completed: {len(recorded_actions)} actions")
            return {"status": "success", "message": result_text, "actions": recorded_actions}
        except Exception as e:
            self.log(f"Mouse recording error: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def auto_click_sequence(self, coordinates_list, delay=1):
        """Execute a sequence of mouse clicks at specified coordinates"""
        try:
            clicked_points = 0
            for x, y in coordinates_list:
                try:
                    pyautogui.click(x, y)
                    clicked_points += 1
                    time.sleep(delay)
                except Exception:
                    continue
            
            result_text = f"Executed {clicked_points} mouse clicks"
            self.log(f"Auto-click sequence completed: {clicked_points} clicks")
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Auto-click error: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    def send_key_sequence(self, key_sequence):
        """Send a sequence of keystrokes"""
        try:
            for key in key_sequence:
                if isinstance(key, str) and len(key) == 1:
                    pyautogui.press(key)
                else:
                    pyautogui.press(key)  # Special keys like 'enter', 'tab'
                time.sleep(0.1)
            
            result_text = f"Sent {len(key_sequence)} keystrokes"
            self.log(f"Key sequence completed: {len(key_sequence)} keys")
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Key sequence error: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}
    
    # ======================
    # HELPER METHODS
    # ======================
    
    def _scheduler_worker(self):
        """Background worker for running scheduled tasks"""
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.log(f"Scheduler error: {str(e)}")
                time.sleep(5)
    
    def _schedule_task(self, task):
        """Schedule a task with the schedule library"""
        try:
            if task['schedule_type'] == 'daily':
                schedule.every().day.at(task['schedule_value']).do(self._execute_task, task)
            elif task['schedule_type'] == 'hourly':
                schedule.every().hour.do(self._execute_task, task)
            elif task['schedule_type'] == 'weekly':
                # Assume schedule_value is like "monday:10:00"
                day, time_str = task['schedule_value'].split(':')
                getattr(schedule.every(), day.lower()).at(time_str).do(self._execute_task, task)
        except Exception as e:
            self.log(f"Failed to schedule task {task['name']}: {str(e)}")
    
    def _execute_task(self, task):
        """Execute a scheduled task"""
        try:
            if not task['enabled']:
                return
            
            self.log(f"Executing scheduled task: {task['name']}")
            
            # Execute the command
            if task['command'].endswith('.exe') or '\\' in task['command']:
                subprocess.Popen(task['command'])
            else:
                subprocess.run(task['command'], shell=True, check=False)
            
            # Update last run time
            task['last_run'] = datetime.now().isoformat()
            self.save_tasks()
            
            self.log(f"Task completed: {task['name']}")
        except Exception as e:
            self.log(f"Task execution failed {task['name']}: {str(e)}")
    
    def _reload_schedules(self):
        """Reload all scheduled tasks"""
        for task in self.scheduled_tasks:
            if task['enabled']:
                self._schedule_task(task)
    
    def save_tasks(self):
        """Save tasks to file"""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self.scheduled_tasks, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save tasks: {str(e)}")
    
    def load_tasks(self):
        """Load tasks from file"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    self.scheduled_tasks = json.load(f)
                self._reload_schedules()
        except Exception as e:
            self.log(f"Failed to load tasks: {str(e)}")
            self.scheduled_tasks = []
