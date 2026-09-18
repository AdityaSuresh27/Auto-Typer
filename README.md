# Auto Typer

Auto Typer is a Python-based graphical user interface (GUI) application designed to simulate human keyboard input. By leveraging operating system-level keystroke simulation, it ensures that target applications and web interfaces process the input as physical hardware events rather than clipboard paste operations.

## Key Features

- **Hardware-Level Simulation**: Utilizes the `pynput` library to dispatch genuine OS-level key events, bypassing mechanisms that detect or restrict pasted content.
- **Configurable Input Rate**: Allows precise adjustment of the typing speed, ranging from 5 to 2000 characters per second, via the integrated interface.
- **Initialization Delay**: Provides a configurable pre-execution delay (1 to 10 seconds), ensuring sufficient time to shift focus to the designated target window before input begins.
- **Process Interruption**: Features a global interruption hook, enabling users to terminate the typing sequence instantaneously by pressing the `Esc` key or utilizing the interface's stop function.
- **Modern Interface**: Implements a responsive, dark-themed GUI built upon the `customtkinter` framework.
- **Real-Time Telemetry**: Displays continuous progress updates and operational status indicators within the application footer.

## System Requirements

- Python 3.x
- Supported Operating System (Windows, macOS, or Linux)

## Installation Instructions

1. Obtain the source code by cloning or downloading this repository.
2. Navigate to the project directory via the command line interface.
3. Install the necessary dependencies specified in the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

   The requisite packages encompass:
   - `customtkinter` (GUI framework)
   - `pynput` (Keystroke simulation)
   - `Pillow` (Image processing dependencies for the GUI)

## Operational Guide

1. Initialize the application by executing the primary script:

   ```bash
   python auto_typer.py
   ```

2. **Data Entry**: Input the intended text into the primary text area.
3. **Parameter Configuration**:
   - Utilize the **Typing Speed** control to define the output velocity.
   - Utilize the **Start Delay** control to allocate adequate time for context switching.
4. **Execution**: Click the **START TYPING** button to initiate the sequence.
5. **Context Switching**: Immediately shift focus to the target application or input field. The application will commence typing upon the conclusion of the initialization delay.
6. **Manual Termination**: To halt the process prematurely, press the `Esc` key or click the **STOP** button within the application interface.

## Technical Considerations

- **Application Focus**: It is imperative that the target input field retains focus prior to the conclusion of the countdown. The application will transmit keystrokes to whichever window currently holds system focus.
- **Thread Management**: The keystroke simulation and global interruption listeners are executed as background threads to ensure continuous responsiveness of the primary graphical interface.
