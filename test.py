

def get_key():
    """
    Detect key inputs using arrow prefixes
    All console terminals use this
    """
    sys = __import__("sys")
    if sys.platform.startswith('win'):
        msvcrt = __import__("msvcrt")
        while True:
            ch = msvcrt.getch() # type: ignore
            if ch == b'\xe0':  # Arrow prefix
                ch2 = msvcrt.getch() # type: ignore
                if ch2 == b'H': return 'UP'
                elif ch2 == b'P': return 'DOWN'
                elif ch2 == b'K': return 'LEFT'
                elif ch2 == b'M': return 'RIGHT'
            else:
                ch = ch.decode()
                if ch.lower() == 'w': return 'UP'
                elif ch.lower() == 's': return 'DOWN'
                elif ch.lower() == 'a': return 'LEFT'
                elif ch.lower() == 'd': return 'RIGHT'
                elif ch == 'q': return 'QUIT'
    else:
        tty = __import__("tty")
        termios = __import__("termios")
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                next1 = sys.stdin.read(1)
                if next1 == '': return 'ESCAPE'
                next2 = sys.stdin.read(1)
                if next1 == '[':
                    if next2 == 'A': return 'UP'
                    elif next2 == 'B': return 'DOWN'
                    elif next2 == 'C': return 'RIGHT'
                    elif next2 == 'D': return 'LEFT'
            elif ch.lower() == 'w': return 'UP'
            elif ch.lower() == 's': return 'DOWN'
            elif ch.lower() == 'a': return 'LEFT'
            elif ch.lower() == 'd': return 'RIGHT'
            elif ch == 'q': return 'QUIT'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# === Example usage ===
print("Press arrow keys or WASD to move, 'q' to quit.")

while True:
    key = get_key()
    if key:
        print(f"You pressed: {key}")
        if key == 'QUIT':
            print("Goodbye!")
            break