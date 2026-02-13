import tkinter as tk
import pyperclip as pc
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import Text, StringVar
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import pygame
import time
import json
from datetime import datetime
import speech_recognition as sr


root = tk.Tk()
root.title('Language translator')
root.geometry('1200x700')
root.minsize(800, 600)
root.configure(bg='#f5f5f5')

# Global variables
translated_text = ""
translation_history = []

COLORS = {
    'bg': '#f5f5f5',
    'card': '#ffffff',
    'primary': '#6366f1',
    'primary_hover': '#4f46e5',
    'text_dark': '#1f2937',
    'text_light': '#6b7280',
    'text_lighter': '#9ca3af',
    'border': '#e5e7eb',
    'border_hover': '#6366f1',      # Indigo border on hover
    'border_active': '#6366f1',     # Indigo border when popup open
    'success': '#10b981',
    'danger': '#ef4444',
    'arrow': '#9ca3af',
    'arrow_hover': '#6b7280',
    'popup_bg': '#ffffff',
    'popup_hover': '#f0f0ff',
    'popup_selected': '#eef2ff',
    'popup_shadow': '#d1d5db',
}

LANGUAGES_SOURCE = [
    'Auto Detect',
    'Afrikaans', 'Albanian', 'Arabic', 'Armenian', 'Azerbaijani',
    'Basque', 'Belarusian', 'Bengali', 'Bosnian', 'Bulgarian',
    'Catalan', 'Chinese', 'Croatian', 'Czech', 'Danish',
    'Dutch', 'English', 'Estonian', 'Filipino', 'Finnish',
    'French', 'Galician', 'Georgian', 'German', 'Greek',
    'Gujarati', 'Haitian Creole', 'Hebrew', 'Hindi', 'Hungarian',
    'Icelandic', 'Indonesian', 'Irish', 'Italian', 'Japanese',
    'Kannada', 'Korean', 'Latvian', 'Lithuanian', 'Macedonian',
    'Malay', 'Maltese', 'Marathi', 'Norwegian', 'Persian',
    'Polish', 'Portuguese', 'Punjabi', 'Romanian', 'Russian',
    'Serbian', 'Slovak', 'Slovenian', 'Spanish', 'Swahili',
    'Swedish', 'Tamil', 'Telugu', 'Thai', 'Turkish',
    'Ukrainian', 'Urdu', 'Vietnamese', 'Welsh'
]

LANGUAGES_TARGET = [
    'Afrikaans', 'Albanian', 'Arabic', 'Armenian', 'Azerbaijani',
    'Basque', 'Belarusian', 'Bengali', 'Bosnian', 'Bulgarian',
    'Catalan', 'Chinese', 'Croatian', 'Czech', 'Danish',
    'Dutch', 'English', 'Estonian', 'Filipino', 'Finnish',
    'French', 'Galician', 'Georgian', 'German', 'Greek',
    'Gujarati', 'Haitian Creole', 'Hebrew', 'Hindi', 'Hungarian',
    'Icelandic', 'Indonesian', 'Irish', 'Italian', 'Japanese',
    'Kannada', 'Korean', 'Latvian', 'Lithuanian', 'Macedonian',
    'Malay', 'Maltese', 'Marathi', 'Norwegian', 'Persian',
    'Polish', 'Portuguese', 'Punjabi', 'Romanian', 'Russian',
    'Serbian', 'Slovak', 'Slovenian', 'Spanish', 'Swahili',
    'Swedish', 'Tamil', 'Telugu', 'Thai', 'Turkish',
    'Ukrainian', 'Urdu', 'Vietnamese', 'Welsh'
]

# StringVars
a = StringVar(value='Auto Detect')
l = StringVar(value='Select Language')


