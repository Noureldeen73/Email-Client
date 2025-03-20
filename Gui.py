import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from email_utils import send_email, fetch_latest_email, EmailError


class EmailGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Client")
        self.root.geometry("500x400")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Tabs for Send & Fetch Email
        self.send_tab = ttk.Frame(self.notebook)
        self.fetch_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.send_tab, text="Send Email")
        self.notebook.add(self.fetch_tab, text="Fetch Email")

        self.create_send_tab()
        self.create_fetch_tab()

    def create_send_tab(self):
        """Create the Send Email tab"""
        ttk.Label(self.send_tab, text="Sender Email:").pack(pady=2)
        self.sender_email = ttk.Entry(self.send_tab, width=40)
        self.sender_email.pack(pady=2)

        ttk.Label(self.send_tab, text="Sender Password:").pack(pady=2)
        self.sender_password = ttk.Entry(self.send_tab, width=40, show="*")
        self.sender_password.pack(pady=2)

        ttk.Label(self.send_tab, text="Receiver Email:").pack(pady=2)
        self.receiver_email = ttk.Entry(self.send_tab, width=40)
        self.receiver_email.pack(pady=2)

        ttk.Label(self.send_tab, text="Subject:").pack(pady=2)
        self.subject = ttk.Entry(self.send_tab, width=40)
        self.subject.pack(pady=2)

        ttk.Label(self.send_tab, text="Body:").pack(pady=2)
        self.body = scrolledtext.ScrolledText(self.send_tab, width=40, height=5)
        self.body.pack(pady=2)

        self.send_button = ttk.Button(self.send_tab, text="Send Email", command=self.send_email_thread)
        self.send_button.pack(pady=10)

    def send_email_thread(self):
        """Runs email sending in a separate thread"""
        threading.Thread(target=self.send_email, daemon=True).start()

    def send_email(self):
        """Handles sending the email"""
        sender = self.sender_email.get()
        password = self.sender_password.get()
        receiver = self.receiver_email.get()
        subject = self.subject.get()
        body = self.body.get("1.0", tk.END).strip()

        if not sender or not password or not receiver or not subject or not body:
            messagebox.showwarning("Warning", "All fields must be filled!")
            return

        try:
            send_email(sender, password, receiver, subject, body)
            messagebox.showinfo("Success", "Email sent successfully!")
        except EmailError as e:
            messagebox.showerror("Error", str(e))

    def create_fetch_tab(self):
        """Create the Fetch Email tab"""
        ttk.Label(self.fetch_tab, text="Email Address:").pack(pady=2)
        self.fetch_email_entry = ttk.Entry(self.fetch_tab, width=40)
        self.fetch_email_entry.pack(pady=2)

        ttk.Label(self.fetch_tab, text="Password:").pack(pady=2)
        self.fetch_password = ttk.Entry(self.fetch_tab, width=40, show="*")
        self.fetch_password.pack(pady=2)

        self.fetch_button = ttk.Button(self.fetch_tab, text="Fetch Latest Email", command=self.fetch_email_thread)
        self.fetch_button.pack(pady=10)

        self.email_display = scrolledtext.ScrolledText(self.fetch_tab, wrap="word")
        self.email_display.pack(pady=5, padx=5, expand=True, fill="both")

    def fetch_email_thread(self):
        """Runs email fetching in a separate thread"""
        threading.Thread(target=self.fetch_email, daemon=True).start()

    def fetch_email(self):
        """Handles fetching the latest email"""
        email_address = self.fetch_email_entry.get()
        password = self.fetch_password.get()

        if not email_address or not password:
            messagebox.showwarning("Warning", "Email and password must be provided!")
            return

        try:
            result = fetch_latest_email(email_address, password)
            self.email_display.delete("1.0", tk.END)
            email_content = f"Subject: {result['subject']}\n"
            email_content += f"From: {result['sender']}\n"

            if result["text_body"]:
                email_content += f"\nText Body:\n{result['text_body']}"
            elif result["html_body"]:
                email_content += f"\nHTML Body:\n{result['html_body']}"

            if result["attachments"]:
                email_content += "\n\nAttachments:"
                for attachment in result["attachments"]:
                    email_content += f"\n{attachment['filename']}"

            self.email_display.insert(tk.END, email_content)
        except EmailError as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = EmailGUI(root)
    root.mainloop()
