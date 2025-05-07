import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import processor
import pickle
import os

class DiffCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptek File Diff & Compression Tool")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        self.fileA = ""
        self.fileB = ""
        self.latest_bin_file = None
        self.latest_tree_file = None

        title = tk.Label(root, text="Cryptek Diff & Compression", font=("Helvetica", 20, "bold"), bg="#f0f0f0", fg="#333")
        title.pack(pady=10)

        file_frame = tk.Frame(root, bg="#f0f0f0")
        file_frame.pack(pady=10)

        self.fileA_label = tk.Label(file_frame, text="File A: Not selected", bg="#f0f0f0", fg="#555", width=80, anchor="w")
        self.fileA_label.grid(row=0, column=0, padx=10, pady=5)
        tk.Button(file_frame, text="Browse File A", command=self.select_fileA).grid(row=0, column=1, padx=5)

        self.fileB_label = tk.Label(file_frame, text="File B: Not selected", bg="#f0f0f0", fg="#555", width=80, anchor="w")
        self.fileB_label.grid(row=1, column=0, padx=10, pady=5)
        tk.Button(file_frame, text="Browse File B", command=self.select_fileB).grid(row=1, column=1, padx=5)

        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Run Diff & Compress", command=self.run_process, bg="#007acc", fg="white", width=20).pack(pady=2)
        tk.Button(button_frame, text="Export .bin to USB", command=self.export_bin, bg="#5cb85c", fg="white", width=20).pack(pady=2)
        tk.Button(button_frame, text="Load & Decompress .bin", command=self.load_bin_file, bg="#f0ad4e", fg="white", width=20).pack(pady=2)
        tk.Button(button_frame, text="Clear Output", command=self.clear_output, bg="#d9534f", fg="white", width=20).pack(pady=5)

        self.output = scrolledtext.ScrolledText(root, width=110, height=30, font=("Courier", 10), bg="white", fg="#111")
        self.output.pack(pady=10)

    def select_fileA(self):
        self.fileA = filedialog.askopenfilename()
        self.fileA_label.config(text=f"File A: {self.fileA}")

    def select_fileB(self):
        self.fileB = filedialog.askopenfilename()
        self.fileB_label.config(text=f"File B: {self.fileB}")

    def clear_output(self):
        self.output.delete("1.0", tk.END)

    def run_process(self):
        if not self.fileA or not self.fileB:
            messagebox.showerror("Error", "Please select both files.")
            return

        diff, bits, status, stats = processor.process_files(self.fileA, self.fileB)
        self.latest_bin_file = stats['bin_file']
        self.latest_tree_file = stats['tree_file']

        self.output.insert(tk.END, "\n=== Difference ===\n", "section")
        self.output.insert(tk.END, diff[:1000] + '\n...\n' if len(diff) > 1000 else diff)

        self.output.insert(tk.END, "\n=== Encoded Bits ===\n", "section")
        self.output.insert(tk.END, bits[:500] + '\n...\n' if len(bits) > 500 else bits)

        self.output.insert(tk.END, f"\nSaved: {stats['bin_file']}, {stats['tree_file']}, {stats['txt_file']}\n")

        self.output.insert(tk.END, "\n=== Decompression ===\n", "section")
        self.output.insert(tk.END, "✅ Success\n" if status else "❌ Failed\n", "success" if status else "fail")

        self.output.insert(tk.END, "\n=== File Size Stats ===\n", "section")
        self.output.insert(tk.END, f"File A Size: {stats['fileA_size']} bytes\n")
        self.output.insert(tk.END, f"File B Size: {stats['fileB_size']} bytes\n")
        self.output.insert(tk.END, f"Diff Size: {stats['diff_size']} bytes\n")
        self.output.insert(tk.END, f"Compressed Size: {stats['compressed_size']} bytes\n")
        self.output.insert(tk.END, f"Compression Ratio: {stats['compression_ratio']:.2f}%\n")
        self.output.insert(tk.END, "-"*100 + "\n")

        self.output.tag_config("section", font=("Helvetica", 12, "bold"), foreground="#007acc")
        self.output.tag_config("success", foreground="green", font=("Helvetica", 10, "bold"))
        self.output.tag_config("fail", foreground="red", font=("Helvetica", 10, "bold"))

    def export_bin(self):
        if not self.latest_bin_file:
            messagebox.showwarning("No .bin file", "Run compression first.")
            return
        dest_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary Files", "*.bin")])
        if dest_path:
            try:
                with open(self.latest_bin_file, "rb") as src:
                    data = src.read()
                with open(dest_path, "wb") as dst:
                    dst.write(data)
                messagebox.showinfo("Success", f"Exported to {dest_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def load_bin_file(self):
        bin_path = filedialog.askopenfilename(title="Select .bin File", filetypes=[("Binary Files", "*.bin")])
        if not bin_path:
            return
        tree_path = filedialog.askopenfilename(title="Select .tree File", filetypes=[("Pickle Files", "*.pkl")])
        if not tree_path:
            return
        try:
            # Load compressed bits
            with open(bin_path, "rb") as f_bin:
                byte_data = f_bin.read()
            bit_string = ''.join(f"{byte:08b}" for byte in byte_data)

            # Load tree
            with open(tree_path, "rb") as f_tree:
                tree = pickle.load(f_tree)

            decoded_text = processor.huffman_decode(bit_string, tree)

            self.output.insert(tk.END, f"\n=== Loaded .bin File: {bin_path} ===\n", "section")
            self.output.insert(tk.END, f"Decoded Original Diff:\n{decoded_text[:1000]}\n...\n" if len(decoded_text) > 1000 else decoded_text)
            self.output.insert(tk.END, "-"*100 + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load/decode: {e}")

# Launch GUI
root = tk.Tk()
app = DiffCompressorGUI(root)
root.mainloop()
