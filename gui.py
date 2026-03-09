"""
Thoth GUI - A modern GUI for the Thoth chatbot
Keeps all original agent functionality but adds a pleasing GUI interface
"""

import customtkinter as ctk
from tkinter import END
import threading
import queue
import time
import sys
import os

# Import the required components
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent

# ==================== AGENT SETUP (same as agent.py) ====================

# Model
llm = ChatOllama(model="llama3.2")

# Tool
search = DuckDuckGoSearchRun()

@tool
def web_search(query: str) -> str:
    """Search internet for information."""
    return search.run(query)

tools = [web_search]

# Agent
agent = create_agent(
    llm,
    tools,
    system_prompt="""You are a research AI assistant.

Think step by step."""
)

# ==================== GUI APPLICATION ====================

class ThothGUI:
    def __init__(self):
        # Set appearance mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Thoth")
        self.root.geometry("800x350")
        self.root.minsize(600, 400)
        
        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        # Typing animation state
        self.typing_dots = ["", ".", "..", "..."]
        self.typing_index = 0
        self.typing_after_id = None
        
        # Build UI
        self.create_header()
        self.create_chat_area()
        self.create_input_area()
        
        # Start message processing
        self.process_queue()
        
        # Add welcome message
        self.add_message("Thoth", "Hello! I'm Thoth, your AI research assistant. How can I help you today?", is_user=False)
    
    def create_header(self):
        """Create the header with title and status"""
        header_frame = ctk.CTkFrame(self.root, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 0))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Thoth",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="AI Research Assistant",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 10))
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="● Ready",
            font=ctk.CTkFont(size=11),
            text_color="green"
        )
        self.status_label.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        
        # Separator
        separator = ctk.CTkFrame(self.root, height=2, corner_radius=0)
        separator.grid(row=1, column=0, sticky="ew")
    
    def create_chat_area(self):
        """Create the scrollable chat display area"""
        # Chat frame
        self.chat_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.chat_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable text area
        self.chat_text = ctk.CTkTextbox(
            self.chat_frame,
            wrap="word",
            fg_color=("#2B2B2B", "#1A1A1A"),
            border_width=0,
            activate_scrollbars=False
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew")
        self.chat_text.configure(state="disabled")  # Make read-only
        
        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(self.chat_frame, command=self.chat_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_text.configure(yscrollcommand=self.scrollbar.set)
    
    def create_input_area(self):
        """Create the input area with text field and send button"""
        # Input frame
        input_frame = ctk.CTkFrame(self.root, corner_radius=0)
        input_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Text input
        self.input_field = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message here...",
            height=40,
            corner_radius=20
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=10)
        self.input_field.bind("<Return>", lambda event: self.send_message())
        
        # Send button
        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_message,
            width=80,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.send_button.grid(row=0, column=1, sticky="e", padx=(5, 10), pady=10)
    
    def add_message(self, sender, message, is_user, scroll_to_top=False):
        """Add a message to the chat display"""
        self.chat_text.configure(state="normal")
        
        # Color scheme
        if is_user:
            name_color = "#4A90D9"
            align = "right"
        else:
            name_color = "#9B59B6"
            align = "left"
        
        # Insert at the beginning (newest messages at top)
        self.chat_text.insert("1.0", f"\n{sender}\n{message}\n\n", "message")
        
        # Configure tags
        self.chat_text.tag_config("message", foreground="white")
        
        # Scroll to top to show newest message
        self.chat_text.see("1.0")
        
        self.chat_text.configure(state="disabled")
    
    def start_typing_animation(self):
        """Start the typing animation"""
        self.typing_index = (self.typing_index + 1) % 4
        self.status_label.configure(text=f"● Thinking{self.typing_dots[self.typing_index]}")
        self.typing_after_id = self.root.after(300, self.start_typing_animation)
    
    def stop_typing_animation(self):
        """Stop the typing animation"""
        if self.typing_after_id:
            self.root.after_cancel(self.typing_after_id)
            self.typing_after_id = None
        self.status_label.configure(text="● Ready", text_color="green")
    
    def send_message(self):
        """Handle sending a message"""
        message = self.input_field.get().strip()
        if not message:
            return
        
        # Clear input field
        self.input_field.delete(0, END)
        
        # Add user message to chat (at top since newest first)
        self.add_message("You", message, is_user=True)
        
        # Update status and start typing animation
        self.status_label.configure(text="● Thinking.", text_color="orange")
        self.send_button.configure(state="disabled")
        
        # Start typing animation
        self.start_typing_animation()
        
        # Run agent in separate thread
        thread = threading.Thread(target=self.run_agent, args=(message,))
        thread.daemon = True
        thread.start()
    
    def run_agent(self, user_input):
        """Run the agent in a separate thread"""
        try:
            result = agent.invoke({
                "messages": [("user", user_input)]
            })
            
            # Get the last message from the model
            response = ""
            for message in reversed(result["messages"]):
                if hasattr(message, "type") and message.type == "ai" and message.content:
                    response = message.content
                    break
            
            # Put result in queue
            self.message_queue.put(("success", response))
        except Exception as e:
            self.message_queue.put(("error", str(e)))
    
    def process_queue(self):
        """Process messages from the queue"""
        try:
            while True:
                status, content = self.message_queue.get_nowait()
                
                # Stop typing animation first
                self.stop_typing_animation()
                
                if status == "success":
                    self.add_message("Thoth", content, is_user=False, scroll_to_top=True)
                    self.status_label.configure(text="● Ready", text_color="green")
                else:
                    self.add_message("Thoth", f"Error: {content}", is_user=False, scroll_to_top=True)
                    self.status_label.configure(text="● Error", text_color="red")
                
                self.send_button.configure(state="normal")
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue)
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = ThothGUI()
    app.run()


if __name__ == "__main__":
    main()