# ===== FLOATING POPUP CLASS =====
class FloatingLangPopup:
    def __init__(self, root, string_var, languages, btn_frame_ref):
        self.root = root
        self.var = string_var
        self.languages = languages
        self.btn_frame_ref = btn_frame_ref  # The button frame to highlight
        self.popup = None
        self.is_open = False
        self.search_var = StringVar()

    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()

    def open(self):
        # Close other popups first
        if source_popup.is_open and self != source_popup:
            source_popup.close()
        if target_popup.is_open and self != target_popup:
            target_popup.close()

        self.is_open = True
        # Highlight the button border
        self.btn_frame_ref.config(highlightbackground=COLORS['border_active'],
                                  highlightthickness=2)

        # Get position of the button frame relative to root
        self.root.update_idletasks()
        bx = self.btn_frame_ref.winfo_rootx() - self.root.winfo_rootx()
        by = self.btn_frame_ref.winfo_rooty() - self.root.winfo_rooty()
        bw = self.btn_frame_ref.winfo_width()

        # Create the floating popup frame ON root (so it overlaps everything)
        # Create the floating popup frame ON root (so it overlaps everything)
        # Right-align with button and extend left
        popup_width = 500
        popup_x = bx + bw - popup_width  # Right edge of button minus popup width

        self.popup = Frame(self.root, bg=COLORS['popup_bg'], width=popup_width, height=420,
                        highlightbackground=COLORS['popup_shadow'], highlightthickness=1)
        self.popup.place(x=popup_x, y=by + 38, width=popup_width, height=420)
        self.popup.lift()  # Bring to front
        self.popup.pack_propagate(False)

        # Search box frame
        search_outer = Frame(self.popup, bg=COLORS['popup_bg'])
        search_outer.pack(fill=X, padx=12, pady=(12, 8))

        search_box = Frame(search_outer, bg=COLORS['popup_bg'],
                          highlightbackground=COLORS['border'], highlightthickness=1)
        search_box.pack(fill=X)

        search_icon = Label(search_box, text="🔍", font=('Arial', 11),
                           bg=COLORS['popup_bg'], fg=COLORS['text_lighter'])
        search_icon.pack(side=LEFT, padx=(8, 2), pady=7)

        self.search_entry = Entry(search_box, textvariable=self.search_var,
                                 font=('Arial', 11), bg=COLORS['popup_bg'],
                                 fg=COLORS['text_dark'], insertbackground=COLORS['primary'],
                                 relief=FLAT, bd=0)
        self.search_entry.pack(fill=X, pady=7, padx=(0, 8))
        self.search_entry.insert(0, "Search...")
        self.search_entry.config(fg=COLORS['text_lighter'])

        def on_focus(e):
            if self.search_entry.get() == "Search...":
                self.search_entry.delete(0, END)
                self.search_entry.config(fg=COLORS['text_dark'])

        def on_blur(e):
            if self.search_entry.get() == "":
                self.search_entry.insert(0, "Search...")
                self.search_entry.config(fg=COLORS['text_lighter'])

        self.search_entry.bind('<FocusIn>', on_focus)
        self.search_entry.bind('<FocusOut>', on_blur)
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_languages())
        self.search_entry.focus_set()

        # Scrollable area
        scroll_container = Frame(self.popup, bg=COLORS['popup_bg'])
        scroll_container.pack(fill=BOTH, expand=True, padx=(12, 0), pady=(0, 12))

        self.canvas = Canvas(scroll_container, bg=COLORS['popup_bg'], highlightthickness=0)
        scrollbar = Scrollbar(scroll_container, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.grid_frame = Frame(self.canvas, bg=COLORS['popup_bg'])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_frame, anchor='nw')

        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(
            self.canvas_window, width=e.width))
        self.grid_frame.bind('<Configure>', lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox('all')))

        # Mouse wheel
        self.canvas.bind('<MouseWheel>', lambda e: self.canvas.yview_scroll(
            int(-1 * (e.delta / 120)), 'units'))
        self.grid_frame.bind('<MouseWheel>', lambda e: self.canvas.yview_scroll(
            int(-1 * (e.delta / 120)), 'units'))

        self.build_grid(self.languages)

        # Bind click outside to close
        self.root.bind('<Button-1>', self._check_outside_click)

    def _check_outside_click(self, event):
        if not self.is_open or self.popup is None:
            return
        # Check if click is inside popup
        px = self.popup.winfo_x()
        py = self.popup.winfo_y()
        pw = self.popup.winfo_width()
        ph = self.popup.winfo_height()
        if not (px <= event.x_root - self.root.winfo_x() <= px + pw and
                py <= event.y_root - self.root.winfo_y() <= py + ph):
            # Also check if click is on the button itself (toggle handles that)
            bx = self.btn_frame_ref.winfo_x()
            by = self.btn_frame_ref.winfo_y()
            bw = self.btn_frame_ref.winfo_width()
            bh = self.btn_frame_ref.winfo_height()
            click_x = event.x_root - self.root.winfo_x()
            click_y = event.y_root - self.root.winfo_y()
            if not (bx <= click_x <= bx + bw and by <= click_y <= by + bh):
                self.close()

    def close(self):
        self.is_open = False
        # Reset button border
        self.btn_frame_ref.config(highlightbackground=COLORS['border'],
                                  highlightthickness=1)
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None
        self.root.unbind('<Button-1>')
        self.search_var.set('')

    def build_grid(self, languages):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        current = self.var.get()
        cols = 3

        for i, lang in enumerate(languages):
            row = i // cols
            col = i % cols
            is_selected = (lang == current)

            btn_bg = COLORS['popup_selected'] if is_selected else COLORS['popup_bg']

            btn_frame = Frame(self.grid_frame, bg=btn_bg)
            btn_frame.grid(row=row, column=col, sticky='ew', padx=(0, 2), pady=1)
            self.grid_frame.grid_columnconfigure(col, weight=1)

            btn = Button(btn_frame, text=lang, font=('Arial', 10),
                        bg=btn_bg,
                        fg=COLORS['primary'] if is_selected else COLORS['text_dark'],
                        relief=FLAT, bd=0, cursor='hand2', anchor='w',
                        padx=10, pady=5,
                        activebackground=COLORS['popup_hover'],
                        command=lambda l=lang: self.select_language(l))
            btn.pack(side=LEFT, fill=X, expand=True)

            if is_selected:
                check = Label(btn_frame, text="✓", font=('Arial', 10, 'bold'),
                            bg=btn_bg, fg=COLORS['primary'])
                check.pack(side=RIGHT, padx=(0, 8))

            # Hover
            def on_enter(e, f=btn_frame, s=is_selected):
                c = COLORS['popup_selected'] if s else COLORS['popup_hover']
                f.config(bg=c)
                for w in f.winfo_children():
                    w.config(bg=c)

            def on_leave(e, f=btn_frame, s=is_selected):
                c = COLORS['popup_selected'] if s else COLORS['popup_bg']
                f.config(bg=c)
                for w in f.winfo_children():
                    w.config(bg=c)

            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            # Propagate hover to frame children too
            for child in btn_frame.winfo_children():
                child.bind('<Enter>', on_enter)
                child.bind('<Leave>', on_leave)

    def filter_languages(self):
        query = self.search_entry.get().lower()
        if query == "search...":
            query = ""
        filtered = [lang for lang in self.languages if query in lang.lower()]
        self.build_grid(filtered)
        self.canvas.yview_moveto(0)

    def select_language(self, lang):
        self.var.set(lang)
        self.close()


