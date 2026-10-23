# TODO List for Fixing Security Script

- [x] Filter selected files in `__main__` to only include .txt and programming language files (e.g., .py, .java, .cpp, .c, .js, .ts, .html, .css, .php, .rb, .go).
- [x] Add window message hooking using `win32gui` to intercept WM_CLOSE and perform face scan.
- [x] Modify `on_exit_attempt` to trigger alarm and restart surveillance if intruder detected during shutdown.
- [ ] Test the script to ensure it doesn't close on right-click without authentication and restarts surveillance on intruder detection.
