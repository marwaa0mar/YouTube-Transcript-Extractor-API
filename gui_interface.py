import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading

class YouTubeTranscriptGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Transcript Extractor")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # API URL (change this to your ngrok URL when testing)
        self.api_url = "http://127.0.0.1:8000"
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="YouTube Transcript Extractor", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Video ID input
        ttk.Label(main_frame, text="YouTube Video ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.video_id_var = tk.StringVar()
        self.video_id_entry = ttk.Entry(main_frame, textvariable=self.video_id_var, width=30)
        self.video_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # Extract button
        self.extract_btn = ttk.Button(main_frame, text="Extract Transcript", 
                                     command=self.extract_transcript)
        self.extract_btn.grid(row=1, column=2, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Transcript with Timestamps", padding="5")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Transcript display
        self.transcript_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                        height=20, font=('Consolas', 10))
        self.transcript_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Enter a YouTube Video ID and click Extract")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Bind Enter key to extract button
        self.video_id_entry.bind('<Return>', lambda e: self.extract_transcript())
        
        # Focus on entry
        self.video_id_entry.focus()
    
    def extract_transcript(self):
        video_id = self.video_id_var.get().strip()
        
        if not video_id:
            messagebox.showerror("Error", "Please enter a YouTube Video ID")
            return
        
        if len(video_id) != 11:
            messagebox.showerror("Error", "YouTube Video ID must be exactly 11 characters")
            return
        
        # Start extraction in a separate thread
        self.extract_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set("Extracting transcript...")
        self.transcript_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self._extract_thread, args=(video_id,))
        thread.daemon = True
        thread.start()
    
    def _extract_thread(self, video_id):
        try:
            # Make API request
            url = f"{self.api_url}/video-info/{video_id}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Update UI in main thread
                self.root.after(0, self._display_results, data)
            else:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('detail', 'Unknown error')}"
                except:
                    pass
                self.root.after(0, lambda: self._show_error(error_msg))
                
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self._show_error(f"Network Error: {str(e)}"))
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Error: {str(e)}"))
        finally:
            self.root.after(0, self._extraction_finished)
    
    def _display_results(self, data):
        self.transcript_text.delete(1.0, tk.END)
        
        # Display video info
        video_info = f"Video ID: {data.get('video_id', 'N/A')}\n"
        video_info += f"Title: {data.get('title', 'N/A')}\n"
        video_info += f"Duration: {data.get('duration', 'N/A')} seconds\n"
        video_info += f"Uploader: {data.get('uploader', 'N/A')}\n"
        video_info += f"Caption Type: {data.get('caption_type', 'None')}\n"
        video_info += f"Success: {data.get('success', False)}\n"
        video_info += "=" * 80 + "\n\n"
        
        self.transcript_text.insert(tk.END, video_info)
        
        # Display captions with timestamps
        captions = data.get('captions', [])
        if captions:
            for i, caption in enumerate(captions, 1):
                start_time = caption.get('start', '00:00')
                end_time = caption.get('end', '00:00')
                text = caption.get('text', '')
                
                caption_line = f"[{i:3d}] {start_time} - {end_time}: {text}\n\n"
                self.transcript_text.insert(tk.END, caption_line)
            
            self.status_var.set(f"Success! Found {len(captions)} caption segments")
        else:
            self.transcript_text.insert(tk.END, "No captions found for this video.\n")
            self.transcript_text.insert(tk.END, f"Message: {data.get('message', 'No message')}\n")
            self.status_var.set("No captions available")
    
    def _show_error(self, error_msg):
        messagebox.showerror("Error", error_msg)
        self.status_var.set("Error occurred")
    
    def _extraction_finished(self):
        self.extract_btn.config(state='normal')
        self.progress.stop()

def main():
    root = tk.Tk()
    app = YouTubeTranscriptGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