# ===== HISTORY =====
def load_history():
    global translation_history
    try:
        if os.path.exists('translation_history.json'):
            with open('translation_history.json', 'r', encoding='utf-8') as f:
                translation_history = json.load(f)
    except:
        translation_history = []

def save_history():
    try:
        with open('translation_history.json', 'w', encoding='utf-8') as f:
            json.dump(translation_history[-50:], f, ensure_ascii=False, indent=2)
    except:
        pass

def add_to_history(source_text, translated_text, source_lang, target_lang):
    translation_history.append({
        'source': source_text,
        'translation': translated_text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_history()


# ===== CORE FUNCTIONS =====
def translate(event=None):
    global translated_text
    input_text = t1.get("1.0", "end-1c")
    target_lang = l.get()

    if input_text.strip() == "":
        messagebox.showerror('Language Translator', 'Please enter text to translate')
        return
    if target_lang == 'Select Language':
        messagebox.showerror('Language Translator', 'Please select a target language')
        return

    t2.delete(1.0, 'end')
    detected_lang_label.config(text="Detecting...")

    lang_codes = {
        'Afrikaans': 'af', 'Albanian': 'sq', 'Arabic': 'ar', 'Armenian': 'hy',
        'Azerbaijani': 'az', 'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn',
        'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca', 'Chinese': 'zh-CN',
        'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl',
        'English': 'en', 'Estonian': 'et', 'Filipino': 'tl', 'Finnish': 'fi',
        'French': 'fr', 'Galician': 'gl', 'Georgian': 'ka', 'German': 'de',
        'Greek': 'el', 'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hebrew': 'he',
        'Hindi': 'hi', 'Hungarian': 'hu', 'Icelandic': 'is', 'Indonesian': 'id',
        'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja', 'Kannada': 'kn',
        'Korean': 'ko', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Macedonian': 'mk',
        'Malay': 'ms', 'Maltese': 'mt', 'Marathi': 'mr', 'Norwegian': 'no',
        'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt', 'Punjabi': 'pa',
        'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr', 'Slovak': 'sk',
        'Slovenian': 'sl', 'Spanish': 'es', 'Swahili': 'sw', 'Swedish': 'sv',
        'Tamil': 'ta', 'Telugu': 'te', 'Thai': 'th', 'Turkish': 'tr',
        'Ukrainian': 'uk', 'Urdu': 'ur', 'Vietnamese': 'vi', 'Welsh': 'cy'
    }

    try:
        translator = GoogleTranslator(source='auto', target=lang_codes[target_lang])
        translated_text = translator.translate(input_text)
        detected_lang_label.config(text="Translated")
        t2.delete(1.0, 'end')
        t2.insert('end', translated_text)
        add_to_history(input_text, translated_text, a.get(), target_lang)
        update_char_count()
    except Exception as e:
        messagebox.showerror('Error', f'Translation failed: {str(e)}')
        detected_lang_label.config(text="")


def clear(event=None):
    t1.delete(1.0, 'end')
    t2.delete(1.0, 'end')
    char_count_label.config(text="0 / 5000")
    detected_lang_label.config(text="")

def copy(event=None):
    text = t2.get("1.0", "end-1c")
    if text.strip():
        pc.copy(text)
        copy_btn.config(text="✓ Copied")
        root.after(1500, lambda: copy_btn.config(text="Copy"))
    else:
        messagebox.showwarning('Warning', 'Nothing to copy!')

# Audio playback control functions
audio_paused = False

def play_audio():
    """Play or resume audio"""
    global audio_paused
    
    # Check if there's translation text
    text = t2.get("1.0", "end-1c")
    if not text or text.strip() == '':
        messagebox.showerror('Error', 'No translation to read aloud!')
        return
    
    try:
        if audio_paused:
            pygame.mixer.music.unpause()
            audio_paused = False
            play_btn.config(fg=COLORS['text_lighter'], state=DISABLED)
            pause_btn.config(fg=COLORS['text_light'], state=NORMAL)
        else:
            # Start playing from beginning
            if os.path.exists("translation.mp3"):
                pygame.mixer.init()
                pygame.mixer.music.load("translation.mp3")
                pygame.mixer.music.play()
                play_btn.config(fg=COLORS['text_lighter'], state=DISABLED)
                pause_btn.config(fg=COLORS['text_light'], state=NORMAL)
                
                # Check when audio finishes
                def check_audio_finished():
                    if pygame.mixer.music.get_busy():
                        root.after(100, check_audio_finished)
                    else:
                        # Audio finished, reset buttons
                        play_btn.config(fg=COLORS['text_light'], state=NORMAL)
                        pause_btn.config(fg=COLORS['text_lighter'], state=DISABLED)
                
                check_audio_finished()
            else:
                messagebox.showerror('Error', 'No audio file found. Please click the speaker icon first to generate audio.')
    except Exception as e:
        messagebox.showerror('Error', f'Playback failed: {str(e)}')

def pause_audio():
    """Pause audio"""
    global audio_paused
    
    # Check if there's translation text
    text = t2.get("1.0", "end-1c")
    if not text or text.strip() == '':
        messagebox.showerror('Error', 'No translation to read aloud!')
        return
    
    try:
        pygame.mixer.music.pause()
        audio_paused = True
        pause_btn.config(fg=COLORS['text_lighter'], state=DISABLED)
        play_btn.config(fg=COLORS['text_light'], state=NORMAL)
    except:
        pass


def text_to_speech():
    text = t2.get("1.0", "end-1c")
    target_lang = l.get()
    
    if not text or text.strip() == '':
        messagebox.showerror('Error', 'No translation to read aloud!')
        return

    # Check if text is too long for TTS
    if len(text) > 500:
        response = messagebox.askyesno('Long Text', 
            f'The translation is {len(text)} characters long. Text-to-speech may take a while. Continue?')
        if not response:
            return

    lang_codes = {
        'Afrikaans': 'af', 'Albanian': 'sq', 'Arabic': 'ar', 'Bengali': 'bn',
        'Chinese': 'zh-CN', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl',
        'English': 'en', 'Finnish': 'fi', 'French': 'fr', 'German': 'de',
        'Greek': 'el', 'Hindi': 'hi', 'Hungarian': 'hu', 'Indonesian': 'id',
        'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko', 'Malayalam': 'ml',
        'Marathi': 'mr', 'Norwegian': 'no', 'Polish': 'pl', 'Portuguese': 'pt',
        'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr', 'Spanish': 'es',
        'Swahili': 'sw', 'Swedish': 'sv', 'Tamil': 'ta', 'Telugu': 'te',
        'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Vietnamese': 'vi'
    }
    lang_code = lang_codes.get(target_lang, 'en')

    # Run in a separate thread to avoid freezing UI
    import threading
    
    def generate_and_play():
        try:
            # Stop any currently playing audio
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                time.sleep(0.3)
            except:
                pass
            
            # Delete old file
            if os.path.exists("translation.mp3"):
                try:
                    os.remove("translation.mp3")
                except:
                    pass
            
            # Generate audio (this is the slow part)
            speech = gTTS(text=text, lang=lang_code, slow=False)
            speech.save("translation.mp3")
            
            # Play audio
            pygame.mixer.init()
            pygame.mixer.music.load("translation.mp3")
            pygame.mixer.music.play()
            
            # Visual feedback on main thread
           # Visual feedback and enable controls on main thread
            root.after(0, lambda: speaker_btn.config(fg=COLORS['primary']))
            root.after(1000, lambda: speaker_btn.config(fg=COLORS['text_light']))
            root.after(0, lambda: play_btn.config(state=NORMAL, fg=COLORS['text_light']))
            root.after(0, lambda: pause_btn.config(state=DISABLED, fg=COLORS['text_lighter']))
            
        except Exception as e:
            root.after(0, lambda: messagebox.showerror('Error', f'Text-to-speech failed: {str(e)}'))
    
    # Start thread
    tts_thread = threading.Thread(target=generate_and_play, daemon=True)
    tts_thread.start()
    
    # Show feedback that it's working
    speaker_btn.config(fg=COLORS['warning'])
    messagebox.showinfo('Please Wait', 'Generating audio... This may take a moment for long text.')


def start_recording():
    recognizer = sr.Recognizer()
    mic_btn.config(fg=COLORS['danger'])
    root.update()
    try:
        with sr.Microphone() as source:
            messagebox.showinfo('Recording', 'Listening... Speak now!')
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        try:
            text = recognizer.recognize_google(audio)
            t1.delete(1.0, 'end')
            t1.insert('end', text)
            update_char_count()
            mic_btn.config(fg=COLORS['success'])
            root.after(1500, lambda: mic_btn.config(fg=COLORS['text_light']))
        except sr.UnknownValueError:
            messagebox.showerror('Error', 'Could not understand audio')
            mic_btn.config(fg=COLORS['text_light'])
        except sr.RequestError:
            messagebox.showerror('Error', 'Could not request results')
            mic_btn.config(fg=COLORS['text_light'])
    except Exception as e:
        messagebox.showerror('Error', f'Microphone error: {str(e)}')
        mic_btn.config(fg=COLORS['text_light'])


def swap_languages():
    source = a.get()
    target = l.get()
    if source != 'Auto Detect' and target != 'Select Language':
        a.set(target)
        l.set(source)
        source_text = t1.get("1.0", "end-1c")
        target_text = t2.get("1.0", "end-1c")
        t1.delete(1.0, 'end')
        t2.delete(1.0, 'end')
        if target_text:
            t1.insert('end', target_text)
        if source_text:
            t2.insert('end', source_text)
        update_char_count()


def update_char_count(event=None):
    count = len(t1.get("1.0", "end-1c"))
    char_count_label.config(text=f"{count} / 5000")
    char_count_label.config(fg=COLORS['danger'] if count > 5000 else COLORS['text_lighter'])


def view_history():
    from tkinter import Toplevel
    history_window = Toplevel(root)
    history_window.title('Translation History')
    history_window.geometry('800x500')
    history_window.configure(bg=COLORS['bg'])

    Label(history_window, text="Translation History", font=('Arial', 18, 'bold'),
          bg=COLORS['bg'], fg=COLORS['text_dark']).pack(pady=20)

    list_frame = Frame(history_window, bg=COLORS['card'], relief=FLAT)
    list_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))

    scrollbar = Scrollbar(list_frame)
    scrollbar.pack(side=RIGHT, fill=Y)

    history_list = Listbox(list_frame, font=('Arial', 11), yscrollcommand=scrollbar.set,
                          bg=COLORS['card'], fg=COLORS['text_dark'],
                          selectbackground=COLORS['primary'], bd=0, highlightthickness=0)
    history_list.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
    scrollbar.config(command=history_list.yview)

    if not translation_history:
        history_list.insert(END, "No translation history yet")
    else:
        for item in reversed(translation_history):
            history_list.insert(END, f"📅 {item['timestamp']} | {item['source_lang']} → {item['target_lang']}")
            history_list.insert(END, f"   {item['source'][:80]}...")
            history_list.insert(END, f"   → {item['translation'][:80]}...")
            history_list.insert(END, "")

    Button(history_window, text="Close", font=('Arial', 12, 'bold'),
           bg=COLORS['primary'], fg='white', padx=30, pady=10, relief=FLAT,
           cursor='hand2', command=history_window.destroy, bd=0,
           activebackground=COLORS['primary_hover']).pack(pady=(0, 20))


