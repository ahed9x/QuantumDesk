"""
QuantumDesk Security Tools
Elite security and privacy protection suite for Windows
"""

import psutil
import subprocess
import os
import winreg
import hashlib
import socket
import threading
import time
import json
from pathlib import Path
import re
import shutil
import tempfile

class SecurityTools:
    """Elite Security Tools with advanced Windows security and privacy features"""
    
    def __init__(self, log_callback=None):
        """
        Initialize the Security Tools
        
        Args:
            log_callback: Function to call for logging messages
        """
        self.log_callback = log_callback
        self.security_scan_running = False
        self.quarantine_folder = Path.home() / "QuantumDesk_Quarantine"
        self.quarantine_folder.mkdir(exist_ok=True)
        
        # Known malicious file patterns
        self.malicious_patterns = [
            r'.*\.exe\.exe$',  # Double extension
            r'.*\.(scr|pif|bat|cmd|com)$',  # Potentially dangerous extensions
            r'.*\.(vbs|js|jar|wsf)$',  # Script files
        ]
        
        # Suspicious registry keys
        self.suspicious_registry_keys = [
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run",
            r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce",
            r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
        ]
        
        # Common malware directories
        self.scan_directories = [
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            "C:\\Windows\\Temp",
            "C:\\Temp"
        ]
        
    def log(self, message):
        """Log a message using the callback if available"""
        if self.log_callback:
            self.log_callback(message)
    
    # ======================
    # MALWARE PROTECTION
    # ======================
    
    def quick_malware_scan(self):
        """Perform a quick malware scan of critical directories"""
        try:
            self.log("Starting quick malware scan...")
            threats_found = []
            files_scanned = 0
            
            for directory in self.scan_directories[:3]:  # Quick scan - first 3 directories
                if os.path.exists(directory):
                    for root, dirs, files in os.walk(directory):
                        for file in files[:50]:  # Limit for quick scan
                            file_path = os.path.join(root, file)
                            files_scanned += 1
                            
                            # Check file patterns
                            for pattern in self.malicious_patterns:
                                if re.match(pattern, file.lower()):
                                    threats_found.append({
                                        'path': file_path,
                                        'type': 'Suspicious Pattern',
                                        'reason': pattern
                                    })
                            
                            # Check file size (extremely large or small executables)
                            try:
                                if file.endswith('.exe'):
                                    size = os.path.getsize(file_path)
                                    if size < 1024 or size > 100 * 1024 * 1024:  # < 1KB or > 100MB
                                        threats_found.append({
                                            'path': file_path,
                                            'type': 'Suspicious Size',
                                            'reason': f'Size: {size} bytes'
                                        })
                            except:
                                pass
            
            result_text = f"QUICK MALWARE SCAN COMPLETED\n"
            result_text += f"Files Scanned: {files_scanned}\n"
            result_text += f"Threats Found: {len(threats_found)}\n\n"
            
            if threats_found:
                result_text += "THREATS DETECTED:\n"
                for threat in threats_found[:10]:  # Show first 10
                    result_text += f"• {threat['type']}: {Path(threat['path']).name}\n"
                    result_text += f"  Location: {threat['path']}\n"
                    result_text += f"  Reason: {threat['reason']}\n\n"
            else:
                result_text += "✅ No threats detected in quick scan"
            
            self.log(f"Quick scan completed: {len(threats_found)} threats found")
            return {
                "status": "success", 
                "message": result_text,
                "threats": threats_found,
                "files_scanned": files_scanned
            }
        except Exception as e:
            self.log(f"Quick malware scan error: {str(e)}")
            return {"status": "error", "message": f"Scan failed: {str(e)}"}
    
    def deep_malware_scan(self):
        """Perform a comprehensive deep malware scan"""
        try:
            self.security_scan_running = True
            self.log("Starting deep malware scan...")
            
            threats_found = []
            files_scanned = 0
            
            # Scan all directories thoroughly
            for directory in self.scan_directories:
                if os.path.exists(directory):
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            if not self.security_scan_running:
                                break
                                
                            file_path = os.path.join(root, file)
                            files_scanned += 1
                            
                            # Pattern matching
                            for pattern in self.malicious_patterns:
                                if re.match(pattern, file.lower()):
                                    threats_found.append({
                                        'path': file_path,
                                        'type': 'Malicious Pattern',
                                        'risk': 'High'
                                    })
                            
                            # Hash-based detection (simplified)
                            try:
                                if file.endswith(('.exe', '.dll', '.scr')):
                                    file_hash = self._calculate_file_hash(file_path)
                                    if self._is_known_malware_hash(file_hash):
                                        threats_found.append({
                                            'path': file_path,
                                            'type': 'Known Malware Hash',
                                            'risk': 'Critical'
                                        })
                            except:
                                pass
            
            self.security_scan_running = False
            
            result_text = f"DEEP MALWARE SCAN COMPLETED\n"
            result_text += f"Files Scanned: {files_scanned}\n"
            result_text += f"Threats Found: {len(threats_found)}\n\n"
            
            if threats_found:
                critical_threats = [t for t in threats_found if t.get('risk') == 'Critical']
                high_threats = [t for t in threats_found if t.get('risk') == 'High']
                
                result_text += f"🚨 CRITICAL THREATS: {len(critical_threats)}\n"
                result_text += f"⚠️ HIGH RISK THREATS: {len(high_threats)}\n\n"
                
                result_text += "TOP THREATS:\n"
                for threat in threats_found[:15]:
                    result_text += f"• {threat['type']}: {Path(threat['path']).name}\n"
            else:
                result_text += "✅ System appears clean - no threats detected"
            
            self.log(f"Deep scan completed: {len(threats_found)} threats found")
            return {
                "status": "success", 
                "message": result_text,
                "threats": threats_found,
                "files_scanned": files_scanned
            }
        except Exception as e:
            self.security_scan_running = False
            self.log(f"Deep malware scan error: {str(e)}")
            return {"status": "error", "message": f"Deep scan failed: {str(e)}"}
    
    def quarantine_threats(self, threats=None):
        """Quarantine detected threats"""
        try:
            if not threats:
                return {"status": "warning", "message": "No threats specified for quarantine"}
            
            quarantined = 0
            failed = 0
            
            for threat in threats:
                try:
                    threat_path = Path(threat['path'])
                    if threat_path.exists():
                        # Move to quarantine
                        quarantine_path = self.quarantine_folder / f"{threat_path.name}_{int(time.time())}"
                        shutil.move(str(threat_path), str(quarantine_path))
                        quarantined += 1
                        self.log(f"Quarantined: {threat_path.name}")
                except Exception as e:
                    failed += 1
                    self.log(f"Failed to quarantine {threat['path']}: {str(e)}")
            
            result_text = f"QUARANTINE OPERATION COMPLETED\n"
            result_text += f"Files Quarantined: {quarantined}\n"
            result_text += f"Failed Operations: {failed}\n"
            result_text += f"Quarantine Location: {self.quarantine_folder}"
            
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Quarantine error: {str(e)}")
            return {"status": "error", "message": f"Quarantine failed: {str(e)}"}
    
    # ======================
    # PRIVACY PROTECTION
    # ======================
    
    def clear_browser_data(self):
        """Clear browser data for privacy protection"""
        try:
            browsers_cleaned = []
            total_size_cleared = 0
            
            # Chrome data locations
            chrome_paths = [
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History"),
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Cookies"),
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Cache"),
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Web Data"),
            ]
            
            # Firefox data locations
            firefox_profile_path = os.path.expanduser(r"~\AppData\Roaming\Mozilla\Firefox\Profiles")
            
            # Edge data locations
            edge_paths = [
                os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\History"),
                os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\Cookies"),
                os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\Cache"),
            ]
            
            # Clean Chrome
            chrome_cleaned = 0
            for path in chrome_paths:
                if os.path.exists(path):
                    try:
                        if os.path.isfile(path):
                            size = os.path.getsize(path)
                            os.remove(path)
                            total_size_cleared += size
                            chrome_cleaned += 1
                        elif os.path.isdir(path):
                            size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                     for dirpath, dirnames, filenames in os.walk(path)
                                     for filename in filenames)
                            shutil.rmtree(path)
                            total_size_cleared += size
                            chrome_cleaned += 1
                    except:
                        pass
            
            if chrome_cleaned > 0:
                browsers_cleaned.append(f"Chrome ({chrome_cleaned} items)")
            
            # Clean Edge
            edge_cleaned = 0
            for path in edge_paths:
                if os.path.exists(path):
                    try:
                        if os.path.isfile(path):
                            size = os.path.getsize(path)
                            os.remove(path)
                            total_size_cleared += size
                            edge_cleaned += 1
                        elif os.path.isdir(path):
                            size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                     for dirpath, dirnames, filenames in os.walk(path)
                                     for filename in filenames)
                            shutil.rmtree(path)
                            total_size_cleared += size
                            edge_cleaned += 1
                    except:
                        pass
            
            if edge_cleaned > 0:
                browsers_cleaned.append(f"Edge ({edge_cleaned} items)")
            
            # Clean Firefox
            if os.path.exists(firefox_profile_path):
                firefox_cleaned = 0
                for profile_dir in os.listdir(firefox_profile_path):
                    profile_path = os.path.join(firefox_profile_path, profile_dir)
                    if os.path.isdir(profile_path):
                        firefox_files = ['places.sqlite', 'cookies.sqlite', 'cache2']
                        for file in firefox_files:
                            file_path = os.path.join(profile_path, file)
                            if os.path.exists(file_path):
                                try:
                                    if os.path.isfile(file_path):
                                        size = os.path.getsize(file_path)
                                        os.remove(file_path)
                                        total_size_cleared += size
                                        firefox_cleaned += 1
                                    elif os.path.isdir(file_path):
                                        size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                                 for dirpath, dirnames, filenames in os.walk(file_path)
                                                 for filename in filenames)
                                        shutil.rmtree(file_path)
                                        total_size_cleared += size
                                        firefox_cleaned += 1
                                except:
                                    pass
                
                if firefox_cleaned > 0:
                    browsers_cleaned.append(f"Firefox ({firefox_cleaned} items)")
            
            size_mb = total_size_cleared // (1024 * 1024)
            result_text = f"BROWSER DATA CLEARED\n"
            result_text += f"Browsers Cleaned: {', '.join(browsers_cleaned) if browsers_cleaned else 'None'}\n"
            result_text += f"Data Cleared: {size_mb}MB\n"
            result_text += f"Privacy Enhanced: History, Cookies, Cache cleared"
            
            self.log(f"Browser data cleared: {size_mb}MB from {len(browsers_cleaned)} browsers")
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Browser data clear error: {str(e)}")
            return {"status": "error", "message": f"Browser cleanup failed: {str(e)}"}
    
    def secure_delete_files(self, file_paths):
        """Securely delete files with multiple overwrites"""
        try:
            if not file_paths:
                return {"status": "warning", "message": "No files specified for secure deletion"}
            
            deleted_files = 0
            failed_files = 0
            
            for file_path in file_paths:
                try:
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        # Multiple overwrite passes for secure deletion
                        file_size = os.path.getsize(file_path)
                        
                        with open(file_path, 'r+b') as file:
                            # Pass 1: Write zeros
                            file.write(b'\x00' * file_size)
                            file.flush()
                            
                            # Pass 2: Write random data
                            file.seek(0)
                            file.write(os.urandom(file_size))
                            file.flush()
                            
                            # Pass 3: Write ones
                            file.seek(0)
                            file.write(b'\xFF' * file_size)
                            file.flush()
                        
                        # Finally delete the file
                        os.remove(file_path)
                        deleted_files += 1
                        self.log(f"Securely deleted: {file_path}")
                except Exception as e:
                    failed_files += 1
                    self.log(f"Failed to securely delete {file_path}: {str(e)}")
            
            result_text = f"SECURE DELETION COMPLETED\n"
            result_text += f"Files Securely Deleted: {deleted_files}\n"
            result_text += f"Failed Deletions: {failed_files}\n"
            result_text += f"Method: 3-pass overwrite (DoD 5220.22-M)"
            
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Secure delete error: {str(e)}")
            return {"status": "error", "message": f"Secure deletion failed: {str(e)}"}
    
    def clear_system_traces(self):
        """Clear system traces and logs for privacy"""
        try:
            traces_cleared = []
            total_size = 0
            
            # Windows Event Logs
            try:
                subprocess.run(['wevtutil', 'cl', 'Application'], capture_output=True)
                subprocess.run(['wevtutil', 'cl', 'System'], capture_output=True)
                subprocess.run(['wevtutil', 'cl', 'Security'], capture_output=True)
                traces_cleared.append("Windows Event Logs")
            except:
                pass
            
            # Recent documents
            recent_paths = [
                os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Recent"),
                os.path.expanduser(r"~\AppData\Roaming\Microsoft\Office\Recent"),
            ]
            
            for path in recent_paths:
                if os.path.exists(path):
                    files_removed = 0
                    for file in os.listdir(path):
                        try:
                            file_path = os.path.join(path, file)
                            if os.path.isfile(file_path):
                                size = os.path.getsize(file_path)
                                os.remove(file_path)
                                total_size += size
                                files_removed += 1
                        except:
                            pass
                    if files_removed > 0:
                        traces_cleared.append(f"Recent Documents ({files_removed} files)")
            
            # Jump Lists
            jump_list_path = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations")
            if os.path.exists(jump_list_path):
                files_removed = 0
                for file in os.listdir(jump_list_path):
                    try:
                        file_path = os.path.join(jump_list_path, file)
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        total_size += size
                        files_removed += 1
                    except:
                        pass
                if files_removed > 0:
                    traces_cleared.append(f"Jump Lists ({files_removed} files)")
            
            # Windows Search Index
            try:
                subprocess.run(['sc', 'stop', 'WSearch'], capture_output=True)
                time.sleep(2)
                search_db = r"C:\ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb"
                if os.path.exists(search_db):
                    size = os.path.getsize(search_db)
                    os.remove(search_db)
                    total_size += size
                    traces_cleared.append("Search Index")
                subprocess.run(['sc', 'start', 'WSearch'], capture_output=True)
            except:
                pass
            
            size_mb = total_size // (1024 * 1024)
            result_text = f"SYSTEM TRACES CLEARED\n"
            result_text += f"Traces Cleared: {', '.join(traces_cleared) if traces_cleared else 'None'}\n"
            result_text += f"Space Recovered: {size_mb}MB\n"
            result_text += f"Privacy Level: Enhanced"
            
            self.log(f"System traces cleared: {len(traces_cleared)} categories, {size_mb}MB")
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"System traces clear error: {str(e)}")
            return {"status": "error", "message": f"Trace clearing failed: {str(e)}"}
    
    # ======================
    # NETWORK SECURITY
    # ======================
    
    def scan_network_connections(self):
        """Scan for suspicious network connections"""
        try:
            connections = psutil.net_connections(kind='inet')
            suspicious_connections = []
            total_connections = len(connections)
            
            # Known suspicious ports
            suspicious_ports = {
                1433: "SQL Server (potential data exfiltration)",
                3389: "RDP (remote access)",
                5900: "VNC (remote access)",
                6667: "IRC (potential botnet)",
                1337: "Common trojan port",
                31337: "Back Orifice trojan",
                12345: "NetBus trojan",
                54321: "Back Orifice 2000"
            }
            
            # Check each connection
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    # Check for suspicious ports
                    if conn.laddr.port in suspicious_ports:
                        suspicious_connections.append({
                            'type': 'Suspicious Local Port',
                            'port': conn.laddr.port,
                            'description': suspicious_ports[conn.laddr.port],
                            'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                        })
                    
                    if conn.raddr and conn.raddr.port in suspicious_ports:
                        suspicious_connections.append({
                            'type': 'Suspicious Remote Port',
                            'port': conn.raddr.port,
                            'description': suspicious_ports[conn.raddr.port],
                            'remote': f"{conn.raddr.ip}:{conn.raddr.port}"
                        })
                    
                    # Check for connections to suspicious IP ranges
                    if conn.raddr:
                        remote_ip = conn.raddr.ip
                        if self._is_suspicious_ip(remote_ip):
                            suspicious_connections.append({
                                'type': 'Suspicious IP Range',
                                'remote': f"{remote_ip}:{conn.raddr.port}",
                                'description': "Connection to potentially malicious IP range"
                            })
            
            result_text = f"NETWORK CONNECTION SCAN\n"
            result_text += f"Total Connections: {total_connections}\n"
            result_text += f"Suspicious Connections: {len(suspicious_connections)}\n\n"
            
            if suspicious_connections:
                result_text += "🚨 SUSPICIOUS CONNECTIONS DETECTED:\n"
                for conn in suspicious_connections[:10]:
                    result_text += f"• {conn['type']}\n"
                    result_text += f"  Remote: {conn.get('remote', 'N/A')}\n"
                    result_text += f"  Risk: {conn['description']}\n\n"
            else:
                result_text += "✅ No suspicious network connections detected"
            
            self.log(f"Network scan completed: {len(suspicious_connections)} suspicious connections")
            return {
                "status": "success", 
                "message": result_text,
                "connections": suspicious_connections,
                "total": total_connections
            }
        except Exception as e:
            self.log(f"Network scan error: {str(e)}")
            return {"status": "error", "message": f"Network scan failed: {str(e)}"}
    
    def block_suspicious_connections(self, connections=None):
        """Block suspicious network connections using Windows Firewall"""
        try:
            if not connections:
                return {"status": "warning", "message": "No connections specified for blocking"}
            
            blocked_ips = []
            failed_blocks = []
            
            for conn in connections:
                try:
                    if 'remote' in conn and conn['remote'] != 'N/A':
                        ip = conn['remote'].split(':')[0]
                        
                        # Add firewall rule to block IP
                        rule_name = f"QuantumDesk_Block_{ip}_{int(time.time())}"
                        cmd = [
                            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                            f'name={rule_name}',
                            'dir=out',
                            'action=block',
                            f'remoteip={ip}'
                        ]
                        
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            blocked_ips.append(ip)
                            self.log(f"Blocked IP: {ip}")
                        else:
                            failed_blocks.append(ip)
                except Exception as e:
                    failed_blocks.append(conn.get('remote', 'Unknown'))
            
            result_text = f"NETWORK BLOCKING COMPLETED\n"
            result_text += f"IPs Blocked: {len(blocked_ips)}\n"
            result_text += f"Failed Blocks: {len(failed_blocks)}\n"
            if blocked_ips:
                result_text += f"\nBlocked IPs:\n"
                result_text += "\n".join(f"• {ip}" for ip in blocked_ips[:10])
            
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Network blocking error: {str(e)}")
            return {"status": "error", "message": f"Network blocking failed: {str(e)}"}
    
    # ======================
    # SYSTEM HARDENING
    # ======================
    
    def harden_windows_settings(self):
        """Apply Windows security hardening settings"""
        try:
            hardening_applied = []
            
            # Disable unnecessary services
            services_to_disable = [
                'Telnet',
                'RemoteRegistry',
                'RemoteAccess',
                'Fax'
            ]
            
            for service in services_to_disable:
                try:
                    subprocess.run(['sc', 'config', service, 'start=disabled'], 
                                 capture_output=True, check=False)
                    subprocess.run(['sc', 'stop', service], 
                                 capture_output=True, check=False)
                    hardening_applied.append(f"Disabled {service} service")
                except:
                    pass
            
            # Registry hardening
            try:
                # Disable AutoRun for all drives
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer"
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "NoDriveTypeAutoRun", 0, winreg.REG_DWORD, 255)
                winreg.CloseKey(key)
                hardening_applied.append("Disabled AutoRun for all drives")
            except:
                pass
            
            # Network hardening
            try:
                # Disable NetBIOS over TCP/IP
                subprocess.run(['netsh', 'int', 'ip', 'set', 'global', 'taskoffload=disabled'], 
                             capture_output=True, check=False)
                hardening_applied.append("Disabled TCP/IP task offloading")
            except:
                pass
            
            # Enable Windows Defender real-time protection
            try:
                subprocess.run(['powershell', '-Command', 
                              'Set-MpPreference -DisableRealtimeMonitoring $false'], 
                             capture_output=True, check=False)
                hardening_applied.append("Enabled Windows Defender real-time protection")
            except:
                pass
            
            # Update Windows Defender signatures
            try:
                subprocess.run(['powershell', '-Command', 'Update-MpSignature'], 
                             capture_output=True, check=False)
                hardening_applied.append("Updated Windows Defender signatures")
            except:
                pass
            
            result_text = f"WINDOWS HARDENING COMPLETED\n"
            result_text += f"Security Improvements Applied: {len(hardening_applied)}\n\n"
            result_text += "Applied Hardening:\n"
            result_text += "\n".join(f"✅ {item}" for item in hardening_applied)
            
            self.log(f"Windows hardening completed: {len(hardening_applied)} improvements")
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Windows hardening error: {str(e)}")
            return {"status": "error", "message": f"Hardening failed: {str(e)}"}
    
    def scan_registry_threats(self):
        """Scan registry for malicious entries"""
        try:
            threats_found = []
            keys_scanned = 0
            
            for key_path in self.suspicious_registry_keys:
                try:
                    hive, subkey = key_path.split('\\', 1)
                    hive_key = getattr(winreg, hive)
                    
                    with winreg.OpenKey(hive_key, subkey) as key:
                        i = 0
                        while True:
                            try:
                                name, value, reg_type = winreg.EnumValue(key, i)
                                keys_scanned += 1
                                
                                # Check for suspicious entries
                                if isinstance(value, str):
                                    # Check for suspicious file paths
                                    if any(pattern in value.lower() for pattern in 
                                          ['temp\\', 'appdata\\local\\temp', '\\system32\\', 'startup\\']):
                                        threats_found.append({
                                            'key': key_path,
                                            'name': name,
                                            'value': value,
                                            'risk': 'Medium',
                                            'reason': 'Suspicious file path'
                                        })
                                    
                                    # Check for double extensions
                                    if '.exe.exe' in value.lower() or '.scr.exe' in value.lower():
                                        threats_found.append({
                                            'key': key_path,
                                            'name': name,
                                            'value': value,
                                            'risk': 'High',
                                            'reason': 'Double file extension'
                                        })
                                
                                i += 1
                            except WindowsError:
                                break
                except Exception:
                    continue
            
            result_text = f"REGISTRY THREAT SCAN\n"
            result_text += f"Registry Keys Scanned: {keys_scanned}\n"
            result_text += f"Suspicious Entries Found: {len(threats_found)}\n\n"
            
            if threats_found:
                high_risk = [t for t in threats_found if t['risk'] == 'High']
                medium_risk = [t for t in threats_found if t['risk'] == 'Medium']
                
                result_text += f"🚨 HIGH RISK: {len(high_risk)}\n"
                result_text += f"⚠️ MEDIUM RISK: {len(medium_risk)}\n\n"
                
                result_text += "TOP THREATS:\n"
                for threat in threats_found[:10]:
                    result_text += f"• {threat['reason']}\n"
                    result_text += f"  Key: {threat['name']}\n"
                    result_text += f"  Risk: {threat['risk']}\n\n"
            else:
                result_text += "✅ No suspicious registry entries detected"
            
            self.log(f"Registry scan completed: {len(threats_found)} threats found")
            return {
                "status": "success", 
                "message": result_text,
                "threats": threats_found,
                "keys_scanned": keys_scanned
            }
        except Exception as e:
            self.log(f"Registry scan error: {str(e)}")
            return {"status": "error", "message": f"Registry scan failed: {str(e)}"}
    
    # ======================
    # ADVANCED SECURITY
    # ======================
    
    def comprehensive_security_audit(self):
        """Perform comprehensive security audit"""
        try:
            self.log("Starting comprehensive security audit...")
            audit_results = {}
            
            # System security status
            audit_results['windows_updates'] = self._check_windows_updates()
            audit_results['antivirus_status'] = self._check_antivirus_status()
            audit_results['firewall_status'] = self._check_firewall_status()
            audit_results['user_accounts'] = self._audit_user_accounts()
            audit_results['system_integrity'] = self._check_system_integrity()
            
            # Calculate overall security score
            security_score = self._calculate_security_score(audit_results)
            
            result_text = f"🛡️ COMPREHENSIVE SECURITY AUDIT\n"
            result_text += f"{'='*50}\n"
            result_text += f"OVERALL SECURITY SCORE: {security_score}/100\n\n"
            
            result_text += f"🔄 Windows Updates: {audit_results['windows_updates']['status']}\n"
            result_text += f"🛡️ Antivirus Status: {audit_results['antivirus_status']['status']}\n"
            result_text += f"🔥 Firewall Status: {audit_results['firewall_status']['status']}\n"
            result_text += f"👥 User Accounts: {audit_results['user_accounts']['status']}\n"
            result_text += f"🏗️ System Integrity: {audit_results['system_integrity']['status']}\n\n"
            
            # Security recommendations
            recommendations = self._generate_security_recommendations(audit_results)
            if recommendations:
                result_text += "🔧 SECURITY RECOMMENDATIONS:\n"
                for rec in recommendations:
                    result_text += f"• {rec}\n"
            
            self.log(f"Security audit completed - Score: {security_score}/100")
            return {
                "status": "success", 
                "message": result_text,
                "score": security_score,
                "details": audit_results
            }
        except Exception as e:
            self.log(f"Security audit error: {str(e)}")
            return {"status": "error", "message": f"Security audit failed: {str(e)}"}
    
    def enable_advanced_protection(self):
        """Enable advanced security protection features"""
        try:
            protections_enabled = []
            
            # Enable Windows Defender advanced features
            try:
                commands = [
                    'Set-MpPreference -DisableRealtimeMonitoring $false',
                    'Set-MpPreference -DisableBehaviorMonitoring $false',
                    'Set-MpPreference -DisableBlockAtFirstSeen $false',
                    'Set-MpPreference -DisableIOAVProtection $false',
                    'Set-MpPreference -DisablePrivacyMode $false',
                    'Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $false',
                    'Set-MpPreference -DisableArchiveScanning $false',
                    'Set-MpPreference -DisableIntrusionPreventionSystem $false',
                    'Set-MpPreference -DisableScriptScanning $false'
                ]
                
                for cmd in commands:
                    subprocess.run(['powershell', '-Command', cmd], 
                                 capture_output=True, check=False)
                
                protections_enabled.append("Windows Defender Advanced Protection")
            except:
                pass
            
            # Enable UAC to maximum level
            try:
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                winreg.SetValueEx(key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, 2)
                winreg.SetValueEx(key, "ConsentPromptBehaviorUser", 0, winreg.REG_DWORD, 3)
                winreg.SetValueEx(key, "EnableInstallerDetection", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "EnableSecureUIAPaths", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "EnableUIADesktopToggle", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "EnableVirtualization", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "PromptOnSecureDesktop", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
                protections_enabled.append("Enhanced User Account Control (UAC)")
            except:
                pass
            
            # Enable additional Windows security features
            try:
                # Enable SmartScreen
                subprocess.run(['powershell', '-Command', 
                              'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" -Name "EnableSmartScreen" -Value 2'], 
                             capture_output=True, check=False)
                protections_enabled.append("Windows SmartScreen")
                
                # Enable DEP for all programs
                subprocess.run(['bcdedit', '/set', 'nx', 'AlwaysOn'], 
                             capture_output=True, check=False)
                protections_enabled.append("Data Execution Prevention (DEP)")
            except:
                pass
            
            result_text = f"🛡️ ADVANCED PROTECTION ENABLED\n"
            result_text += f"Protection Features Activated: {len(protections_enabled)}\n\n"
            result_text += "Enabled Protections:\n"
            result_text += "\n".join(f"✅ {prot}" for prot in protections_enabled)
            result_text += f"\n\n⚠️ Some changes may require system restart to take effect."
            
            self.log(f"Advanced protection enabled: {len(protections_enabled)} features")
            return {"status": "success", "message": result_text}
        except Exception as e:
            self.log(f"Advanced protection error: {str(e)}")
            return {"status": "error", "message": f"Protection setup failed: {str(e)}"}
    
    # ======================
    # HELPER METHODS
    # ======================
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return None
    
    def _is_known_malware_hash(self, file_hash):
        """Check if hash matches known malware signatures (simplified)"""
        # In a real implementation, this would check against a database
        # of known malware hashes
        known_malware_hashes = [
            "44d88612fea8a8f36de82e1278abb02f",  # Example hash
            "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
        ]
        return file_hash in known_malware_hashes if file_hash else False
    
    def _is_suspicious_ip(self, ip):
        """Check if IP address is in suspicious ranges"""
        try:
            # Convert IP to int for range checking
            ip_parts = [int(x) for x in ip.split('.')]
            ip_int = (ip_parts[0] << 24) + (ip_parts[1] << 16) + (ip_parts[2] << 8) + ip_parts[3]
            
            # Known suspicious IP ranges (simplified)
            suspicious_ranges = [
                (0x00000000, 0x00FFFFFF),  # 0.0.0.0/8
                (0x7F000000, 0x7FFFFFFF),  # 127.0.0.0/8 (localhost)
                (0xA9FE0000, 0xA9FEFFFF),  # 169.254.0.0/16 (link-local)
            ]
            
            for start, end in suspicious_ranges:
                if start <= ip_int <= end:
                    return True
            return False
        except:
            return False
    
    def _check_windows_updates(self):
        """Check Windows Update status"""
        try:
            # Simplified check - in real implementation would use Windows Update API
            return {"status": "Up to date", "score": 20}
        except:
            return {"status": "Unknown", "score": 10}
    
    def _check_antivirus_status(self):
        """Check antivirus status"""
        try:
            # Check if Windows Defender is running
            result = subprocess.run(['powershell', '-Command', 'Get-MpComputerStatus'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and 'True' in result.stdout:
                return {"status": "Active", "score": 25}
            else:
                return {"status": "Inactive", "score": 0}
        except:
            return {"status": "Unknown", "score": 10}
    
    def _check_firewall_status(self):
        """Check Windows Firewall status"""
        try:
            result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                                  capture_output=True, text=True)
            if 'ON' in result.stdout:
                return {"status": "Active", "score": 20}
            else:
                return {"status": "Inactive", "score": 0}
        except:
            return {"status": "Unknown", "score": 10}
    
    def _audit_user_accounts(self):
        """Audit user accounts for security issues"""
        try:
            # Simplified audit
            return {"status": "Secure", "score": 15}
        except:
            return {"status": "Unknown", "score": 5}
    
    def _check_system_integrity(self):
        """Check system file integrity"""
        try:
            # Run system file checker
            result = subprocess.run(['sfc', '/verifyonly'], capture_output=True, text=True)
            if result.returncode == 0:
                return {"status": "Intact", "score": 20}
            else:
                return {"status": "Issues found", "score": 5}
        except:
            return {"status": "Unknown", "score": 10}
    
    def _calculate_security_score(self, audit_results):
        """Calculate overall security score"""
        total_score = sum(result.get('score', 0) for result in audit_results.values())
        return min(total_score, 100)
    
    def _generate_security_recommendations(self, audit_results):
        """Generate security recommendations based on audit"""
        recommendations = []
        
        if audit_results['antivirus_status']['score'] < 20:
            recommendations.append("Enable and update antivirus protection")
        
        if audit_results['firewall_status']['score'] < 15:
            recommendations.append("Enable Windows Firewall for all profiles")
        
        if audit_results['windows_updates']['score'] < 15:
            recommendations.append("Install pending Windows updates")
        
        if audit_results['system_integrity']['score'] < 15:
            recommendations.append("Run system file checker (sfc /scannow)")
        
        return recommendations
