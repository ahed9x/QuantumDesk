"""
Elite System Information Module for QuantumDesk
Provides comprehensive system information, hardware details, and real-time monitoring
"""

import psutil
import platform
import cpuinfo
import GPUtil
import socket
import uuid
import subprocess
import json
import time
import threading
from datetime import datetime, timedelta
import os
import wmi
import winreg
from collections import defaultdict

class EliteSystemInfo:
    def __init__(self):
        """Initialize the Elite System Information module"""
        self.wmi_instance = None
        self.system_data = {}
        self.monitoring_active = False
        self.performance_history = defaultdict(list)
        self.max_history = 100  # Keep last 100 data points
        
        try:
            self.wmi_instance = wmi.WMI()
        except Exception as e:
            print(f"WMI initialization failed: {e}")
    
    def get_system_overview(self):
        """Get comprehensive system overview"""
        try:
            system_info = {
                'hostname': platform.node(),
                'platform': platform.platform(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'machine': platform.machine(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
                'uptime': str(timedelta(seconds=int(time.time() - psutil.boot_time()))),
                'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return system_info
        except Exception as e:
            return {'error': f"Failed to get system overview: {e}"}
    
    def get_cpu_info(self):
        """Get detailed CPU information"""
        try:
            cpu_info = cpuinfo.get_cpu_info()
            cpu_data = {
                'name': cpu_info.get('brand_raw', 'Unknown'),
                'architecture': cpu_info.get('arch', 'Unknown'),
                'bits': cpu_info.get('bits', 'Unknown'),
                'count_physical': psutil.cpu_count(logical=False),
                'count_logical': psutil.cpu_count(logical=True),
                'max_frequency': f"{psutil.cpu_freq().max:.2f} MHz" if psutil.cpu_freq() else "Unknown",
                'current_frequency': f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "Unknown",
                'usage_percent': psutil.cpu_percent(interval=1),
                'usage_per_core': psutil.cpu_percent(interval=1, percpu=True),
                'temperature': self.get_cpu_temperature(),
                'cache_info': self.get_cpu_cache_info(),
                'features': cpu_info.get('flags', [])
            }
            return cpu_data
        except Exception as e:
            return {'error': f"Failed to get CPU info: {e}"}
    
    def get_cpu_temperature(self):
        """Get CPU temperature (Windows specific)"""
        try:
            if self.wmi_instance:
                temps = self.wmi_instance.MSAcpi_ThermalZoneTemperature()
                if temps:
                    # Convert from tenths of Kelvin to Celsius
                    temp_celsius = (temps[0].CurrentTemperature / 10.0) - 273.15
                    return f"{temp_celsius:.1f}°C"
            return "Not available"
        except Exception:
            return "Not available"
    
    def get_cpu_cache_info(self):
        """Get CPU cache information"""
        try:
            if self.wmi_instance:
                cache_info = {}
                for cache in self.wmi_instance.Win32_CacheMemory():
                    level = cache.Level
                    size = cache.MaxCacheSize
                    cache_info[f"L{level}"] = f"{size} KB" if size else "Unknown"
                return cache_info
            return {}
        except Exception:
            return {}
    
    def get_memory_info(self):
        """Get detailed memory information"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = {
                'total': self.bytes_to_human(mem.total),
                'available': self.bytes_to_human(mem.available),
                'used': self.bytes_to_human(mem.used),
                'free': self.bytes_to_human(mem.free),
                'percent_used': mem.percent,
                'swap_total': self.bytes_to_human(swap.total),
                'swap_used': self.bytes_to_human(swap.used),
                'swap_free': self.bytes_to_human(swap.free),
                'swap_percent': swap.percent,
                'memory_modules': self.get_memory_modules()
            }
            return memory_info
        except Exception as e:
            return {'error': f"Failed to get memory info: {e}"}
    
    def get_memory_modules(self):
        """Get physical memory module information"""
        try:
            if self.wmi_instance:
                modules = []
                for mem in self.wmi_instance.Win32_PhysicalMemory():
                    module = {
                        'capacity': self.bytes_to_human(int(mem.Capacity)) if mem.Capacity else "Unknown",
                        'speed': f"{mem.Speed} MHz" if mem.Speed else "Unknown",
                        'type': mem.MemoryType or "Unknown",
                        'manufacturer': mem.Manufacturer or "Unknown",
                        'part_number': mem.PartNumber or "Unknown",
                        'serial_number': mem.SerialNumber or "Unknown",
                        'location': mem.DeviceLocator or "Unknown"
                    }
                    modules.append(module)
                return modules
            return []
        except Exception:
            return []
    
    def get_disk_info(self):
        """Get detailed disk information"""
        try:
            disk_info = {}
            
            # Get disk usage for each partition
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total': self.bytes_to_human(usage.total),
                        'used': self.bytes_to_human(usage.used),
                        'free': self.bytes_to_human(usage.free),
                        'percent_used': (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue
            
            # Get physical disk information
            disk_info['physical_disks'] = self.get_physical_disks()
            
            return disk_info
        except Exception as e:
            return {'error': f"Failed to get disk info: {e}"}
    
    def get_physical_disks(self):
        """Get physical disk information"""
        try:
            if self.wmi_instance:
                disks = []
                for disk in self.wmi_instance.Win32_DiskDrive():
                    disk_data = {
                        'model': disk.Model or "Unknown",
                        'size': self.bytes_to_human(int(disk.Size)) if disk.Size else "Unknown",
                        'interface': disk.InterfaceType or "Unknown",
                        'media_type': disk.MediaType or "Unknown",
                        'serial_number': disk.SerialNumber or "Unknown",
                        'partitions': disk.Partitions or 0,
                        'status': disk.Status or "Unknown"
                    }
                    disks.append(disk_data)
                return disks
            return []
        except Exception:
            return []
    
    def get_gpu_info(self):
        """Get detailed GPU information"""
        try:
            gpu_info = []
            
            # Get NVIDIA GPUs
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_data = {
                        'name': gpu.name,
                        'driver': gpu.driver,
                        'memory_total': f"{gpu.memoryTotal} MB",
                        'memory_used': f"{gpu.memoryUsed} MB",
                        'memory_free': f"{gpu.memoryFree} MB",
                        'temperature': f"{gpu.temperature}°C",
                        'load': f"{gpu.load * 100:.1f}%",
                        'uuid': gpu.uuid
                    }
                    gpu_info.append(gpu_data)
            except Exception:
                pass
            
            # Get all GPUs via WMI
            if self.wmi_instance:
                try:
                    for gpu in self.wmi_instance.Win32_VideoController():
                        if not any(g['name'] == gpu.Name for g in gpu_info):
                            gpu_data = {
                                'name': gpu.Name or "Unknown",
                                'driver': gpu.DriverVersion or "Unknown",
                                'memory_total': f"{int(gpu.AdapterRAM) // (1024*1024)} MB" if gpu.AdapterRAM else "Unknown",
                                'resolution': f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}" if gpu.CurrentHorizontalResolution else "Unknown",
                                'refresh_rate': f"{gpu.CurrentRefreshRate} Hz" if gpu.CurrentRefreshRate else "Unknown",
                                'status': gpu.Status or "Unknown"
                            }
                            gpu_info.append(gpu_data)
                except Exception:
                    pass
            
            return gpu_info
        except Exception as e:
            return {'error': f"Failed to get GPU info: {e}"}
    
    def get_network_info(self):
        """Get detailed network information"""
        try:
            network_info = {
                'hostname': socket.gethostname(),
                'ip_address': socket.gethostbyname(socket.gethostname()),
                'mac_address': ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1]),
                'interfaces': {},
                'connections': self.get_network_connections()
            }
            
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface, addresses in interfaces.items():
                interface_info = {
                    'addresses': [],
                    'is_up': stats[interface].isup if interface in stats else False,
                    'speed': f"{stats[interface].speed} Mbps" if interface in stats and stats[interface].speed > 0 else "Unknown",
                    'mtu': stats[interface].mtu if interface in stats else "Unknown"
                }
                
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        interface_info['addresses'].append({
                            'type': 'IPv4',
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        })
                    elif addr.family == socket.AF_INET6:
                        interface_info['addresses'].append({
                            'type': 'IPv6',
                            'address': addr.address,
                            'netmask': addr.netmask
                        })
                
                network_info['interfaces'][interface] = interface_info
            
            return network_info
        except Exception as e:
            return {'error': f"Failed to get network info: {e}"}
    
    def get_network_connections(self):
        """Get active network connections"""
        try:
            connections = []
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    connections.append({
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "Unknown",
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "Unknown",
                        'status': conn.status,
                        'pid': conn.pid
                    })
            return connections[:20]  # Limit to 20 connections
        except Exception:
            return []
    
    def get_processes_info(self):
        """Get detailed process information"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
                try:
                    proc_info = proc.info
                    proc_info['memory_mb'] = proc.memory_info().rss / 1024 / 1024
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            return processes[:50]  # Return top 50 processes
        except Exception as e:
            return {'error': f"Failed to get process info: {e}"}
    
    def get_services_info(self):
        """Get Windows services information"""
        try:
            if self.wmi_instance:
                services = []
                for service in self.wmi_instance.Win32_Service():
                    service_info = {
                        'name': service.Name,
                        'display_name': service.DisplayName,
                        'status': service.Status,
                        'state': service.State,
                        'start_mode': service.StartMode,
                        'service_type': service.ServiceType,
                        'path': service.PathName
                    }
                    services.append(service_info)
                return services
            return []
        except Exception:
            return []
    
    def get_startup_programs(self):
        """Get startup programs information"""
        try:
            startup_programs = []
            
            # Check registry locations
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce"
            ]
            
            for reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            startup_programs.append({
                                'name': name,
                                'path': value,
                                'location': f"HKLM\\{reg_path}"
                            })
                            i += 1
                        except WindowsError:
                            break
                    winreg.CloseKey(key)
                except Exception:
                    continue
            
            return startup_programs
        except Exception:
            return []
    
    def get_installed_software(self):
        """Get installed software information"""
        try:
            if self.wmi_instance:
                software = []
                for product in self.wmi_instance.Win32_Product():
                    software_info = {
                        'name': product.Name,
                        'version': product.Version,
                        'vendor': product.Vendor,
                        'install_date': product.InstallDate,
                        'install_location': product.InstallLocation
                    }
                    software.append(software_info)
                return software
            return []
        except Exception:
            return []
    
    def get_system_performance(self):
        """Get real-time system performance metrics"""
        try:
            performance = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'cpu_per_core': psutil.cpu_percent(interval=1, percpu=True),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': {},
                'network_io': psutil.net_io_counters(),
                'disk_io': psutil.disk_io_counters(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Get disk usage for each partition
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    performance['disk_usage'][partition.device] = (usage.used / usage.total) * 100
                except PermissionError:
                    continue
            
            return performance
        except Exception as e:
            return {'error': f"Failed to get performance info: {e}"}
    
    def start_monitoring(self, callback=None):
        """Start real-time system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        def monitor():
            while self.monitoring_active:
                try:
                    perf_data = self.get_system_performance()
                    
                    # Store in history
                    if 'error' not in perf_data:
                        self.performance_history['cpu'].append(perf_data['cpu_percent'])
                        self.performance_history['memory'].append(perf_data['memory_percent'])
                        self.performance_history['timestamp'].append(perf_data['timestamp'])
                        
                        # Limit history size
                        if len(self.performance_history['cpu']) > self.max_history:
                            for key in self.performance_history:
                                self.performance_history[key].pop(0)
                    
                    if callback:
                        callback(perf_data)
                    
                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time system monitoring"""
        self.monitoring_active = False
    
    def get_performance_history(self):
        """Get performance history data"""
        return dict(self.performance_history)
    
    def generate_system_report(self):
        """Generate comprehensive system report"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'system_overview': self.get_system_overview(),
                'cpu_info': self.get_cpu_info(),
                'memory_info': self.get_memory_info(),
                'disk_info': self.get_disk_info(),
                'gpu_info': self.get_gpu_info(),
                'network_info': self.get_network_info(),
                'top_processes': self.get_processes_info()[:10],
                'system_performance': self.get_system_performance()
            }
            return report
        except Exception as e:
            return {'error': f"Failed to generate system report: {e}"}
    
    def export_report(self, filename=None):
        """Export system report to JSON file"""
        try:
            if not filename:
                filename = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report = self.generate_system_report()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return {'success': True, 'filename': filename}
        except Exception as e:
            return {'error': f"Failed to export report: {e}"}
    
    @staticmethod
    def bytes_to_human(bytes_value):
        """Convert bytes to human readable format"""
        if bytes_value == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while bytes_value >= 1024 and i < len(units) - 1:
            bytes_value /= 1024
            i += 1
        
        return f"{bytes_value:.2f} {units[i]}"
    
    def run_system_diagnostics(self):
        """Run comprehensive system diagnostics"""
        try:
            diagnostics = {
                'cpu_stress_test': self.cpu_stress_test(),
                'memory_test': self.memory_test(),
                'disk_health': self.check_disk_health(),
                'network_test': self.network_test(),
                'system_stability': self.check_system_stability()
            }
            return diagnostics
        except Exception as e:
            return {'error': f"Failed to run diagnostics: {e}"}
    
    def cpu_stress_test(self):
        """Simple CPU stress test"""
        try:
            start_time = time.time()
            cpu_usage_before = psutil.cpu_percent(interval=1)
            
            # Run for 10 seconds
            end_time = start_time + 10
            max_usage = 0
            
            while time.time() < end_time:
                current_usage = psutil.cpu_percent(interval=0.1)
                max_usage = max(max_usage, current_usage)
            
            return {
                'duration': 10,
                'max_cpu_usage': max_usage,
                'avg_cpu_before': cpu_usage_before,
                'status': 'completed'
            }
        except Exception as e:
            return {'error': f"CPU stress test failed: {e}"}
    
    def memory_test(self):
        """Basic memory test"""
        try:
            mem = psutil.virtual_memory()
            return {
                'total_memory': self.bytes_to_human(mem.total),
                'available_memory': self.bytes_to_human(mem.available),
                'memory_usage': mem.percent,
                'status': 'healthy' if mem.percent < 80 else 'warning'
            }
        except Exception as e:
            return {'error': f"Memory test failed: {e}"}
    
    def check_disk_health(self):
        """Check disk health status"""
        try:
            disk_health = {}
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    health_status = 'healthy'
                    
                    if usage.percent > 90:
                        health_status = 'critical'
                    elif usage.percent > 80:
                        health_status = 'warning'
                    
                    disk_health[partition.device] = {
                        'usage_percent': usage.percent,
                        'free_space': self.bytes_to_human(usage.free),
                        'status': health_status
                    }
                except PermissionError:
                    continue
            
            return disk_health
        except Exception as e:
            return {'error': f"Disk health check failed: {e}"}
    
    def network_test(self):
        """Basic network connectivity test"""
        try:
            # Test DNS resolution
            try:
                socket.gethostbyname('google.com')
                dns_status = 'working'
            except socket.gaierror:
                dns_status = 'failed'
            
            # Get network interface status
            interfaces_up = sum(1 for iface, stats in psutil.net_if_stats().items() if stats.isup)
            
            return {
                'dns_resolution': dns_status,
                'interfaces_up': interfaces_up,
                'network_io': psutil.net_io_counters()._asdict(),
                'status': 'healthy' if dns_status == 'working' else 'warning'
            }
        except Exception as e:
            return {'error': f"Network test failed: {e}"}
    
    def check_system_stability(self):
        """Check system stability indicators"""
        try:
            boot_time = psutil.boot_time()
            uptime_hours = (time.time() - boot_time) / 3600
            
            # Get system load
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            stability_score = 100
            issues = []
            
            # Check uptime
            if uptime_hours < 1:
                stability_score -= 10
                issues.append("Recent system restart")
            
            # Check CPU load
            if load_avg[0] > cpu_count * 0.8:
                stability_score -= 20
                issues.append("High CPU load")
            
            # Check memory usage
            mem_percent = psutil.virtual_memory().percent
            if mem_percent > 85:
                stability_score -= 15
                issues.append("High memory usage")
            
            return {
                'uptime_hours': round(uptime_hours, 2),
                'stability_score': max(0, stability_score),
                'issues': issues,
                'status': 'stable' if stability_score > 70 else 'unstable'
            }
        except Exception as e:
            return {'error': f"Stability check failed: {e}"}