def on_enter_btn(e, button, color):
    button['background'] = color

def on_leave_btn(e, button, color):
    button['background'] = color


load_history()


# ===== UI LAYOUT =====

# Top frame
top_frame = Frame(root, bg=COLORS['card'], height=100)
top_frame.pack(fill=X, padx=20, pady=(20, 10))
top_frame.pack_propagate(False)

lang_frame = Frame(top_frame, bg=COLORS['card'])
lang_frame.place(relx=0.5, rely=0.5, anchor='center')

# --- SOURCE SIDE ---
source_label = Label(lang_frame, text="From", font=('Arial', 13, 'bold'),
                    bg=COLORS['card'], fg=COLORS['text_light'])
source_label.grid(row=0, column=0, padx=25, pady=(0, 5))

# Button frame with border (this gets highlighted)
source_btn_frame = Frame(lang_frame, bg=COLORS['card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
source_btn_frame.grid(row=1, column=0, padx=25)

source_btn = Button(source_btn_frame, text="Auto Detect", font=('Arial', 12),
                   bg=COLORS['card'], fg=COLORS['text_dark'],
                   relief=FLAT, bd=0, cursor='hand2', anchor='w',
                   activebackground=COLORS['card'], padx=10, pady=6)
source_btn.pack(side=LEFT)

source_chevron = Label(source_btn_frame, text="▾", font=('Arial', 10),
                      bg=COLORS['card'], fg=COLORS['text_lighter'], padx=6)
source_chevron.pack(side=RIGHT)

# Hover on source button frame
def source_hover_on(e):
    if not source_popup.is_open:
        source_btn_frame.config(highlightbackground=COLORS['border_hover'], highlightthickness=2)
def source_hover_off(e):
    if not source_popup.is_open:
        source_btn_frame.config(highlightbackground=COLORS['border'], highlightthickness=1)

source_btn.bind('<Enter>', source_hover_on)
source_btn.bind('<Leave>', source_hover_off)
source_chevron.bind('<Enter>', source_hover_on)
source_chevron.bind('<Leave>', source_hover_off)


# --- SWAP ARROW ---
arrow_btn = Button(lang_frame, text="⇄", font=('Arial', 24), bg=COLORS['card'],
                   fg=COLORS['arrow'], relief=FLAT, cursor='hand2',
                   command=swap_languages, bd=0, activebackground=COLORS['card'],
                   activeforeground=COLORS['arrow_hover'])
arrow_btn.grid(row=1, column=1, padx=12)
arrow_btn.bind('<Enter>', lambda e: arrow_btn.config(fg=COLORS['arrow_hover']))
arrow_btn.bind('<Leave>', lambda e: arrow_btn.config(fg=COLORS['arrow']))


# --- TARGET SIDE ---
target_label = Label(lang_frame, text="To", font=('Arial', 13, 'bold'),
                    bg=COLORS['card'], fg=COLORS['text_light'])
target_label.grid(row=0, column=2, padx=25, pady=(0, 5))

target_btn_frame = Frame(lang_frame, bg=COLORS['card'],
                        highlightbackground=COLORS['border'], highlightthickness=1)
target_btn_frame.grid(row=1, column=2, padx=25)

target_btn = Button(target_btn_frame, text="Select Language", font=('Arial', 12),
                   bg=COLORS['card'], fg=COLORS['text_dark'],
                   relief=FLAT, bd=0, cursor='hand2', anchor='w',
                   activebackground=COLORS['card'], padx=10, pady=6)
target_btn.pack(side=LEFT)

target_chevron = Label(target_btn_frame, text="▾", font=('Arial', 10),
                      bg=COLORS['card'], fg=COLORS['text_lighter'], padx=6)
target_chevron.pack(side=RIGHT)

def target_hover_on(e):
    if not target_popup.is_open:
        target_btn_frame.config(highlightbackground=COLORS['border_hover'], highlightthickness=2)
def target_hover_off(e):
    if not target_popup.is_open:
        target_btn_frame.config(highlightbackground=COLORS['border'], highlightthickness=1)

target_btn.bind('<Enter>', target_hover_on)
target_btn.bind('<Leave>', target_hover_off)
target_chevron.bind('<Enter>', target_hover_on)
target_chevron.bind('<Leave>', target_hover_off)


# --- CREATE POPUPS (after frames exist) ---
source_popup = FloatingLangPopup(root, a, LANGUAGES_SOURCE, source_btn_frame)
target_popup = FloatingLangPopup(root, l, LANGUAGES_TARGET, target_btn_frame)

# Wire buttons to toggle popups
source_btn.config(command=source_popup.toggle)
source_chevron.bind('<Button-1>', lambda e: source_popup.toggle())
target_btn.config(command=target_popup.toggle)
target_chevron.bind('<Button-1>', lambda e: target_popup.toggle())

# Update button text when StringVar changes
def update_source_btn(*args):
    source_btn.config(text=a.get())
a.trace_add('write', update_source_btn)

def update_target_btn(*args):
    target_btn.config(text=l.get())
l.trace_add('write', update_target_btn)


# --- BOTTOM FRAME (buttons) ---
bottom_frame = Frame(root, bg=COLORS['bg'], height=80)
bottom_frame.pack(side=BOTTOM, fill=X, padx=20, pady=(10, 20))
bottom_frame.pack_propagate(False)

button_container = Frame(bottom_frame, bg=COLORS['bg'])
button_container.place(relx=0.5, rely=0.5, anchor='center')

translate_btn = Button(button_container, text="Translate", font=('Arial', 12, 'bold'),
                      bg=COLORS['primary'], fg='white', padx=30, pady=12,
                      relief=FLAT, cursor='hand2', command=translate, bd=0,
                      activebackground=COLORS['primary_hover'])
translate_btn.grid(row=0, column=0, padx=5)
translate_btn.bind("<Enter>", lambda e: on_enter_btn(e, translate_btn, COLORS['primary_hover']))
translate_btn.bind("<Leave>", lambda e: on_leave_btn(e, translate_btn, COLORS['primary']))

clear_btn = Button(button_container, text="Clear", font=('Arial', 11),
                  bg=COLORS['card'], fg=COLORS['text_dark'], padx=20, pady=12,
                  relief=FLAT, cursor='hand2', command=clear, bd=0,
                  highlightbackground=COLORS['border'], highlightthickness=1)
clear_btn.grid(row=0, column=1, padx=5)

copy_btn = Button(button_container, text="Copy", font=('Arial', 11),
                 bg=COLORS['card'], fg=COLORS['text_dark'], padx=20, pady=12,
                 relief=FLAT, cursor='hand2', command=copy, bd=0,
                 highlightbackground=COLORS['border'], highlightthickness=1)
copy_btn.grid(row=0, column=2, padx=5)

history_btn = Button(button_container, text="History", font=('Arial', 11),
                    bg=COLORS['card'], fg=COLORS['text_dark'], padx=20, pady=12,
                    relief=FLAT, cursor='hand2', command=view_history, bd=0,
                    highlightbackground=COLORS['border'], highlightthickness=1)
history_btn.grid(row=0, column=3, padx=5)


# --- MIDDLE FRAME (text boxes) ---
middle_frame = Frame(root, bg=COLORS['bg'])
middle_frame.pack(fill=BOTH, expand=True, padx=20, pady=0)

middle_frame.grid_columnconfigure(0, weight=1)
middle_frame.grid_columnconfigure(1, weight=1)
middle_frame.grid_rowconfigure(0, weight=1)

# LEFT BOX
left_frame = Frame(middle_frame, bg='#fafafa', relief=FLAT, bd=0,
                  highlightbackground=COLORS['border'], highlightthickness=1)
left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 8))

