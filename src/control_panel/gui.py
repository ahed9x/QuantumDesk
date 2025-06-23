import customtkinter as ctk
import psutil
import threading
import time
import GPUtil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from system_optimizer import SystemOptimizer
from security_prefs import SecurityTools

class QuantumDeskGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuantumDesk")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="QuantumDesk", font=("Arial", 20, "bold"))
        self.sidebar_label.pack(pady=(20, 10))

        # Navigation buttons
        self.buttons = {}
        features = [
            "Control Panel", "Task Automation", "File Tools", "System Optimizer",
            "System Info", "Macros", "Launcher", "Logs", "Updates", "Security"
        ]
        for feat in features:
            btn = ctk.CTkButton(self.sidebar, text=feat, command=lambda f=feat: self.show_panel(f))
            btn.pack(fill="x", pady=2, padx=10)
            self.buttons[feat] = btn

        # Light/Dark mode toggle
        self.theme_toggle = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme)
        self.theme_toggle.pack(pady=(30, 10), padx=10)        # Main content area
        self.main_panel = ctk.CTkFrame(self, corner_radius=10)
        self.main_panel.pack(expand=True, fill="both", padx=10, pady=10)
        self.panel_label = ctk.CTkLabel(self.main_panel, text="Welcome to QuantumDesk!", font=("Arial", 18))
        self.panel_label.pack(pady=20)

        # --- Control Panel Monitoring Widgets ---
        # Use CTkScrollableFrame for automatic mouse wheel scrolling
        self.monitor_frame = ctk.CTkScrollableFrame(self.main_panel, corner_radius=10)
        self.monitor_frame.pack(expand=True, fill="both", padx=20, pady=20)
        # CPU, RAM, GPU, Battery, Network, Disks
        self.cpu_label = ctk.CTkLabel(self.monitor_frame, text="CPU Usage: --%", font=("Arial", 16))
        self.cpu_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ram_label = ctk.CTkLabel(self.monitor_frame, text="RAM Usage: --%", font=("Arial", 16))
        self.ram_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.gpu_label = ctk.CTkLabel(self.monitor_frame, text="GPU Usage: --% | Temp: --°C", font=("Arial", 16))
        self.gpu_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.battery_label = ctk.CTkLabel(self.monitor_frame, text="Battery: --", font=("Arial", 16))
        self.battery_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.net_label = ctk.CTkLabel(self.monitor_frame, text="Network: --", font=("Arial", 16))
        self.net_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.disk_labels = []
        self.disk_graphs = []
        self.disk_usage_history = {}
        # Use all fixed drives only, not just those with a mountpoint
        partitions = [p for p in psutil.disk_partitions(all=True) if p.fstype and (p.opts.find('cdrom') == -1)]
        for i, part in enumerate(partitions):
            label = ctk.CTkLabel(self.monitor_frame, text=f"{part.device} Usage: --%", font=("Arial", 16))
            label.grid(row=5+i, column=0, padx=10, pady=10, sticky="w")
            self.disk_labels.append(label)
            self.disk_usage_history[part.device] = [0]*60
            fig, ax = plt.subplots(figsize=(3.2,1.5), dpi=100, facecolor='none')
            ax.set_title(f"{part.device} Usage (%)", fontsize=10, color='#B0B0B0', pad=12)
            ax.set_ylim(0, 100)
            ax.set_xlim(0, 59)
            ax.set_xticks([0, 20, 40, 59])
            ax.set_yticks([0,25,50,75,100])
            ax.set_facecolor('none')
            ax.grid(True, color='#444444', linestyle='--', linewidth=0.5, alpha=0.5)
            for spine in ax.spines.values():
                spine.set_visible(False)
            line, = ax.plot(self.disk_usage_history[part.device], color='#00BFFF', linewidth=2, alpha=0.7)
            ax.tick_params(axis='x', colors='#B0B0B0', labelsize=8)
            ax.tick_params(axis='y', colors='#B0B0B0', labelsize=8)
            for label_ in ax.get_xticklabels() + ax.get_yticklabels():
                label_.set_backgroundcolor((0,0,0,0))
            for y in [0,25,50,75,100]:
                ax.text(59, y, f'{y}', color='#B0B0B0', fontsize=8, va='center', ha='left', alpha=0.8)
            canvas = FigureCanvasTkAgg(fig, master=self.monitor_frame)
            canvas.get_tk_widget().grid(row=5+i, column=1, padx=10, pady=10, sticky='nsew')
            self.disk_graphs.append((fig, ax, line, canvas, part.device))        # CPU, RAM, GPU graphs
        self.cpu_history = [0]*60
        self.ram_history = [0]*60
        self.gpu_history = [0]*60
        def make_graph(title, color):
            fig, ax = plt.subplots(figsize=(3.2,1.5), dpi=100, facecolor='none')
            ax.set_title(title, fontsize=10, color='#B0B0B0', pad=12)
            ax.set_ylim(0, 100)
            ax.set_xlim(0, 59)
            ax.set_xticks([0, 20, 40, 59])
            ax.set_yticks([0,25,50,75,100])
            ax.set_facecolor('none')
            ax.grid(True, color='#444444', linestyle='--', linewidth=0.5, alpha=0.5)
            for spine in ax.spines.values():
                spine.set_visible(False)
            line, = ax.plot([0]*60, color=color, linewidth=2, alpha=0.7)
            ax.tick_params(axis='x', colors='#B0B0B0', labelsize=8)
            ax.tick_params(axis='y', colors='#B0B0B0', labelsize=8)
            for label_ in ax.get_xticklabels() + ax.get_yticklabels():
                label_.set_backgroundcolor((0,0,0,0))
            for y in [0,25,50,75,100]:
                ax.text(59, y, f'{y}', color='#B0B0B0', fontsize=8, va='center', ha='left', alpha=0.8)
            return fig, ax, line
        self.cpu_fig, self.cpu_ax, self.cpu_line = make_graph("CPU Usage (%)", '#FF5555')
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=self.monitor_frame)
        self.cpu_canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        self.ram_fig, self.ram_ax, self.ram_line = make_graph("RAM Usage (%)", '#44FF44')
        self.ram_canvas = FigureCanvasTkAgg(self.ram_fig, master=self.monitor_frame)
        self.ram_canvas.get_tk_widget().grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
        self.gpu_fig, self.gpu_ax, self.gpu_line = make_graph("GPU Usage (%)", '#AA88FF')
        self.gpu_canvas = FigureCanvasTkAgg(self.gpu_fig, master=self.monitor_frame)
        self.gpu_canvas.get_tk_widget().grid(row=2, column=1, padx=10, pady=10, sticky='nsew')
        self.monitor_frame.pack_forget()

        # --- System Optimizer Panel ---
        self.optimizer_frame = ctk.CTkScrollableFrame(self.main_panel, corner_radius=10)
        
        # RAM Optimization Section
        ram_section = ctk.CTkFrame(self.optimizer_frame)
        ram_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(ram_section, text="🧠 Memory Optimization", font=("Arial", 18, "bold")).pack(pady=10)
        
        ram_buttons = ctk.CTkFrame(ram_section)
        ram_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(ram_buttons, text="Free RAM", command=self.free_ram, fg_color="#FF6B6B").pack(side="left", padx=5)
        ctk.CTkButton(ram_buttons, text="Clear Cache", command=self.clear_cache, fg_color="#4ECDC4").pack(side="left", padx=5)
        ctk.CTkButton(ram_buttons, text="Optimize Memory", command=self.optimize_memory, fg_color="#45B7D1").pack(side="left", padx=5)
        
        self.ram_status = ctk.CTkLabel(ram_section, text="Ready to optimize", font=("Arial", 12))
        self.ram_status.pack(pady=5)
        
        # Process Management Section
        process_section = ctk.CTkFrame(self.optimizer_frame)
        process_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(process_section, text="⚡ Process Manager", font=("Arial", 18, "bold")).pack(pady=10)
        
        proc_buttons = ctk.CTkFrame(process_section)
        proc_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(proc_buttons, text="Kill Heavy Processes", command=self.kill_heavy_processes, fg_color="#FF8A65").pack(side="left", padx=5)
        ctk.CTkButton(proc_buttons, text="End Idle Apps", command=self.end_idle_apps, fg_color="#FFB74D").pack(side="left", padx=5)
        ctk.CTkButton(proc_buttons, text="Chrome Cleaner", command=self.clean_chrome, fg_color="#A5D6A7").pack(side="left", padx=5)
        
        self.process_list = ctk.CTkTextbox(process_section, height=120)
        self.process_list.pack(fill="x", padx=10, pady=5)
        
        # Startup Management Section
        startup_section = ctk.CTkFrame(self.optimizer_frame)
        startup_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(startup_section, text="🚀 Startup Manager", font=("Arial", 18, "bold")).pack(pady=10)
        
        startup_buttons = ctk.CTkFrame(startup_section)
        startup_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(startup_buttons, text="Scan Startup", command=self.scan_startup, fg_color="#CE93D8").pack(side="left", padx=5)
        ctk.CTkButton(startup_buttons, text="Disable Heavy Apps", command=self.disable_heavy_startup, fg_color="#F48FB1").pack(side="left", padx=5)
        ctk.CTkButton(startup_buttons, text="Optimize Boot", command=self.optimize_boot, fg_color="#80CBC4").pack(side="left", padx=5)
        
        self.startup_list = ctk.CTkTextbox(startup_section, height=100)
        self.startup_list.pack(fill="x", padx=10, pady=5)
        
        # System Cleanup Section
        cleanup_section = ctk.CTkFrame(self.optimizer_frame)
        cleanup_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(cleanup_section, text="🧹 System Cleanup", font=("Arial", 18, "bold")).pack(pady=10)
        
        cleanup_buttons = ctk.CTkFrame(cleanup_section)
        cleanup_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(cleanup_buttons, text="Clean Temp Files", command=self.clean_temp, fg_color="#81C784").pack(side="left", padx=5)
        ctk.CTkButton(cleanup_buttons, text="Empty Recycle Bin", command=self.empty_recycle, fg_color="#FFD54F").pack(side="left", padx=5)
        ctk.CTkButton(cleanup_buttons, text="Clear Prefetch", command=self.clear_prefetch, fg_color="#FFAB91").pack(side="left", padx=5)
        
        cleanup_buttons2 = ctk.CTkFrame(cleanup_section)
        cleanup_buttons2.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(cleanup_buttons2, text="Registry Clean", command=self.clean_registry, fg_color="#F06292").pack(side="left", padx=5)
        ctk.CTkButton(cleanup_buttons2, text="Disk Cleanup", command=self.disk_cleanup, fg_color="#BA68C8").pack(side="left", padx=5)
        ctk.CTkButton(cleanup_buttons2, text="Full System Clean", command=self.full_system_clean, fg_color="#E57373").pack(side="left", padx=5)
        
        self.cleanup_status = ctk.CTkLabel(cleanup_section, text="Ready for cleanup", font=("Arial", 12))
        self.cleanup_status.pack(pady=5)
          # Performance Boost Section
        perf_section = ctk.CTkFrame(self.optimizer_frame)
        perf_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(perf_section, text="⚡ Performance Boost", font=("Arial", 18, "bold")).pack(pady=10)
        
        perf_buttons = ctk.CTkFrame(perf_section)
        perf_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(perf_buttons, text="Game Mode", command=self.game_mode, fg_color="#FF5722").pack(side="left", padx=5)
        ctk.CTkButton(perf_buttons, text="High Performance", command=self.high_performance, fg_color="#795548").pack(side="left", padx=5)
        ctk.CTkButton(perf_buttons, text="Priority Boost", command=self.priority_boost, fg_color="#607D8B").pack(side="left", padx=5)
        
        self.perf_status = ctk.CTkLabel(perf_section, text="Performance: Normal", font=("Arial", 12))
        self.perf_status.pack(pady=5)
        
        # Elite Tools Section
        elite_section = ctk.CTkFrame(self.optimizer_frame)
        elite_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(elite_section, text="👑 Elite Tools", font=("Arial", 18, "bold")).pack(pady=10)
        
        elite_buttons = ctk.CTkFrame(elite_section)
        elite_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(elite_buttons, text="Auto Optimize", command=self.auto_optimize, fg_color="#9C27B0").pack(side="left", padx=5)
        ctk.CTkButton(elite_buttons, text="System Health", command=self.check_system_health, fg_color="#673AB7").pack(side="left", padx=5)
        ctk.CTkButton(elite_buttons, text="Elite Clean", command=self.elite_clean, fg_color="#3F51B5").pack(side="left", padx=5)
        
        self.elite_status = ctk.CTkTextbox(elite_section, height=80)
        self.elite_status.pack(fill="x", padx=10, pady=5)
        self.elite_status.insert("1.0", "Elite optimization tools ready...")
        
        self.optimizer_frame.pack_forget()
        
        # --- Security Tools Panel ---
        self.security_frame = ctk.CTkScrollableFrame(self.main_panel, corner_radius=10)
        
        # Malware Protection Section
        malware_section = ctk.CTkFrame(self.security_frame)
        malware_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(malware_section, text="🛡️ Malware Protection", font=("Arial", 18, "bold")).pack(pady=10)
        
        malware_buttons = ctk.CTkFrame(malware_section)
        malware_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(malware_buttons, text="Quick Scan", command=self.quick_malware_scan, fg_color="#E53E3E").pack(side="left", padx=5)
        ctk.CTkButton(malware_buttons, text="Deep Scan", command=self.deep_malware_scan, fg_color="#C53030").pack(side="left", padx=5)
        ctk.CTkButton(malware_buttons, text="Quarantine Threats", command=self.quarantine_threats, fg_color="#9B2C2C").pack(side="left", padx=5)
        
        self.malware_status = ctk.CTkTextbox(malware_section, height=120)
        self.malware_status.pack(fill="x", padx=10, pady=5)
        self.malware_status.insert("1.0", "Ready for malware scan...")
        
        # Privacy Protection Section
        privacy_section = ctk.CTkFrame(self.security_frame)
        privacy_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(privacy_section, text="🔒 Privacy Protection", font=("Arial", 18, "bold")).pack(pady=10)
        
        privacy_buttons = ctk.CTkFrame(privacy_section)
        privacy_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(privacy_buttons, text="Clear Browser Data", command=self.clear_browser_data, fg_color="#2D3748").pack(side="left", padx=5)
        ctk.CTkButton(privacy_buttons, text="Clear System Traces", command=self.clear_system_traces, fg_color="#1A202C").pack(side="left", padx=5)
        ctk.CTkButton(privacy_buttons, text="Secure Delete", command=self.secure_delete_dialog, fg_color="#171923").pack(side="left", padx=5)
        
        self.privacy_status = ctk.CTkLabel(privacy_section, text="Privacy protection ready", font=("Arial", 12))
        self.privacy_status.pack(pady=5)
        
        # Network Security Section
        network_section = ctk.CTkFrame(self.security_frame)
        network_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(network_section, text="🌐 Network Security", font=("Arial", 18, "bold")).pack(pady=10)
        
        network_buttons = ctk.CTkFrame(network_section)
        network_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(network_buttons, text="Scan Connections", command=self.scan_network_connections, fg_color="#2B6CB0").pack(side="left", padx=5)
        ctk.CTkButton(network_buttons, text="Block Threats", command=self.block_network_threats, fg_color="#2C5282").pack(side="left", padx=5)
        ctk.CTkButton(network_buttons, text="Network Analysis", command=self.network_analysis, fg_color="#2A4365").pack(side="left", padx=5)
        
        self.network_status = ctk.CTkTextbox(network_section, height=100)
        self.network_status.pack(fill="x", padx=10, pady=5)
        self.network_status.insert("1.0", "Network security monitoring ready...")
        
        # System Hardening Section
        hardening_section = ctk.CTkFrame(self.security_frame)
        hardening_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(hardening_section, text="⚔️ System Hardening", font=("Arial", 18, "bold")).pack(pady=10)
        
        hardening_buttons = ctk.CTkFrame(hardening_section)
        hardening_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(hardening_buttons, text="Harden Windows", command=self.harden_windows, fg_color="#38A169").pack(side="left", padx=5)
        ctk.CTkButton(hardening_buttons, text="Registry Scan", command=self.scan_registry_threats, fg_color="#2F855A").pack(side="left", padx=5)
        ctk.CTkButton(hardening_buttons, text="Enable Protection", command=self.enable_advanced_protection, fg_color="#276749").pack(side="left", padx=5)
        
        self.hardening_status = ctk.CTkLabel(hardening_section, text="System hardening ready", font=("Arial", 12))
        self.hardening_status.pack(pady=5)
        
        # Elite Security Section
        elite_security_section = ctk.CTkFrame(self.security_frame)
        elite_security_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(elite_security_section, text="👑 Elite Security", font=("Arial", 18, "bold")).pack(pady=10)
        
        elite_security_buttons = ctk.CTkFrame(elite_security_section)
        elite_security_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(elite_security_buttons, text="Security Audit", command=self.comprehensive_security_audit, fg_color="#805AD5").pack(side="left", padx=5)
        ctk.CTkButton(elite_security_buttons, text="Full Protection", command=self.enable_full_protection, fg_color="#6B46C1").pack(side="left", padx=5)
        ctk.CTkButton(elite_security_buttons, text="Threat Analysis", command=self.advanced_threat_analysis, fg_color="#553C9A").pack(side="left", padx=5)
        
        self.elite_security_status = ctk.CTkTextbox(elite_security_section, height=100)
        self.elite_security_status.pack(fill="x", padx=10, pady=5)
        self.elite_security_status.insert("1.0", "Elite security tools ready for deployment...")
        
        self.security_frame.pack_forget()
        
        # Status/Log panel
        self.log_panel = ctk.CTkTextbox(self, height=80)
        self.log_panel.pack(side="bottom", fill="x", padx=10, pady=5)
        self.log_panel.insert("end", "[INFO] QuantumDesk started.\n")
        self.log_panel.configure(state="disabled")

        self.show_panel("Control Panel")
        self.monitoring = True
        self.update_counter = 0  # For selective updates
          # Initialize System Optimizer and Security Tools
        self.optimizer = SystemOptimizer(log_callback=self.log)
        self.security_tools = SecurityTools(log_callback=self.log)
        
        threading.Thread(target=self.update_monitor, daemon=True).start()

    def show_panel(self, feature):
        if feature == "Control Panel":
            self.panel_label.configure(text="System Monitor")
            self.monitor_frame.pack(expand=True, fill="both", padx=20, pady=20)
            self.optimizer_frame.pack_forget()
            self.security_frame.pack_forget()
        elif feature == "System Optimizer":
            self.panel_label.configure(text="System Optimizer")
            self.optimizer_frame.pack(expand=True, fill="both", padx=20, pady=20)
            self.monitor_frame.pack_forget()
            self.security_frame.pack_forget()
        elif feature == "Security":
            self.panel_label.configure(text="Security Tools")
            self.security_frame.pack(expand=True, fill="both", padx=20, pady=20)
            self.monitor_frame.pack_forget()
            self.optimizer_frame.pack_forget()
        else:
            self.panel_label.configure(text=f"{feature} (Coming Soon)")
            self.monitor_frame.pack_forget()
            self.optimizer_frame.pack_forget()
            self.security_frame.pack_forget()
        self.log(f"Switched to {feature} panel.")

    def toggle_theme(self):
        mode = "Dark" if self.theme_toggle.get() else "Light"
        ctk.set_appearance_mode(mode)
        self.log(f"Switched to {mode} mode.")

    def log(self, message):
        self.log_panel.configure(state="normal")
        self.log_panel.insert("end", f"[LOG] {message}\n")
        self.log_panel.see("end")
        self.log_panel.configure(state="disabled")

    def update_monitor(self):
        while self.monitoring:
            self.update_counter += 1
            
            # Get system data
            cpu = psutil.cpu_percent(interval=0.1)  # Faster interval
            ram = psutil.virtual_memory().percent
            self.cpu_history.append(cpu)
            self.cpu_history.pop(0)
            self.ram_history.append(ram)
            self.ram_history.pop(0)
            
            # GPU (update less frequently)
            if self.update_counter % 2 == 0:  # Every 2nd update
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        gpu_load = int(gpu.load*100)
                        gpu_temp = int(gpu.temperature)
                    else:
                        gpu_load = 0
                        gpu_temp = 0
                except Exception:
                    gpu_load = 0
                    gpu_temp = 0
                self.gpu_history.append(gpu_load)
                self.gpu_history.pop(0)
                
            # Disks (update even less frequently)
            if self.update_counter % 5 == 0:  # Every 5th update
                partitions = [p for p in psutil.disk_partitions(all=True) if p.fstype and (p.opts.find('cdrom') == -1)]
                for i, part in enumerate(partitions):
                    try:
                        usage = psutil.disk_usage(part.mountpoint).percent
                    except Exception:
                        usage = 0
                    if i < len(self.disk_labels):
                        self.disk_labels[i].configure(text=f"{part.device} Usage: {usage}%")
                        self.disk_usage_history[part.device].append(usage)
                        self.disk_usage_history[part.device].pop(0)
                        
            # Battery and Network (update even less frequently)
            if self.update_counter % 10 == 0:  # Every 10th update
                try:
                    battery = psutil.sensors_battery()
                    battery_str = f"{battery.percent}% ({'Plugged' if battery.power_plugged else 'On Battery'})" if battery else "N/A"
                except Exception:
                    battery_str = "N/A"
                try:
                    net = psutil.net_io_counters()
                    net_str = f"Sent: {net.bytes_sent//1024//1024} MB, Recv: {net.bytes_recv//1024//1024} MB"
                except Exception:
                    net_str = "N/A"
                self.battery_label.configure(text=f"Battery: {battery_str}")
                self.net_label.configure(text=f"Network: {net_str}")
            
            # Update labels (CPU/RAM every time, others as updated above)
            self.cpu_label.configure(text=f"CPU Usage: {cpu:.1f}%")
            self.ram_label.configure(text=f"RAM Usage: {ram:.1f}%")
            if self.update_counter % 2 == 0:
                self.gpu_label.configure(text=f"GPU Usage: {gpu_load}% | Temp: {gpu_temp}°C")
            
            # Update graphs more efficiently
            self.cpu_line.set_ydata(self.cpu_history)
            self.cpu_canvas.draw_idle()  # More efficient than draw()
            
            self.ram_line.set_ydata(self.ram_history)
            self.ram_canvas.draw_idle()
            
            if self.update_counter % 2 == 0:
                self.gpu_line.set_ydata(self.gpu_history)
                self.gpu_canvas.draw_idle()
                
            # Update disk graphs less frequently
            if self.update_counter % 5 == 0:
                for i, (fig, ax, line, canvas, dev) in enumerate(self.disk_graphs):
                    if dev in self.disk_usage_history:
                        line.set_ydata(self.disk_usage_history[dev])
                        canvas.draw_idle()
            
            time.sleep(0.2)  # Faster update rate

    # System Optimizer Methods - Using SystemOptimizer module
    def free_ram(self):
        result = self.optimizer.free_ram()
        self.ram_status.configure(text=result['message'])

    def clear_cache(self):
        result = self.optimizer.clear_cache()
        self.ram_status.configure(text=result['message'])

    def optimize_memory(self):
        result = self.optimizer.optimize_memory()
        self.ram_status.configure(text=result['message'])

    def kill_heavy_processes(self):
        result = self.optimizer.kill_heavy_processes()
        self.process_list.delete("1.0", "end")
        self.process_list.insert("1.0", result['message'])

    def end_idle_apps(self):
        result = self.optimizer.end_idle_apps()
        self.process_list.delete("1.0", "end")
        self.process_list.insert("1.0", result['message'])

    def clean_chrome(self):
        result = self.optimizer.clean_chrome()
        self.process_list.delete("1.0", "end")
        self.process_list.insert("1.0", result['message'])

    def scan_startup(self):
        result = self.optimizer.scan_startup()
        self.startup_list.delete("1.0", "end")
        self.startup_list.insert("1.0", result['message'])

    def disable_heavy_startup(self):
        result = self.optimizer.disable_heavy_startup()
        self.startup_list.delete("1.0", "end")
        self.startup_list.insert("1.0", result['message'])

    def optimize_boot(self):
        result = self.optimizer.optimize_boot()
        self.startup_list.delete("1.0", "end")
        self.startup_list.insert("1.0", result['message'])

    def clean_temp(self):
        result = self.optimizer.clean_temp()
        self.cleanup_status.configure(text=result['message'])

    def empty_recycle(self):
        result = self.optimizer.empty_recycle()
        self.cleanup_status.configure(text=result['message'])

    def clear_prefetch(self):
        result = self.optimizer.clear_prefetch()
        self.cleanup_status.configure(text=result['message'])

    def clean_registry(self):
        result = self.optimizer.clean_registry()
        self.cleanup_status.configure(text=result['message'])

    def disk_cleanup(self):
        result = self.optimizer.disk_cleanup()
        self.cleanup_status.configure(text=result['message'])

    def full_system_clean(self):
        result = self.optimizer.full_system_clean()
        self.cleanup_status.configure(text=result['message'])

    def game_mode(self):
        result = self.optimizer.game_mode()
        self.perf_status.configure(text=result['message'])

    def high_performance(self):
        result = self.optimizer.high_performance()
        self.perf_status.configure(text=result['message'])

    def priority_boost(self):
        result = self.optimizer.priority_boost()
        self.perf_status.configure(text=result['message'])
    
    # Elite Tools Methods
    def auto_optimize(self):
        """Run automatic optimization based on system state"""
        result = self.optimizer.auto_optimize()
        self.elite_status.delete("1.0", "end")
        self.elite_status.insert("1.0", result['message'])
    
    def check_system_health(self):
        """Check comprehensive system health"""
        result = self.optimizer.get_system_health()
        if result['status'] == 'success':
            health = result['data']
            health_text = f"""SYSTEM HEALTH REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CPU Usage: {health['cpu_usage']:.1f}%
Memory Usage: {health['memory_usage']:.1f}%
Available Memory: {health['memory_available']}GB
Disk Usage: {health['disk_usage']:.1f}%
Active Processes: {health['process_count']}
System Uptime: {health['uptime_hours']:.1f} hours
System Status: {health['status'].upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        else:
            health_text = f"Health check failed: {result['message']}"
        
        self.elite_status.delete("1.0", "end")
        self.elite_status.insert("1.0", health_text)
    
    def elite_clean(self):
        """Perform elite-level comprehensive cleanup"""
        # Run multiple optimization operations
        self.elite_status.delete("1.0", "end")
        self.elite_status.insert("1.0", "🔥 ELITE CLEANUP INITIATED...\n")
        
        # Run comprehensive cleanup
        threading.Thread(target=self._elite_clean_thread, daemon=True).start()
    
    def _elite_clean_thread(self):
        """Background thread for elite cleanup"""
        operations = [
            ("Memory Optimization", self.optimizer.optimize_memory),
            ("Process Cleanup", self.optimizer.end_idle_apps),
            ("Temp Files", self.optimizer.clean_temp),
            ("Cache Clear", self.optimizer.clear_cache),
            ("Prefetch Clear", self.optimizer.clear_prefetch),
            ("Registry Clean", self.optimizer.clean_registry)
        ]
        
        results = []
        for i, (name, operation) in enumerate(operations):
            try:
                result = operation()
                status = "✅ COMPLETED" if result['status'] == 'success' else "❌ FAILED"
                results.append(f"{name}: {status}")
                
                # Update progress
                progress_text = f"🔥 ELITE CLEANUP IN PROGRESS...\n"
                progress_text += f"Progress: {i+1}/{len(operations)}\n\n"
                progress_text += "\n".join(results)
                
                self.elite_status.delete("1.0", "end")
                self.elite_status.insert("1.0", progress_text)
                
                time.sleep(0.5)  # Small delay for visual effect
            except Exception as e:
                results.append(f"{name}: ❌ ERROR")
        
        # Final results
        final_text = f"🔥 ELITE CLEANUP COMPLETED!\n\n"
        final_text += "\n".join(results)
        final_text += f"\n\n⚡ System optimized to elite performance levels!"
        
        self.elite_status.delete("1.0", "end")
        self.elite_status.insert("1.0", final_text)

    # Security Tools Methods - Using SecurityTools module
    def quick_malware_scan(self):
        """Run quick malware scan"""
        result = self.security_tools.quick_malware_scan()
        self.malware_status.delete("1.0", "end")
        self.malware_status.insert("1.0", result['message'])
        
        # Store threats for potential quarantine
        if result['status'] == 'success' and 'threats' in result:
            self.detected_threats = result['threats']
    
    def deep_malware_scan(self):
        """Run deep malware scan in background"""
        self.malware_status.delete("1.0", "end")
        self.malware_status.insert("1.0", "🔍 DEEP SCAN INITIATED...\nThis may take several minutes...")
        
        # Run deep scan in background
        threading.Thread(target=self._deep_scan_thread, daemon=True).start()
    
    def _deep_scan_thread(self):
        """Background thread for deep malware scan"""
        result = self.security_tools.deep_malware_scan()
        self.malware_status.delete("1.0", "end")
        self.malware_status.insert("1.0", result['message'])
        
        # Store threats for potential quarantine
        if result['status'] == 'success' and 'threats' in result:
            self.detected_threats = result['threats']
    
    def quarantine_threats(self):
        """Quarantine detected threats"""
        if hasattr(self, 'detected_threats') and self.detected_threats:
            result = self.security_tools.quarantine_threats(self.detected_threats)
            self.malware_status.delete("1.0", "end")
            self.malware_status.insert("1.0", result['message'])
        else:
            self.malware_status.delete("1.0", "end")
            self.malware_status.insert("1.0", "No threats detected to quarantine.\nRun a malware scan first.")
    
    def clear_browser_data(self):
        """Clear browser data for privacy"""
        result = self.security_tools.clear_browser_data()
        self.privacy_status.configure(text=result['message'])
    
    def clear_system_traces(self):
        """Clear system traces and logs"""
        result = self.security_tools.clear_system_traces()
        self.privacy_status.configure(text=result['message'])
    
    def secure_delete_dialog(self):
        """Show secure delete dialog (simplified)"""
        self.privacy_status.configure(text="Secure delete: Select files in file explorer, then run this tool")
    
    def scan_network_connections(self):
        """Scan network connections for threats"""
        result = self.security_tools.scan_network_connections()
        self.network_status.delete("1.0", "end")
        self.network_status.insert("1.0", result['message'])
        
        # Store suspicious connections for blocking
        if result['status'] == 'success' and 'connections' in result:
            self.suspicious_connections = result['connections']
    
    def block_network_threats(self):
        """Block suspicious network connections"""
        if hasattr(self, 'suspicious_connections') and self.suspicious_connections:
            result = self.security_tools.block_suspicious_connections(self.suspicious_connections)
            self.network_status.delete("1.0", "end")
            self.network_status.insert("1.0", result['message'])
        else:
            self.network_status.delete("1.0", "end")
            self.network_status.insert("1.0", "No suspicious connections to block.\nRun network scan first.")
    
    def network_analysis(self):
        """Perform comprehensive network analysis"""
        self.network_status.delete("1.0", "end")
        self.network_status.insert("1.0", "🌐 NETWORK ANALYSIS INITIATED...\nAnalyzing connections and traffic...")
        
        # Run analysis in background
        threading.Thread(target=self._network_analysis_thread, daemon=True).start()
    
    def _network_analysis_thread(self):
        """Background thread for network analysis"""
        # Run network scan and display results
        result = self.security_tools.scan_network_connections()
        
        analysis_text = f"🌐 NETWORK ANALYSIS COMPLETE\n"
        analysis_text += f"════════════════════════════════════\n"
        analysis_text += result['message']
        
        self.network_status.delete("1.0", "end")
        self.network_status.insert("1.0", analysis_text)
    
    def harden_windows(self):
        """Apply Windows security hardening"""
        result = self.security_tools.harden_windows_settings()
        self.hardening_status.configure(text=result['message'][:100] + "..." if len(result['message']) > 100 else result['message'])
    
    def scan_registry_threats(self):
        """Scan registry for threats"""
        result = self.security_tools.scan_registry_threats()
        self.hardening_status.configure(text=f"Registry scan: {result['message'][:50]}...")
    
    def enable_advanced_protection(self):
        """Enable advanced security protection"""
        result = self.security_tools.enable_advanced_protection()
        self.hardening_status.configure(text=result['message'][:100] + "..." if len(result['message']) > 100 else result['message'])
    
    def comprehensive_security_audit(self):
        """Run comprehensive security audit"""
        self.elite_security_status.delete("1.0", "end")
        self.elite_security_status.insert("1.0", "🛡️ SECURITY AUDIT INITIATED...\nAnalyzing system security...")
        
        # Run audit in background
        threading.Thread(target=self._security_audit_thread, daemon=True).start()
    
    def _security_audit_thread(self):
        """Background thread for security audit"""
        result = self.security_tools.comprehensive_security_audit()
        self.elite_security_status.delete("1.0", "end")
        self.elite_security_status.insert("1.0", result['message'])
    
    def enable_full_protection(self):
        """Enable full security protection suite"""
        self.elite_security_status.delete("1.0", "end")
        self.elite_security_status.insert("1.0", "🛡️ FULL PROTECTION ACTIVATION...\nEnabling all security features...")
        
        # Run full protection in background
        threading.Thread(target=self._full_protection_thread, daemon=True).start()
    
    def _full_protection_thread(self):
        """Background thread for full protection activation"""
        operations = [
            ("System Hardening", self.security_tools.harden_windows_settings),
            ("Advanced Protection", self.security_tools.enable_advanced_protection),
            ("Privacy Enhancement", self.security_tools.clear_system_traces),
            ("Network Security", self.security_tools.scan_network_connections)
        ]
        
        results = []
        for i, (name, operation) in enumerate(operations):
            try:
                result = operation()
                status = "✅ ENABLED" if result['status'] == 'success' else "❌ FAILED"
                results.append(f"{name}: {status}")
                
                # Update progress
                progress_text = f"🛡️ FULL PROTECTION ACTIVATION...\n"
                progress_text += f"Progress: {i+1}/{len(operations)}\n\n"
                progress_text += "\n".join(results)
                
                self.elite_security_status.delete("1.0", "end")
                self.elite_security_status.insert("1.0", progress_text)
                
                time.sleep(1)  # Delay for visual effect
            except Exception as e:
                results.append(f"{name}: ❌ ERROR")
        
        # Final results
        final_text = f"🛡️ FULL PROTECTION ACTIVATED!\n\n"
        final_text += "\n".join(results)
        final_text += f"\n\n🔒 System secured to elite protection levels!"
        
        self.elite_security_status.delete("1.0", "end")
        self.elite_security_status.insert("1.0", final_text)
    
    def advanced_threat_analysis(self):
        """Perform advanced threat analysis"""
        self.elite_security_status.delete("1.0", "end")
        self.elite_security_status.insert("1.0", "🔍 ADVANCED THREAT ANALYSIS...\nDeep scanning for sophisticated threats...")
        
        # Run threat analysis in background
        threading.Thread(target=self._threat_analysis_thread, daemon=True).start()
    
    def _threat_analysis_thread(self):
        """Background thread for advanced threat analysis"""
        # Combine multiple security scans
        operations = [
            ("Malware Analysis", self.security_tools.quick_malware_scan),
            ("Registry Threats", self.security_tools.scan_registry_threats),
            ("Network Analysis", self.security_tools.scan_network_connections),
            ("Security Audit", self.security_tools.comprehensive_security_audit)
        ]
        
        analysis_results = []
        threat_count = 0
        
        for i, (name, operation) in enumerate(operations):
            try:
                result = operation()
                if result['status'] == 'success':
                    # Extract threat counts
                    if 'threats' in result:
                        threats = len(result['threats'])
                        threat_count += threats
                        analysis_results.append(f"{name}: {threats} threats")
                    elif 'connections' in result:
                        threats = len(result['connections'])
                        threat_count += threats
                        analysis_results.append(f"{name}: {threats} suspicious")
                    else:
                        analysis_results.append(f"{name}: ✅ Clean")
                else:
                    analysis_results.append(f"{name}: ❌ Failed")
                
                # Update progress
                progress_text = f"🔍 ADVANCED THREAT ANALYSIS...\n"
                progress_text += f"Progress: {i+1}/{len(operations)}\n\n"
                progress_text += "\n".join(analysis_results)
                
                self.elite_security_status.delete("1.0", "end")
                self.elite_security_status.insert("1.0", progress_text)
                
                time.sleep(0.5)
            except Exception as e:
                analysis_results.append(f"{name}: ❌ Error")
        
        # Final threat analysis report
        risk_level = "🟢 LOW" if threat_count == 0 else "🟡 MEDIUM" if threat_count < 5 else "🔴 HIGH"
        
        final_text = f"🔍 THREAT ANALYSIS COMPLETE!\n"
        final_text += f"════════════════════════════════════\n"
        final_text += f"TOTAL THREATS DETECTED: {threat_count}\n"
        final_text += f"RISK LEVEL: {risk_level}\n\n"
        final_text += "ANALYSIS RESULTS:\n"
        final_text += "\n".join(analysis_results)
        
        if threat_count > 0:
            final_text += f"\n\n⚠️ IMMEDIATE ACTION RECOMMENDED:\n"
            final_text += f"• Run malware quarantine\n"
            final_text += f"• Block suspicious connections\n"
            final_text += f"• Enable full protection"
        else:
            final_text += f"\n\n✅ SYSTEM SECURE - No threats detected"
        
        self.elite_security_status.delete("1.0", "end")
        self.elite_security_status.insert("1.0", final_text)

if __name__ == "__main__":
    app = QuantumDeskGUI()
    app.mainloop()
