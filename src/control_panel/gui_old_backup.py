import customtkinter as ctk
import psutil
import threading
import time
import os
import GPUtil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from system_optimizer import SystemOptimizer
from security_prefs import SecurityTools
from file_folder_tools.file_tools import EliteFileTools

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
        hardening_buttons.pack(fill="x", padx=10, pady=5)        ctk.CTkButton(hardening_buttons, text="Harden Windows", command=self.harden_windows, fg_color="#38A169").pack(side="left", padx=5)
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
        
        # --- File Tools Panel ---
        self.file_tools_frame = ctk.CTkScrollableFrame(self.main_panel, corner_radius=10)
        
        # File Search Section
        search_section = ctk.CTkFrame(self.file_tools_frame)
        search_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(search_section, text="🔍 Advanced File Search", font=("Arial", 18, "bold")).pack(pady=10)
        
        search_input_frame = ctk.CTkFrame(search_section)
        search_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.search_path_entry = ctk.CTkEntry(search_input_frame, placeholder_text="Search path (leave empty for all drives)", width=300)
        self.search_path_entry.pack(side="left", padx=5)
        
        self.search_pattern_entry = ctk.CTkEntry(search_input_frame, placeholder_text="File pattern (e.g., *.txt, *.pdf)", width=200)
        self.search_pattern_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(search_input_frame, text="Browse", command=self.browse_search_path, width=80).pack(side="left", padx=5)
        
        search_buttons = ctk.CTkFrame(search_section)
        search_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(search_buttons, text="Quick Search", command=self.quick_file_search, fg_color="#4ECDC4").pack(side="left", padx=5)
        ctk.CTkButton(search_buttons, text="Advanced Search", command=self.advanced_file_search, fg_color="#45B7D1").pack(side="left", padx=5)
        ctk.CTkButton(search_buttons, text="Content Search", command=self.content_search, fg_color="#96CEB4").pack(side="left", padx=5)
        
        self.search_results = ctk.CTkTextbox(search_section, height=120)
        self.search_results.pack(fill="x", padx=10, pady=5)
        self.search_results.insert("1.0", "Search results will appear here...")
        
        # File Operations Section
        operations_section = ctk.CTkFrame(self.file_tools_frame)
        operations_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(operations_section, text="📁 File Operations", font=("Arial", 18, "bold")).pack(pady=10)
        
        ops_input_frame = ctk.CTkFrame(operations_section)
        ops_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.source_path_entry = ctk.CTkEntry(ops_input_frame, placeholder_text="Source file/folder path", width=250)
        self.source_path_entry.pack(side="left", padx=5)
        
        self.dest_path_entry = ctk.CTkEntry(ops_input_frame, placeholder_text="Destination path", width=250)
        self.dest_path_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(ops_input_frame, text="Browse Source", command=self.browse_source_path, width=100).pack(side="left", padx=5)
        ctk.CTkButton(ops_input_frame, text="Browse Dest", command=self.browse_dest_path, width=100).pack(side="left", padx=5)
        
        ops_buttons = ctk.CTkFrame(operations_section)
        ops_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(ops_buttons, text="Secure Copy", command=self.secure_copy_file, fg_color="#FF6B6B").pack(side="left", padx=5)
        ctk.CTkButton(ops_buttons, text="Secure Move", command=self.secure_move_file, fg_color="#FFD93D").pack(side="left", padx=5)
        ctk.CTkButton(ops_buttons, text="Secure Delete", command=self.secure_delete_file, fg_color="#E74C3C").pack(side="left", padx=5)
        ctk.CTkButton(ops_buttons, text="Analyze File", command=self.analyze_file, fg_color="#9B59B6").pack(side="left", padx=5)
        
        self.operations_status = ctk.CTkLabel(operations_section, text="Ready for file operations", font=("Arial", 12))
        self.operations_status.pack(pady=5)
        
        # Duplicate Detection Section
        duplicate_section = ctk.CTkFrame(self.file_tools_frame)
        duplicate_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(duplicate_section, text="🔍 Duplicate Detection", font=("Arial", 18, "bold")).pack(pady=10)
        
        dup_input_frame = ctk.CTkFrame(duplicate_section)
        dup_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.dup_scan_path_entry = ctk.CTkEntry(dup_input_frame, placeholder_text="Path to scan for duplicates", width=400)
        self.dup_scan_path_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(dup_input_frame, text="Browse", command=self.browse_dup_path, width=80).pack(side="left", padx=5)
        
        dup_buttons = ctk.CTkFrame(duplicate_section)
        dup_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(dup_buttons, text="Find Duplicates", command=self.find_duplicates, fg_color="#3498DB").pack(side="left", padx=5)
        ctk.CTkButton(dup_buttons, text="Smart Cleanup", command=self.smart_duplicate_cleanup, fg_color="#2ECC71").pack(side="left", padx=5)
        ctk.CTkButton(dup_buttons, text="View Results", command=self.view_duplicate_results, fg_color="#F39C12").pack(side="left", padx=5)
        
        self.duplicate_results = ctk.CTkTextbox(duplicate_section, height=100)
        self.duplicate_results.pack(fill="x", padx=10, pady=5)
        self.duplicate_results.insert("1.0", "Duplicate scan results will appear here...")
        
        # File Organization Section
        organize_section = ctk.CTkFrame(self.file_tools_frame)
        organize_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(organize_section, text="📋 Smart Organization", font=("Arial", 18, "bold")).pack(pady=10)
        
        org_input_frame = ctk.CTkFrame(organize_section)
        org_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.organize_path_entry = ctk.CTkEntry(org_input_frame, placeholder_text="Path to organize", width=400)
        self.organize_path_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(org_input_frame, text="Browse", command=self.browse_organize_path, width=80).pack(side="left", padx=5)
        
        org_buttons = ctk.CTkFrame(organize_section)
        org_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(org_buttons, text="Auto Organize", command=self.auto_organize_files, fg_color="#8E44AD").pack(side="left", padx=5)
        ctk.CTkButton(org_buttons, text="Sort by Date", command=self.sort_by_date, fg_color="#27AE60").pack(side="left", padx=5)
        ctk.CTkButton(org_buttons, text="Sort by Type", command=self.sort_by_type, fg_color="#E67E22").pack(side="left", padx=5)
        ctk.CTkButton(org_buttons, text="Bulk Rename", command=self.bulk_rename_dialog, fg_color="#16A085").pack(side="left", padx=5)
        
        self.organize_status = ctk.CTkLabel(organize_section, text="Ready to organize files", font=("Arial", 12))
        self.organize_status.pack(pady=5)
        
        # Disk Analysis Section
        analysis_section = ctk.CTkFrame(self.file_tools_frame)
        analysis_section.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(analysis_section, text="📊 Disk Analysis", font=("Arial", 18, "bold")).pack(pady=10)
        
        analysis_input_frame = ctk.CTkFrame(analysis_section)
        analysis_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.analysis_path_entry = ctk.CTkEntry(analysis_input_frame, placeholder_text="Path to analyze", width=400)
        self.analysis_path_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(analysis_input_frame, text="Browse", command=self.browse_analysis_path, width=80).pack(side="left", padx=5)
        
        analysis_buttons = ctk.CTkFrame(analysis_section)
        analysis_buttons.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(analysis_buttons, text="Disk Usage", command=self.analyze_disk_usage, fg_color="#D35400").pack(side="left", padx=5)
        ctk.CTkButton(analysis_buttons, text="Large Files", command=self.find_large_files, fg_color="#C0392B").pack(side="left", padx=5)
        ctk.CTkButton(analysis_buttons, text="File Types", command=self.analyze_file_types, fg_color="#8E44AD").pack(side="left", padx=5)
        ctk.CTkButton(analysis_buttons, text="Generate Report", command=self.generate_analysis_report, fg_color="#2C3E50").pack(side="left", padx=5)
        
        self.analysis_results = ctk.CTkTextbox(analysis_section, height=120)
        self.analysis_results.pack(fill="x", padx=10, pady=5)
        self.analysis_results.insert("1.0", "Analysis results will appear here...")
        
        self.file_tools_frame.pack_forget()
        
        # Status/Log panel
        self.log_panel = ctk.CTkTextbox(self, height=80)
        self.log_panel.pack(side="bottom", fill="x", padx=10, pady=5)
        self.log_panel.insert("end", "[INFO] QuantumDesk started.\n")
        self.log_panel.configure(state="disabled")

        self.show_panel("Control Panel")
        self.monitoring = True
        self.update_counter = 0  # For selective updates          # Initialize System Optimizer and Security Tools
        self.optimizer = SystemOptimizer(log_callback=self.log)
        self.security_tools = SecurityTools(log_callback=self.log)
        self.file_tools = EliteFileTools(log_callback=self.log)
        
        threading.Thread(target=self.update_monitor, daemon=True).start()    def show_panel(self, feature):
        if feature == "Control Panel":
            self.panel_label.configure(text="System Monitor")
            self.monitor_frame.pack(expand=True, fill="both", padx=20, pady=20)
            self.optimizer_frame.pack_forget()
            self.security_frame.pack_forget()
            self.file_tools_frame.pack_forget()
        elif feature == "System Optimizer":
            self.panel_label.configure(text="System Optimizer")
            self.optimizer_frame.pack(expand=True, fill="both", padx=20, pady=20)
            self.monitor_frame.pack_forget()
            self.security_frame.pack_forget()
            self.file_tools_frame.pack_forget()
        elif feature == "Security":
            self.panel_label.configure(text="Security Tools")
            self.security_frame.pack(expand=True, fill="both", padx=20, pady=20)
            self.monitor_frame.pack_forget()
            self.optimizer_frame.pack_forget()
            self.file_tools_frame.pack_forget()
        elif feature == "File Tools":
            self.panel_label.configure(text="Elite File Tools")
            self.file_tools_frame.pack(expand=True, fill="both", padx=20, pady=20)
            self.monitor_frame.pack_forget()
            self.optimizer_frame.pack_forget()
            self.security_frame.pack_forget()
        else:
            self.panel_label.configure(text=f"{feature} (Coming Soon)")
            self.monitor_frame.pack_forget()
            self.optimizer_frame.pack_forget()
            self.security_frame.pack_forget()
            self.file_tools_frame.pack_forget()
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
    
    # === FILE TOOLS METHODS ===
    
    def browse_search_path(self):
        """Browse for search path"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Search Directory")
        if path:
            self.search_path_entry.delete(0, 'end')
            self.search_path_entry.insert(0, path)
    
    def browse_source_path(self):
        """Browse for source file/folder"""
        from tkinter import filedialog
        path = filedialog.askopenfilename(title="Select Source File") or filedialog.askdirectory(title="Select Source Directory")
        if path:
            self.source_path_entry.delete(0, 'end')
            self.source_path_entry.insert(0, path)
    
    def browse_dest_path(self):
        """Browse for destination path"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Destination Directory")
        if path:
            self.dest_path_entry.delete(0, 'end')
            self.dest_path_entry.insert(0, path)
    
    def browse_dup_path(self):
        """Browse for duplicate scan path"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Directory to Scan for Duplicates")
        if path:
            self.dup_scan_path_entry.delete(0, 'end')
            self.dup_scan_path_entry.insert(0, path)
    
    def browse_organize_path(self):
        """Browse for organization path"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Directory to Organize")
        if path:
            self.organize_path_entry.delete(0, 'end')
            self.organize_path_entry.insert(0, path)
    
    def browse_analysis_path(self):
        """Browse for analysis path"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Directory to Analyze")
        if path:
            self.analysis_path_entry.delete(0, 'end')
            self.analysis_path_entry.insert(0, path)
    
    def quick_file_search(self):
        """Perform quick file search"""
        def search_thread():
            try:
                search_path = self.search_path_entry.get() or None
                pattern = self.search_pattern_entry.get() or "*"
                
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", "🔍 Searching files...\n")
                
                results = self.file_tools.quick_search(search_path, pattern)
                
                if results['status'] == 'success' and results['files']:
                    output = f"✅ Found {len(results['files'])} files:\n\n"
                    for file_path in results['files'][:50]:  # Limit display
                        try:
                            size = os.path.getsize(file_path)
                            size_str = self._format_size(size)
                            output += f"📄 {file_path} ({size_str})\n"
                        except:
                            output += f"📄 {file_path}\n"
                    if len(results['files']) > 50:
                        output += f"\n... and {len(results['files']) - 50} more files"
                else:
                    output = f"❌ {results.get('message', 'No files found')}
                
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", output)
                
            except Exception as e:
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", f"❌ Search error: {str(e)}")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def advanced_file_search(self):
        """Perform advanced file search with filters"""
        def search_thread():
            try:
                search_path = self.search_path_entry.get() or None
                pattern = self.search_pattern_entry.get() or "*"
                
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", "🔍 Advanced searching...\n")
                
                results = self.file_tools.advanced_search(
                    search_path, 
                    pattern,
                    min_size=0,
                    max_size=None,
                    days_old=None
                )
                
                if results['status'] == 'success' and results['files']:
                    output = f"✅ Advanced search found {len(results['files'])} files:\n\n"
                    for file_info in results['files'][:30]:
                        output += f"📄 {file_info['path']}\n"
                        output += f"   Size: {self._format_size(file_info['size'])}\n"
                        output += f"   Modified: {file_info['modified']}\n\n"
                    if len(results['files']) > 30:
                        output += f"... and {len(results['files']) - 30} more files"
                else:
                    output = f"❌ {results.get('message', 'No files found')}
                
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", output)
                
            except Exception as e:
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", f"❌ Advanced search error: {str(e)}")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def content_search(self):
        """Search file contents"""
        def search_thread():
            try:
                search_path = self.search_path_entry.get() or os.getcwd()
                pattern = self.search_pattern_entry.get()
                
                if not pattern:
                    self.search_results.delete("1.0", "end")
                    self.search_results.insert("1.0", "❌ Please enter search text in the pattern field")
                    return
                
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", f"🔍 Searching for '{pattern}' in file contents...\n")
                
                results = self.file_tools.search_content(search_path, pattern)
                
                if results['status'] == 'success' and results['matches']:
                    output = f"✅ Found '{pattern}' in {len(results['matches'])} files:\n\n"
                    for match in results['matches'][:20]:
                        output += f"📄 {match['file']}\n"
                        output += f"   Line {match['line']}: {match['content'][:100]}...\n\n"
                    if len(results['matches']) > 20:
                        output += f"... and {len(results['matches']) - 20} more matches"
                else:
                    output = f"❌ {results.get('message', 'No matches found')}
                
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", output)
                
            except Exception as e:
                self.search_results.delete("1.0", "end")
                self.search_results.insert("1.0", f"❌ Content search error: {str(e)}")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def secure_copy_file(self):
        """Secure copy operation"""
        def copy_thread():
            try:
                source = self.source_path_entry.get()
                dest = self.dest_path_entry.get()
                
                if not source or not dest:
                    self.operations_status.configure(text="❌ Please specify source and destination paths")
                    return
                
                self.operations_status.configure(text="📋 Copying files...")
                
                result = self.file_tools.secure_copy(source, dest)
                
                if result['status'] == 'success':
                    self.operations_status.configure(text="✅ Copy completed successfully")
                    self.log(f"File copied: {source} → {dest}")
                else:
                    self.operations_status.configure(text=f"❌ Copy failed: {result['message']}")
                    
            except Exception as e:
                self.operations_status.configure(text=f"❌ Copy error: {str(e)}")
        
        threading.Thread(target=copy_thread, daemon=True).start()
    
    def secure_move_file(self):
        """Secure move operation"""
        def move_thread():
            try:
                source = self.source_path_entry.get()
                dest = self.dest_path_entry.get()
                
                if not source or not dest:
                    self.operations_status.configure(text="❌ Please specify source and destination paths")
                    return
                
                self.operations_status.configure(text="📋 Moving files...")
                
                result = self.file_tools.secure_move(source, dest)
                
                if result['status'] == 'success':
                    self.operations_status.configure(text="✅ Move completed successfully")
                    self.log(f"File moved: {source} → {dest}")
                else:
                    self.operations_status.configure(text=f"❌ Move failed: {result['message']}")
                    
            except Exception as e:
                self.operations_status.configure(text=f"❌ Move error: {str(e)}")
        
        threading.Thread(target=move_thread, daemon=True).start()
    
    def secure_delete_file(self):
        """Secure delete operation"""
        def delete_thread():
            try:
                source = self.source_path_entry.get()
                
                if not source:
                    self.operations_status.configure(text="❌ Please specify file/folder to delete")
                    return
                
                # Confirmation dialog
                import tkinter.messagebox as msgbox
                if not msgbox.askyesno("Confirm Delete", f"Are you sure you want to securely delete:\n{source}"):
                    return
                
                self.operations_status.configure(text="🗑️ Securely deleting...")
                
                result = self.file_tools.secure_delete(source)
                
                if result['status'] == 'success':
                    self.operations_status.configure(text="✅ Delete completed successfully")
                    self.log(f"File securely deleted: {source}")
                    self.source_path_entry.delete(0, 'end')
                else:
                    self.operations_status.configure(text=f"❌ Delete failed: {result['message']}")
                    
            except Exception as e:
                self.operations_status.configure(text=f"❌ Delete error: {str(e)}")
        
        threading.Thread(target=delete_thread, daemon=True).start()
    
    def analyze_file(self):
        """Analyze file properties"""
        def analyze_thread():
            try:
                source = self.source_path_entry.get()
                
                if not source:
                    self.operations_status.configure(text="❌ Please specify file to analyze")
                    return
                
                self.operations_status.configure(text="🔍 Analyzing file...")
                
                result = self.file_tools.analyze_file(source)
                
                if result['status'] == 'success':
                    analysis = result['analysis']
                    info = f"File Analysis:\n"
                    info += f"📄 Path: {analysis['path']}\n"
                    info += f"📏 Size: {self._format_size(analysis['size'])}\n"
                    info += f"📅 Created: {analysis['created']}\n"
                    info += f"📅 Modified: {analysis['modified']}\n"
                    info += f"🔒 Permissions: {analysis['permissions']}\n"
                    info += f"🏷️ Type: {analysis['type']}\n"
                    
                    if 'hash' in analysis:
                        info += f"🔗 MD5: {analysis['hash']}\n"
                    
                    # Show in a dialog
                    import tkinter.messagebox as msgbox
                    msgbox.showinfo("File Analysis", info)
                    
                    self.operations_status.configure(text="✅ Analysis completed")
                else:
                    self.operations_status.configure(text=f"❌ Analysis failed: {result['message']}")
                    
            except Exception as e:
                self.operations_status.configure(text=f"❌ Analysis error: {str(e)}")
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def find_duplicates(self):
        """Find duplicate files"""
        def duplicate_thread():
            try:
                scan_path = self.dup_scan_path_entry.get()
                
                if not scan_path:
                    self.duplicate_results.delete("1.0", "end")
                    self.duplicate_results.insert("1.0", "❌ Please specify path to scan")
                    return
                
                self.duplicate_results.delete("1.0", "end")
                self.duplicate_results.insert("1.0", "🔍 Scanning for duplicates...\n")
                
                result = self.file_tools.find_duplicates(scan_path)
                
                if result['status'] == 'success':
                    duplicates = result['duplicates']
                    total_waste = sum(group['waste_size'] for group in duplicates)
                    
                    output = f"✅ Duplicate scan complete!\n"
                    output += f"📊 Found {len(duplicates)} duplicate groups\n"
                    output += f"💾 Wasted space: {self._format_size(total_waste)}\n\n"
                    
                    for i, group in enumerate(duplicates[:10]):  # Show first 10 groups
                        output += f"Group {i+1} ({len(group['files'])} files, {self._format_size(group['size'])} each):\n"
                        for file_path in group['files'][:3]:  # Show first 3 files
                            output += f"  📄 {file_path}\n"
                        if len(group['files']) > 3:
                            output += f"  ... and {len(group['files']) - 3} more\n"
                        output += "\n"
                    
                    if len(duplicates) > 10:
                        output += f"... and {len(duplicates) - 10} more groups"
                else:
                    output = f"❌ {result.get('message', 'Duplicate scan failed')}
                
                self.duplicate_results.delete("1.0", "end")
                self.duplicate_results.insert("1.0", output)
                
            except Exception as e:
                self.duplicate_results.delete("1.0", "end")
                self.duplicate_results.insert("1.0", f"❌ Duplicate scan error: {str(e)}")
        
        threading.Thread(target=duplicate_thread, daemon=True).start()
    
    def smart_duplicate_cleanup(self):
        """Smart cleanup of duplicates"""
        def cleanup_thread():
            try:
                scan_path = self.dup_scan_path_entry.get()
                
                if not scan_path:
                    self.duplicate_results.delete("1.0", "end")
                    self.duplicate_results.insert("1.0", "❌ Please specify path to scan")
                    return
                
                import tkinter.messagebox as msgbox
                if not msgbox.askyesno("Confirm Cleanup", "This will automatically delete duplicate files. Continue?"):
                    return
                
                self.duplicate_results.delete("1.0", "end")
                self.duplicate_results.insert("1.0", "🧹 Smart cleanup in progress...\n")
                
                result = self.file_tools.smart_duplicate_cleanup(scan_path)
                
                if result['status'] == 'success':
                    output = f"✅ Cleanup complete!\n"
                    output += f"🗑️ Deleted {result['deleted_count']} duplicate files\n"
                    output += f"💾 Freed space: {self._format_size(result['freed_space'])}\n"
                    output += f"🛡️ Kept {result['kept_count']} original files"
                else:
                    output = f"❌ {result.get('message', 'Cleanup failed')}
                
                self.duplicate_results.delete("1.0", "end")
                self.duplicate_results.insert("1.0", output)
                
                self.log(f"Duplicate cleanup: {result.get('deleted_count', 0)} files deleted")
                
            except Exception as e:
                self.duplicate_results.delete("1.0", "end")
                self.duplicate_results.insert("1.0", f"❌ Cleanup error: {str(e)}")
        
        threading.Thread(target=cleanup_thread, daemon=True).start()
    
    def view_duplicate_results(self):
        """View detailed duplicate results in a new window"""
        try:
            # Create new window for detailed results
            results_window = ctk.CTkToplevel(self)
            results_window.title("Duplicate Files - Detailed Results")
            results_window.geometry("800x600")
            
            # Scrollable text widget
            results_text = ctk.CTkTextbox(results_window, height=500)
            results_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Get current results from the main display
            current_results = self.duplicate_results.get("1.0", "end")
            results_text.insert("1.0", current_results)
            
            # Add buttons for actions
            button_frame = ctk.CTkFrame(results_window)
            button_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkButton(button_frame, text="Close", 
                         command=results_window.destroy).pack(side="right", padx=5)
                         
        except Exception as e:
            self.log(f"Error viewing duplicate results: {str(e)}")
    
    def auto_organize_files(self):
        """Auto organize files by type"""
        def organize_thread():
            try:
                organize_path = self.organize_path_entry.get()
                
                if not organize_path:
                    self.organize_status.configure(text="❌ Please specify path to organize")
                    return
                
                self.organize_status.configure(text="📋 Auto organizing files...")
                
                result = self.file_tools.auto_organize(organize_path)
                
                if result['status'] == 'success':
                    self.organize_status.configure(text=f"✅ Organized {result['moved_count']} files")
                    self.log(f"Auto organized {result['moved_count']} files in {organize_path}")
                else:
                    self.organize_status.configure(text=f"❌ Organization failed: {result['message']}")
                    
            except Exception as e:
                self.organize_status.configure(text=f"❌ Organization error: {str(e)}")
        
        threading.Thread(target=organize_thread, daemon=True).start()
    
    def sort_by_date(self):
        """Sort files by date"""
        def sort_thread():
            try:
                organize_path = self.organize_path_entry.get()
                
                if not organize_path:
                    self.organize_status.configure(text="❌ Please specify path to organize")
                    return
                
                self.organize_status.configure(text="📅 Sorting by date...")
                
                result = self.file_tools.sort_by_date(organize_path)
                
                if result['status'] == 'success':
                    self.organize_status.configure(text=f"✅ Sorted {result['moved_count']} files by date")
                    self.log(f"Sorted {result['moved_count']} files by date in {organize_path}")
                else:
                    self.organize_status.configure(text=f"❌ Sort failed: {result['message']}")
                    
            except Exception as e:
                self.organize_status.configure(text=f"❌ Sort error: {str(e)}")
        
        threading.Thread(target=sort_thread, daemon=True).start()
    
    def sort_by_type(self):
        """Sort files by type"""
        def sort_thread():
            try:
                organize_path = self.organize_path_entry.get()
                
                if not organize_path:
                    self.organize_status.configure(text="❌ Please specify path to organize")
                    return
                
                self.organize_status.configure(text="📁 Sorting by type...")
                
                result = self.file_tools.sort_by_type(organize_path)
                
                if result['status'] == 'success':
                    self.organize_status.configure(text=f"✅ Sorted {result['moved_count']} files by type")
                    self.log(f"Sorted {result['moved_count']} files by type in {organize_path}")
                else:
                    self.organize_status.configure(text=f"❌ Sort failed: {result['message']}")
                    
            except Exception as e:
                self.organize_status.configure(text=f"❌ Sort error: {str(e)}")
        
        threading.Thread(target=sort_thread, daemon=True).start()
    
    def bulk_rename_dialog(self):
        """Open bulk rename dialog"""
        try:
            # Create bulk rename window
            rename_window = ctk.CTkToplevel(self)
            rename_window.title("Bulk Rename Files")
            rename_window.geometry("600x400")
            
            # Path selection
            path_frame = ctk.CTkFrame(rename_window)
            path_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(path_frame, text="Directory:").pack(side="left", padx=5)
            path_entry = ctk.CTkEntry(path_frame, width=400)
            path_entry.pack(side="left", padx=5)
            path_entry.insert(0, self.organize_path_entry.get())
            
            def browse_rename_path():
                from tkinter import filedialog
                path = filedialog.askdirectory(title="Select Directory for Bulk Rename")
                if path:
                    path_entry.delete(0, 'end')
                    path_entry.insert(0, path)
            
            ctk.CTkButton(path_frame, text="Browse", command=browse_rename_path).pack(side="left", padx=5)
            
            # Rename options
            options_frame = ctk.CTkFrame(rename_window)
            options_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(options_frame, text="Rename Pattern:").pack(anchor="w", padx=5)
            pattern_entry = ctk.CTkEntry(options_frame, placeholder_text="e.g., file_{number}.{ext}")
            pattern_entry.pack(fill="x", padx=5, pady=5)
            
            ctk.CTkLabel(options_frame, text="Filter (file extension):").pack(anchor="w", padx=5)
            filter_entry = ctk.CTkEntry(options_frame, placeholder_text="e.g., .jpg, .txt (leave empty for all)")
            filter_entry.pack(fill="x", padx=5, pady=5)
            
            # Preview area
            preview_frame = ctk.CTkFrame(rename_window)
            preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(preview_frame, text="Preview:").pack(anchor="w", padx=5)
            preview_text = ctk.CTkTextbox(preview_frame)
            preview_text.pack(fill="both", expand=True, padx=5, pady=5)
            
            def preview_rename():
                try:
                    path = path_entry.get()
                    pattern = pattern_entry.get()
                    file_filter = filter_entry.get()
                    
                    if not path or not pattern:
                        preview_text.delete("1.0", "end")
                        preview_text.insert("1.0", "Please specify directory and pattern")
                        return
                    
                    result = self.file_tools.preview_bulk_rename(path, pattern, file_filter)
                    
                    if result['status'] == 'success':
                        preview_content = f"Preview for {len(result['preview'])} files:\n\n"
                        for old_name, new_name in result['preview'][:20]:
                            preview_content += f"{old_name} → {new_name}\n"
                        if len(result['preview']) > 20:
                            preview_content += f"... and {len(result['preview']) - 20} more files"
                    else:
                        preview_content = f"Error: {result['message']}"
                    
                    preview_text.delete("1.0", "end")
                    preview_text.insert("1.0", preview_content)
                    
                except Exception as e:
                    preview_text.delete("1.0", "end")
                    preview_text.insert("1.0", f"Preview error: {str(e)}")
            
            def execute_rename():
                try:
                    path = path_entry.get()
                    pattern = pattern_entry.get()
                    file_filter = filter_entry.get()
                    
                    if not path or not pattern:
                        return
                    
                    import tkinter.messagebox as msgbox
                    if not msgbox.askyesno("Confirm Rename", "Execute bulk rename operation?"):
                        return
                    
                    result = self.file_tools.bulk_rename(path, pattern, file_filter)
                    
                    if result['status'] == 'success':
                        msgbox.showinfo("Success", f"Renamed {result['renamed_count']} files")
                        self.log(f"Bulk renamed {result['renamed_count']} files")
                        rename_window.destroy()
                    else:
                        msgbox.showerror("Error", f"Rename failed: {result['message']}")
                        
                except Exception as e:
                    import tkinter.messagebox as msgbox
                    msgbox.showerror("Error", f"Rename error: {str(e)}")
            
            # Buttons
            button_frame = ctk.CTkFrame(rename_window)
            button_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkButton(button_frame, text="Preview", command=preview_rename).pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Execute", command=execute_rename, fg_color="#E74C3C").pack(side="left", padx=5)
            ctk.CTkButton(button_frame, text="Cancel", command=rename_window.destroy).pack(side="right", padx=5)
            
        except Exception as e:
            self.log(f"Error opening bulk rename dialog: {str(e)}")
    
    def analyze_disk_usage(self):
        """Analyze disk usage"""
        def analyze_thread():
            try:
                analysis_path = self.analysis_path_entry.get()
                
                if not analysis_path:
                    self.analysis_results.delete("1.0", "end")
                    self.analysis_results.insert("1.0", "❌ Please specify path to analyze")
                    return
                
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", "📊 Analyzing disk usage...\n")
                
                result = self.file_tools.analyze_disk_usage(analysis_path)
                
                if result['status'] == 'success':
                    analysis = result['analysis']
                    output = f"📊 Disk Usage Analysis:\n\n"
                    output += f"📁 Total directories: {analysis['total_dirs']:,}\n"
                    output += f"📄 Total files: {analysis['total_files']:,}\n"
                    output += f"💾 Total size: {self._format_size(analysis['total_size'])}\n\n"
                    
                    output += f"🔝 Largest directories:\n"
                    for dir_info in analysis['largest_dirs'][:10]:
                        output += f"  📁 {dir_info['path']}: {self._format_size(dir_info['size'])}\n"
                    
                    output += f"\n📈 File type breakdown:\n"
                    for ext, info in list(analysis['file_types'].items())[:10]:
                        output += f"  {ext or 'No extension'}: {info['count']} files, {self._format_size(info['size'])}\n"
                else:
                    output = f"❌ {result.get('message', 'Analysis failed')}
                
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", output)
                
            except Exception as e:
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", f"❌ Analysis error: {str(e)}")
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def find_large_files(self):
        """Find large files"""
        def find_thread():
            try:
                analysis_path = self.analysis_path_entry.get()
                
                if not analysis_path:
                    self.analysis_results.delete("1.0", "end")
                    self.analysis_results.insert("1.0", "❌ Please specify path to analyze")
                    return
                
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", "🔍 Finding large files...\n")
                
                result = self.file_tools.find_large_files(analysis_path, min_size=100*1024*1024)  # 100MB+
                
                if result['status'] == 'success':
                    large_files = result['files']
                    total_size = sum(f['size'] for f in large_files)
                    
                    output = f"🔍 Found {len(large_files)} large files (>100MB):\n"
                    output += f"💾 Total size: {self._format_size(total_size)}\n\n"
                    
                    for file_info in large_files[:20]:
                        output += f"📄 {file_info['path']}\n"
                        output += f"   Size: {self._format_size(file_info['size'])}\n"
                        output += f"   Modified: {file_info['modified']}\n\n"
                    
                    if len(large_files) > 20:
                        output += f"... and {len(large_files) - 20} more files"
                else:
                    output = f"❌ {result.get('message', 'No large files found')}
                
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", output)
                
            except Exception as e:
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", f"❌ Large files search error: {str(e)}")
        
        threading.Thread(target=find_thread, daemon=True).start()
    
    def analyze_file_types(self):
        """Analyze file types distribution"""
        def analyze_thread():
            try:
                analysis_path = self.analysis_path_entry.get()
                
                if not analysis_path:
                    self.analysis_results.delete("1.0", "end")
                    self.analysis_results.insert("1.0", "❌ Please specify path to analyze")
                    return
                
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", "📊 Analyzing file types...\n")
                
                result = self.file_tools.analyze_file_types(analysis_path)
                
                if result['status'] == 'success':
                    file_types = result['file_types']
                    total_files = sum(info['count'] for info in file_types.values())
                    total_size = sum(info['size'] for info in file_types.values())
                    
                    output = f"📊 File Types Analysis:\n\n"
                    output += f"📄 Total files: {total_files:,}\n"
                    output += f"💾 Total size: {self._format_size(total_size)}\n\n"
                    
                    # Sort by size
                    sorted_types = sorted(file_types.items(), 
                                        key=lambda x: x[1]['size'], reverse=True)
                    
                    output += f"🔝 Top file types by size:\n"
                    for ext, info in sorted_types[:15]:
                        percentage = (info['size'] / total_size * 100) if total_size > 0 else 0
                        output += f"  {ext or 'No extension'}: {info['count']:,} files, "
                        output += f"{self._format_size(info['size'])} ({percentage:.1f}%)\n"
                else:
                    output = f"❌ {result.get('message', 'Analysis failed')}
                
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", output)
                
            except Exception as e:
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", f"❌ File types analysis error: {str(e)}")
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        def report_thread():
            try:
                analysis_path = self.analysis_path_entry.get()
                
                if not analysis_path:
                    self.analysis_results.delete("1.0", "end")
                    self.analysis_results.insert("1.0", "❌ Please specify path to analyze")
                    return
                
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", "📊 Generating comprehensive report...\n")
                
                result = self.file_tools.generate_analysis_report(analysis_path)
                
                if result['status'] == 'success':
                    # Show report summary
                    report = result['report']
                    output = f"📊 Analysis Report Generated:\n\n"
                    output += f"📁 Path: {analysis_path}\n"
                    output += f"📄 Total files: {report['total_files']:,}\n"
                    output += f"📁 Total directories: {report['total_dirs']:,}\n"
                    output += f"💾 Total size: {self._format_size(report['total_size'])}\n"
                    output += f"📅 Analysis date: {report['analysis_date']}\n\n"
                    output += f"Report saved to: {result['report_file']}"
                    
                    self.log(f"Analysis report generated: {result['report_file']}")
                else:
                    output = f"❌ {result.get('message', 'Report generation failed')}
                
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", output)
                
            except Exception as e:
                self.analysis_results.delete("1.0", "end")
                self.analysis_results.insert("1.0", f"❌ Report generation error: {str(e)}")
        
        threading.Thread(target=report_thread, daemon=True).start()
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

if __name__ == "__main__":
    app = QuantumDeskGUI()
    app.mainloop()