left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_rowconfigure(0, weight=0)
left_frame.grid_rowconfigure(1, weight=1)
left_frame.grid_rowconfigure(2, weight=0)

left_header = Frame(left_frame, bg='#fafafa')
left_header.grid(row=0, column=0, sticky='ew', padx=15, pady=(12, 5))

input_label = Label(left_header, text="Enter text", font=('Arial', 12, 'bold'),
                   bg='#fafafa', fg=COLORS['text_light'])
input_label.pack(side=LEFT, anchor='w')

char_count_label = Label(left_header, text="0 / 5000", font=('Arial', 10),
                        bg='#fafafa', fg=COLORS['text_lighter'])
char_count_label.pack(side=RIGHT, anchor='e')

t1 = Text(left_frame, font=('Arial', 13), wrap=WORD, relief=FLAT,
         bg='#fafafa', fg=COLORS['text_dark'],
         insertbackground=COLORS['primary'], bd=0,
         highlightthickness=0, padx=10, pady=5)
t1.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
t1.bind('<KeyRelease>', update_char_count)

left_bottom = Frame(left_frame, bg='#fafafa')
left_bottom.grid(row=2, column=0, sticky='ew', padx=15, pady=(0, 10))

mic_btn = Button(left_bottom, text="🎤", font=('Arial', 16),
                bg='#fafafa', fg=COLORS['text_light'],
                relief=FLAT, cursor='hand2', command=start_recording,
                bd=0, activebackground='#fafafa')
