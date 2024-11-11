# Project Name

![Demo GIF](assets\Recording2024-11-12011239-ezgif.com-effects.gif)

A Python application designed with a GUI using PyQt5, capable of monitoring and displaying system metrics such as CPU and memory usage.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Project Overview

This project is a system monitoring application that uses `psutil` to gather real-time system data and `PyQt5` for the graphical user interface. The application visually represents CPU, memory, and internet usage, with unique emoji expressions to indicate different levels of system load.

## Features

- **Real-time System Monitoring**: Tracks CPU, memory, and network usage.
- **Interactive UI**: Emoji expressions change based on system stress, with animations to convey load visually.
- **User Interaction**: Right-click actions to animate and display an option for closing the widget.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yourprojectname.git
   ```
2. Navigate to the project directory:
   ```bash
   cd yourprojectname
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python app.py
```

The application will start and display a widget with animated emojis that change based on system metrics. Right-click the widget to access additional actions.

## Files

- **app.py**: Main application file containing the logic for system monitoring and UI.
- **requirements.txt**: Contains the necessary Python packages (`psutil`, `PyQt5`, etc.) for running the application.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

