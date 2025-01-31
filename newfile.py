import tkinter as tk
from tkinter import messagebox
import threading
import time
import random

# =============== Virtual CPU with Advanced Instructions ===============
class VirtualCPU:
    def __init__(self):
        self.registers = [0] * 8  # 8 General Purpose Registers
        self.pc = 0  # Program Counter
        self.flags = {"Z": 0, "C": 0, "N": 0}  # Zero, Carry, Negative Flags

    def execute_instruction(self, instruction):
        op, *args = instruction.split()
        if op == "LOAD":
            reg, value = int(args[0]), int(args[1])
            self.registers[reg] = value
        elif op == "ADD":
            reg1, reg2 = int(args[0]), int(args[1])
            self.registers[reg1] += self.registers[reg2]
        elif op == "SUB":
            reg1, reg2 = int(args[0]), int(args[1])
            self.registers[reg1] -= self.registers[reg2]
        elif op == "MUL":
            reg1, reg2 = int(args[0]), int(args[1])
            self.registers[reg1] *= self.registers[reg2]
        elif op == "DIV":
            reg1, reg2 = int(args[0]), int(args[1])
            self.registers[reg1] //= self.registers[reg2]
        elif op == "PRINT":
            print("Register Dump:", self.registers)
        elif op == "JUMP":
            self.pc = int(args[0])  # Jump to a different instruction index
        elif op == "RAND":
            reg = int(args[0])
            self.registers[reg] = random.randint(1, 100)

class VirtualMemory:
    def __init__(self, size=1024):  # 1KB RAM
        self.memory = bytearray(size)

    def read(self, addr):
        return self.memory[addr]

    def write(self, addr, value):
        self.memory[addr] = value

# =============== File System with Permissions ===============
class FileSystem:
    def __init__(self):
        self.files = {}
        self.directories = {"root": []}
        self.permissions = {}

    def write_file(self, filename, data, directory="root", permissions="rw"):
        self.files[filename] = data
        self.directories[directory].append(filename)
        self.permissions[filename] = permissions
        print(f"File '{filename}' saved with {permissions} permissions!")

    def read_file(self, filename):
        if "r" in self.permissions.get(filename, ""):
            return self.files.get(filename, "File not found")
        else:
            return "Permission Denied"

    def list_files(self, directory="root"):
        return self.directories.get(directory, [])

# =============== Kernel & System Calls ===============
class Kernel:
    def __init__(self, cpu, memory, filesystem):
        self.cpu = cpu
        self.memory = memory
        self.filesystem = filesystem
        self.apps = []

    def syscall(self, call, *args):
        if call == "PRINT":
            print("Kernel Print:", *args)
        elif call == "READ_MEM":
            addr = args[0]
            return self.memory.read(addr)
        elif call == "WRITE_MEM":
            addr, value = args
            self.memory.write(addr, value)
        elif call == "READ_FILE":
            filename = args[0]
            return self.filesystem.read_file(filename)
        elif call == "WRITE_FILE":
            filename, data = args
            self.filesystem.write_file(filename, data)
        elif call == "LIST_FILES":
            directory = args[0] if args else "root"
            return self.filesystem.list_files(directory)
        elif call == "CREATE_APP":
            app = args[0]
            self.apps.append(app)
            print(f"App '{app}' created.")
        elif call == "RUN_APP":
            app = args[0]
            print(f"Running app: {app}")
            self.run_app(app)
        elif call == "SHUTDOWN":
            print("Shutting down...")
            exit()

    def run_app(self, app):
        # Simulate an app running in its own thread
        def app_thread():
            for i in range(5):
                print(f"{app} is running... Step {i+1}")
                time.sleep(1)
            print(f"{app} finished.")
        
        threading.Thread(target=app_thread).start()

# =============== GUI System (Window Manager with Multitasking) ===============
class GUI:
    def __init__(self, root, kernel):
        self.root = root
        self.kernel = kernel
        self.root.title("Effter 1.0 - Winzernot WebOS Emulator")

        # Main display area
        self.label = tk.Label(root, text="Effter 1.0 Booted!", font=("Arial", 14))
        self.label.pack()

        self.command_entry = tk.Entry(root, width=50)
        self.command_entry.pack()

        self.button_exec = tk.Button(root, text="Execute Command", command=self.execute_command)
        self.button_exec.pack()

        self.output_label = tk.Label(root, text="", font=("Arial", 12))
        self.output_label.pack()

        self.app_buttons_frame = tk.Frame(root)
        self.app_buttons_frame.pack()

    def execute_command(self):
        command = self.command_entry.get()
        output = ""
        try:
            if command == "run":
                self.kernel.syscall("PRINT", "Hello from Effter 1.0 Kernel!")
                output = "Kernel Executed a Command"
            elif command.startswith("write "):
                _, filename, data = command.split(" ", 2)
                self.kernel.syscall("WRITE_FILE", filename, data)
                output = f"File '{filename}' saved!"
            elif command.startswith("read "):
                _, filename = command.split(" ", 1)
                content = self.kernel.syscall("READ_FILE", filename)
                output = f"File Content: {content}"
            elif command == "memory":
                output = f"Memory: {self.kernel.memory.memory[:10]}"  # Display first 10 bytes of RAM
            elif command == "list_files":
                files = self.kernel.syscall("LIST_FILES")
                output = f"Files in root: {files}"
            elif command.startswith("create_app "):
                _, app_name = command.split(" ", 1)
                self.kernel.syscall("CREATE_APP", app_name)
                output = f"App '{app_name}' created."
            elif command.startswith("run_app "):
                _, app_name = command.split(" ", 1)
                self.kernel.syscall("RUN_APP", app_name)
                output = f"Running App: {app_name}"
            elif command == "shutdown":
                self.kernel.syscall("SHUTDOWN")
                output = "Shutting down..."
            else:
                output = "Unknown Command"
        except Exception as e:
            output = f"Error: {str(e)}"
        
        self.output_label.config(text=output)
        self.update_app_buttons()

    def update_app_buttons(self):
        # Update GUI with active apps (if any)
        for widget in self.app_buttons_frame.winfo_children():
            widget.destroy()
        for app in self.kernel.apps:
            app_button = tk.Button(self.app_buttons_frame, text=f"Launch {app}", command=lambda app=app: self.kernel.syscall("RUN_APP", app))
            app_button.pack(side=tk.LEFT)

# =============== Bootloader & Main Program ===============
if __name__ == "__main__":
    cpu = VirtualCPU()
    memory = VirtualMemory()
    filesystem = FileSystem()
    kernel = Kernel(cpu, memory, filesystem)

    root = tk.Tk()
    gui = GUI(root, kernel)
    root.mainloop()