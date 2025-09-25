# ENCRYD_v1

**ENCRYD_v1** is a high-tech, neon-themed AES encryption/decryption dashboard built with PyQt5. It provides an easy-to-use, visually appealing interface for file encryption and decryption using C binaries. The dashboard features a semi-transparent background, animated neon borders, and a modern UI/UX.

---

## Features

- **Encrypt & Decrypt Tabs**  
  Quickly encrypt or decrypt files using AES with password protection.
- **Animated Neon Frame**  
  Hi-tech glowing border with animated gradients and corner widgets.
- **Semi-Transparent Dashboard**  
  Futuristic look with customizable transparency.
- **Terminal Output**  
  Styled output panel with scanline animation for process feedback.
- **Movable & Resizable**  
  Drag the dashboard anywhere, resize with a grip, and control window state.
- **Dark-themed File Picker**  
  Integrated file dialogs with white fonts for clarity.
- **Build Button**  
  One-click build system for your C binaries via `make`.

---

## Screenshots
  
<img width="1242" height="935" alt="Screenshot at 2025-09-23 16-36-20" src="https://github.com/user-attachments/assets/f65c6c4a-5190-4855-a8b0-2ca3386bf301" />

---

## Requirements

- Python 3.x
- [PyQt5](https://pypi.org/project/PyQt5/)
- C binaries: `encryptor`, `decryptor` (compile with included `Makefile`)
- Fira Mono or Consolas font (recommended for best appearance)
- OS: Linux

---

## Setup & Usage

1. **Install Dependencies:**

   ```bash
   sudo apt-get install libssl-dev

   pip install pyqt5
   ```

2. **Build C Binaries:**

   Place your C source files and `Makefile` in the project directory.  
   Click **🛠 Build C Binaries** in the dashboard.

   Binaries will be placed in the `output` subdirectory.

3. **Run the Dashboard:**

   ```bash
   python encryd.py
   ```

4. **Using the App:**

   - Choose **Encrypt** or **Decrypt** from the sidebar.
   - Select input and output files via the file picker.
   - Enter your password.
   - Click **Run** to perform the operation.
   - See feedback in the terminal output panel.

---

## File Structure

```
├── encryd.py        # Main dashboard code
├── output/             # Directory for C binaries
│   ├── encryptor
│   └── decryptor
├── encryptor_aes.c     # c source code
├── decryptor_aes.c     # c source code
├── Makefile            # For building C binaries
└── README.md           # This file

```

---

## Customization

- **Appearance:**  
  Edit color values and border styles in `NeonFrame` for your own neon theme.
- **C Binary Integration:**  
  Make sure your C binaries accept input/output and password parameters as expected.
- **Fonts:**  
  The dashboard will use "Fira Mono" if available, or fall back to "Consolas".

---

## Credits

Made By **WebDragon63**
  
---
