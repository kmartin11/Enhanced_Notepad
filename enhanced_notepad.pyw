import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, font
import os
import datetime
import re

class EnhancedNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Untitled - Enhanced Notepad")
        self.root.geometry("900x700")
        self.root.minsize(400, 300)

        # Variables
        self.current_file = None
        self.font_family = "Arial"
        self.font_size = 12
        self.current_font = font.Font(family=self.font_family, size=self.font_size)
        self.word_wrap = True
        self.show_line_numbers = False
        self.theme = "light"
        self.find_index = "1.0"
        self.zoom_level = 100

        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both')

        # Create status bar frame
        self.status_frame = tk.Frame(self.main_frame)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create text frame
        self.text_frame = tk.Frame(self.main_frame)
        self.text_frame.pack(expand=True, fill='both')

        # Create line numbers text widget
        self.line_numbers = tk.Text(self.text_frame, width=4, padx=3, takefocus=0,
                                   border=0, state='disabled', wrap='none')
        
        # Create Text Area with Scrollbar
        self.text_area = scrolledtext.ScrolledText(
            self.text_frame, 
            wrap=tk.WORD if self.word_wrap else tk.NONE, 
            undo=True,
            font=self.current_font,
            insertbackground='black'
        )
        
        # Pack text widgets
        self.text_area.pack(side=tk.RIGHT, expand=True, fill='both')

        # Bind events
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        self.text_area.bind('<Button-1>', self.on_text_change)
        self.text_area.bind('<Control-f>', lambda e: self.show_find_dialog())
        self.text_area.bind('<Control-h>', lambda e: self.show_replace_dialog())
        self.text_area.bind('<Control-g>', lambda e: self.show_goto_line_dialog())
        self.text_area.bind('<Control-plus>', lambda e: self.zoom_in())
        self.text_area.bind('<Control-minus>', lambda e: self.zoom_out())
        self.text_area.bind('<Control-0>', lambda e: self.reset_zoom())

        # Create status bar elements
        self.status_bar = tk.Label(self.status_frame, text="Line: 1, Column: 1", 
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.zoom_label = tk.Label(self.status_frame, text="100%", relief=tk.SUNKEN)
        self.zoom_label.pack(side=tk.RIGHT)

        # Create Menu Bar
        self.create_menu()

        # Initialize
        self.update_line_numbers()
        self.update_status_bar()
        self.apply_theme()

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Recent Files", command=self.show_recent_files)
        file_menu.add_separator()
        file_menu.add_command(label="Print...", command=self.print_file, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)

        # Edit Menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.show_find_dialog, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.show_replace_dialog, accelerator="Ctrl+H")
        edit_menu.add_command(label="Go to Line...", command=self.show_goto_line_dialog, accelerator="Ctrl+G")
        edit_menu.add_separator()
        edit_menu.add_command(label="Insert Date/Time", command=self.insert_datetime)

        # Format Menu
        format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_checkbutton(label="Word Wrap", command=self.toggle_word_wrap)
        format_menu.add_separator()
        format_menu.add_command(label="Font...", command=self.choose_font)
        format_menu.add_separator()
        format_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        format_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        format_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")

        # View Menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Line Numbers", command=self.toggle_line_numbers)
        view_menu.add_separator()
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Light", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Dark", command=lambda: self.change_theme("dark"))

        # Tools Menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Word Count", command=self.show_word_count)
        tools_menu.add_command(label="Character Count", command=self.show_char_count)
        tools_menu.add_separator()
        tools_menu.add_command(label="Convert to Uppercase", command=self.to_uppercase)
        tools_menu.add_command(label="Convert to Lowercase", command=self.to_lowercase)
        tools_menu.add_command(label="Title Case", command=self.to_title_case)

        # Help Menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Enhanced Notepad", command=self.show_about)

        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-p>', lambda e: self.print_file())
        self.root.bind('<Control-a>', lambda e: self.select_all())

    def on_text_change(self, event=None):
        self.update_line_numbers()
        self.update_status_bar()

    def update_line_numbers(self):
        if not self.show_line_numbers:
            return
            
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        
        content = self.text_area.get('1.0', 'end-1c')
        lines = content.split('\n')
        
        for i in range(len(lines)):
            self.line_numbers.insert('end', f'{i+1}\n')
        
        self.line_numbers.config(state='disabled')

    def update_status_bar(self):
        cursor_pos = self.text_area.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.status_bar.config(text=f"Line: {line}, Column: {int(col)+1}")

    def new_file(self):
        if self.check_unsaved_changes():
            self.text_area.delete(1.0, tk.END)
            self.root.title("Untitled - Enhanced Notepad")
            self.current_file = None

    def open_file(self):
        if self.check_unsaved_changes():
            filepath = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text Documents", "*.txt"),
                    ("Python Files", "*.py"),
                    ("All Files", "*.*")
                ]
            )
            if filepath:
                try:
                    with open(filepath, "r", encoding='utf-8') as file:
                        content = file.read()
                        self.text_area.delete(1.0, tk.END)
                        self.text_area.insert(1.0, content)
                    
                    self.current_file = filepath
                    self.root.title(f"{os.path.basename(filepath)} - Enhanced Notepad")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END + '-1c')
                with open(self.current_file, "w", encoding='utf-8') as file:
                    file.write(content)
                self.root.title(f"{os.path.basename(self.current_file)} - Enhanced Notepad")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text Documents", "*.txt"),
                ("Python Files", "*.py"),
                ("All Files", "*.*")
            ]
        )
        if filepath:
            try:
                content = self.text_area.get(1.0, tk.END + '-1c')
                with open(filepath, "w", encoding='utf-8') as file:
                    file.write(content)
                
                self.current_file = filepath
                self.root.title(f"{os.path.basename(filepath)} - Enhanced Notepad")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def check_unsaved_changes(self):
        # Simple check - in a real app, you'd track if content has changed
        return True

    def print_file(self):
        messagebox.showinfo("Print", "Print functionality would be implemented here.\nYou can copy the text and print from another application.")

    def show_recent_files(self):
        messagebox.showinfo("Recent Files", "Recent files functionality would be implemented here.")

    def exit_app(self):
        if self.check_unsaved_changes():
            self.root.quit()

    def cut_text(self):
        try:
            self.text_area.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def copy_text(self):
        try:
            self.text_area.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def paste_text(self):
        try:
            self.text_area.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)

    def show_find_dialog(self):
        search_term = simpledialog.askstring("Find", "Enter text to find:")
        if search_term:
            self.find_text(search_term)

    def find_text(self, search_term):
        self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
        
        start_pos = self.text_area.search(search_term, self.find_index, tk.END)
        if start_pos:
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.text_area.tag_add(tk.SEL, start_pos, end_pos)
            self.text_area.see(start_pos)
            self.text_area.mark_set(tk.INSERT, end_pos)
            self.find_index = end_pos
        else:
            messagebox.showinfo("Find", "Text not found")
            self.find_index = "1.0"

    def show_replace_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Replace")
        dialog.geometry("400x150")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Find:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        find_entry = tk.Entry(dialog, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Replace with:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        replace_entry = tk.Entry(dialog, width=30)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)

        button_frame = tk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Replace All", 
                 command=lambda: self.replace_all(find_entry.get(), replace_entry.get(), dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def replace_all(self, find_text, replace_text, dialog):
        content = self.text_area.get("1.0", tk.END)
        new_content = content.replace(find_text, replace_text)
        
        if content != new_content:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", new_content)
            count = content.count(find_text)
            messagebox.showinfo("Replace", f"Replaced {count} occurrences")
        else:
            messagebox.showinfo("Replace", "No occurrences found")
        
        dialog.destroy()

    def show_goto_line_dialog(self):
        line_num = simpledialog.askinteger("Go to Line", "Enter line number:")
        if line_num:
            self.text_area.mark_set(tk.INSERT, f"{line_num}.0")
            self.text_area.see(tk.INSERT)

    def insert_datetime(self):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.text_area.insert(tk.INSERT, current_time)

    def toggle_word_wrap(self):
        self.word_wrap = not self.word_wrap
        self.text_area.config(wrap=tk.WORD if self.word_wrap else tk.NONE)

    def toggle_line_numbers(self):
        self.show_line_numbers = not self.show_line_numbers
        if self.show_line_numbers:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
            self.update_line_numbers()
        else:
            self.line_numbers.pack_forget()

    def choose_font(self):
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("Font")
        font_dialog.geometry("300x200")
        
        tk.Label(font_dialog, text="Font Family:").pack(pady=5)
        font_var = tk.StringVar(value=self.font_family)
        font_listbox = tk.Listbox(font_dialog, height=6)
        font_listbox.pack(pady=5)
        
        families = list(font.families())
        for family in sorted(families):
            font_listbox.insert(tk.END, family)
        
        tk.Label(font_dialog, text="Size:").pack(pady=5)
        size_var = tk.StringVar(value=str(self.font_size))
        size_entry = tk.Entry(font_dialog, textvariable=size_var, width=10)
        size_entry.pack(pady=5)
        
        def apply_font():
            try:
                selected_font = font_listbox.get(font_listbox.curselection())
                size = int(size_var.get())
                self.font_family = selected_font
                self.font_size = size
                self.current_font.config(family=selected_font, size=size)
                self.text_area.config(font=self.current_font)
                font_dialog.destroy()
            except:
                messagebox.showerror("Error", "Invalid font selection")
        
        tk.Button(font_dialog, text="OK", command=apply_font).pack(pady=10)

    def zoom_in(self):
        self.zoom_level = min(300, self.zoom_level + 10)
        new_size = max(8, int(self.font_size * self.zoom_level / 100))
        self.current_font.config(size=new_size)
        self.text_area.config(font=self.current_font)
        self.zoom_label.config(text=f"{self.zoom_level}%")

    def zoom_out(self):
        self.zoom_level = max(50, self.zoom_level - 10)
        new_size = max(8, int(self.font_size * self.zoom_level / 100))
        self.current_font.config(size=new_size)
        self.text_area.config(font=self.current_font)
        self.zoom_label.config(text=f"{self.zoom_level}%")

    def reset_zoom(self):
        self.zoom_level = 100
        self.current_font.config(size=self.font_size)
        self.text_area.config(font=self.current_font)
        self.zoom_label.config(text="100%")

    def change_theme(self, theme):
        self.theme = theme
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "dark":
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            select_bg = "#404040"
            insert_bg = "#ffffff"
        else:  # light theme
            bg_color = "#ffffff"
            fg_color = "#000000"
            select_bg = "#316AC5"
            insert_bg = "#000000"

        self.text_area.config(
            bg=bg_color,
            fg=fg_color,
            selectbackground=select_bg,
            insertbackground=insert_bg
        )
        
        if self.show_line_numbers:
            self.line_numbers.config(bg=bg_color, fg=fg_color)

    def show_word_count(self):
        content = self.text_area.get("1.0", tk.END + '-1c')
        words = len(content.split())
        messagebox.showinfo("Word Count", f"Word count: {words}")

    def show_char_count(self):
        content = self.text_area.get("1.0", tk.END + '-1c')
        chars = len(content)
        chars_no_spaces = len(content.replace(' ', '').replace('\n', '').replace('\t', ''))
        messagebox.showinfo("Character Count", 
                          f"Characters: {chars}\nCharacters (no spaces): {chars_no_spaces}")

    def to_uppercase(self):
        try:
            selected_text = self.text_area.selection_get()
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, selected_text.upper())
        except tk.TclError:
            messagebox.showinfo("Info", "Please select text first")

    def to_lowercase(self):
        try:
            selected_text = self.text_area.selection_get()
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, selected_text.lower())
        except tk.TclError:
            messagebox.showinfo("Info", "Please select text first")

    def to_title_case(self):
        try:
            selected_text = self.text_area.selection_get()
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, selected_text.title())
        except tk.TclError:
            messagebox.showinfo("Info", "Please select text first")

    def show_about(self):
        about_text = """Enhanced Notepad v2.0

A powerful text editor with advanced features including:
• Find & Replace functionality
• Line numbers and go-to-line
• Word/character counting
• Text case conversion
• Zoom controls
• Dark/Light themes
• Multiple file format support
• Status bar with cursor position

Created with Python and Tkinter"""
        
        messagebox.showinfo("About Enhanced Notepad", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedNotepad(root)
    root.mainloop()