mic_btn.pack(side=LEFT, anchor='w')

# RIGHT BOX
right_frame = Frame(middle_frame, bg='#fafafa', relief=FLAT, bd=0,
                   highlightbackground=COLORS['border'], highlightthickness=1)
right_frame.grid(row=0, column=1, sticky='nsew', padx=(8, 0))

right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_rowconfigure(0, weight=0)
right_frame.grid_rowconfigure(1, weight=1)
right_frame.grid_rowconfigure(2, weight=0)

right_header = Frame(right_frame, bg='#fafafa')
right_header.grid(row=0, column=0, sticky='ew', padx=15, pady=(12, 5))

output_label = Label(right_header, text="Translation", font=('Arial', 12, 'bold'),
                    bg='#fafafa', fg=COLORS['text_light'])
output_label.pack(side=LEFT, anchor='w')

detected_lang_label = Label(right_header, text="", font=('Arial', 10),
                           bg='#fafafa', fg=COLORS['success'])
detected_lang_label.pack(side=RIGHT, anchor='e')

t2 = Text(right_frame, font=('Arial', 13), wrap=WORD, relief=FLAT,
         bg='#fafafa', fg=COLORS['text_dark'], state=NORMAL, bd=0,
         highlightthickness=0, padx=10, pady=5)
t2.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)

# Speaker icon row - NOW WITH PLAY/PAUSE CONTROLS (PROPERLY ALIGNED)
right_bottom = Frame(right_frame, bg='#fafafa')
right_bottom.grid(row=2, column=0, sticky='ew', padx=15, pady=(0, 10))

# Container frame to hold all audio controls aligned
audio_controls = Frame(right_bottom, bg='#fafafa')
audio_controls.pack(side=LEFT, anchor='w')

# Speaker button (generates TTS)
speaker_btn = Button(audio_controls, text="🔊", font=('Arial', 16),
                    bg='#fafafa', fg=COLORS['text_light'],
                    relief=FLAT, cursor='hand2', command=text_to_speech,
                    bd=0, activebackground='#fafafa')
speaker_btn.grid(row=0, column=0, padx=(0, 8))

# Speaker icon row - NOW WITH PLAY/PAUSE CONTROLS (PROPERLY ALIGNED)
right_bottom = Frame(right_frame, bg='#fafafa')
right_bottom.grid(row=2, column=0, sticky='ew', padx=15, pady=(0, 10))

# Container frame to hold all audio controls aligned
audio_controls = Frame(right_bottom, bg='#fafafa')
audio_controls.pack(side=LEFT, anchor='w')

# Speaker button (generates TTS)
speaker_btn = Button(audio_controls, text="🔊", font=('Arial', 16),
                    bg='#fafafa', fg=COLORS['text_light'],
                    relief=FLAT, cursor='hand2', command=text_to_speech,
                    bd=0, activebackground='#fafafa')
speaker_btn.grid(row=0, column=0, padx=(0, 8))

# Play button (plays/resumes audio)
play_btn = Button(audio_controls, text="▶", font=('Arial', 12),
                 bg='#fafafa', fg=COLORS['text_lighter'],
                 relief=FLAT, cursor='hand2', command=lambda: play_audio(),
                 bd=0, activebackground='#fafafa', state=NORMAL)
play_btn.grid(row=0, column=1, padx=(0, 4), pady=(2, 0))

# Pause button (pauses audio)
pause_btn = Button(audio_controls, text="⏸", font=('Arial', 12),
                  bg='#fafafa', fg=COLORS['text_lighter'],
                  relief=FLAT, cursor='hand2', command=lambda: pause_audio(),
                  bd=0, activebackground='#fafafa', state=NORMAL)
pause_btn.grid(row=0, column=2, pady=(2, 0))

# Keyboard shortcuts
root.bind('<Control-Return>', translate)
root.bind('<Control-l>', clear)
root.bind('<Control-c>', lambda e: copy() if t2.get("1.0", "end-1c").strip() else None)
root.bind('<Control-h>', lambda e: view_history())
root.bind('<Control-m>', lambda e: start_recording())
root.bind('<Control-s>', lambda e: swap_languages())

root.mainloop()