# Macros Module Documentation

## Overview
The Macros module provides comprehensive automation capabilities for QuantumDesk, allowing users to record, play, and manage automation macros for repetitive tasks.

## Features

### 1. Macro Recording
- **Live Recording**: Record keyboard and mouse actions in real-time
- **Event Capture**: Captures keystrokes, mouse clicks, movements, and scrolling
- **Timing Preservation**: Maintains timing between events for accurate playback
- **Safe Recording**: Built-in safety features to prevent infinite loops

### 2. Text Macros
- **Quick Text Entry**: Create simple text-typing macros
- **Fast Creation**: Instantly create macros for frequently typed text
- **Custom Names**: Organize text macros with descriptive names

### 3. Macro Management
- **Macro List**: View all available macros with details
- **Playback Control**: Play, pause, and stop macro execution
- **Macro Deletion**: Remove unwanted macros
- **Status Monitoring**: Real-time status updates during recording/playback

### 4. Import/Export
- **Export Macros**: Save macros to JSON files for backup or sharing
- **Import Macros**: Load macros from external files
- **Cross-System Compatibility**: Share macros between different computers

### 5. Elite Tools
- **Macro Analytics**: View statistics about macro usage and complexity
- **Scheduler**: (Coming Soon) Schedule macros to run at specific times
- **Batch Operations**: (Coming Soon) Chain multiple macros together

## GUI Interface

### Recording Section
- **Macro Name Entry**: Enter a name for the new macro
- **Start Recording**: Begin capturing user actions
- **Stop Recording**: Save the recorded macro
- **Recording Status**: Real-time feedback during recording

### Quick Text Macros
- **Name Field**: Enter a name for the text macro
- **Content Field**: Enter the text to be typed
- **Create Button**: Generate the text macro instantly

### Management Section
- **Macro List Display**: Shows all available macros with details
- **Macro Selection**: Enter macro name for operations
- **Control Buttons**: Play, Delete, Stop, Refresh functionality
- **Status Updates**: Real-time feedback for all operations

## Technical Implementation

### MacroManager Class
```python
class MacroManager:
    def __init__(self):
        # Initialize macro storage and configuration
        
    def start_recording(self, macro_name):
        # Begin recording user actions
        
    def stop_recording(self, macro_name):
        # Stop recording and save macro
        
    def play_macro(self, macro_name):
        # Execute a saved macro
        
    def create_text_macro(self, name, text):
        # Create a simple text-typing macro
```

### Storage Format
Macros are stored in JSON format with the following structure:
- **Name**: User-defined macro name
- **Events**: Array of recorded actions
- **Created**: Timestamp of creation
- **Duration**: Total macro duration
- **Type**: Macro type (recorded/text)

### Event Types
- **Keyboard Events**: Key presses, releases, and combinations
- **Mouse Events**: Clicks, movements, scrolling, drag operations
- **Timing Events**: Delays and pauses between actions

## Safety Features

### Recording Safety
- **Failsafe**: Built-in escape mechanisms
- **Timeout Protection**: Prevents infinite recording sessions
- **Event Filtering**: Ignores system-critical key combinations

### Playback Safety
- **Speed Limiting**: Controls playback speed to prevent system overload
- **Interrupt Capability**: Allow users to stop playback immediately
- **Error Handling**: Graceful handling of playback errors

## Usage Examples

### Recording a Macro
1. Enter a descriptive name in the "Macro Name" field
2. Click "Start Recording"
3. Perform the actions you want to automate
4. Click "Stop Recording" to save

### Creating Text Macros
1. Enter a name in the "Text Macro Name" field
2. Enter the text content in the "Text to type" field
3. Click "Create Text Macro"

### Playing Macros
1. Enter the macro name in the "Select macro name" field
2. Click "Play Macro" to execute
3. Use "Stop Playback" to interrupt if needed

### Managing Macros
- Click "Refresh List" to update the macro display
- Enter macro name and click "Delete Macro" to remove
- Use "Export Macro" to save to file
- Use "Import Macro" to load from file

## Configuration

### Storage Location
Macros are stored in: `~/.quantumdesk/macros.json`

### Dependencies
- `pyautogui`: GUI automation
- `keyboard`: Keyboard event handling
- `mouse`: Mouse event handling
- `json`: Data storage
- `threading`: Background operations

## Security Considerations

### Privacy
- Macros are stored locally only
- No network transmission of recorded actions
- User has full control over macro data

### System Safety
- Built-in failsafe mechanisms
- No recording of sensitive system keys
- Playback speed limitations

## Future Enhancements

### Planned Features
- **Conditional Logic**: Add if/then statements to macros
- **Variable Support**: Dynamic values in macro playback
- **Loop Operations**: Repeat macro sections
- **System Integration**: Trigger macros from system events
- **Advanced Scheduling**: Complex time-based execution
- **Macro Sharing**: Community macro library

### Performance Improvements
- **Compression**: Reduce macro file sizes
- **Optimization**: Faster playback algorithms
- **Memory Management**: Efficient event storage

## Troubleshooting

### Common Issues
1. **Recording not starting**: Check macro name is entered
2. **Playback not working**: Verify macro exists and is valid
3. **Permission errors**: Run as administrator if needed
4. **Performance issues**: Reduce macro complexity

### Error Messages
- "Macro name cannot be empty": Enter a valid macro name
- "Already recording": Stop current recording first
- "Macro not found": Check macro name spelling
- "Recording failed": Restart application and try again

## API Reference

### Core Methods
- `start_recording(name)`: Begin macro recording
- `stop_recording(name)`: End recording and save
- `play_macro(name)`: Execute saved macro
- `delete_macro(name)`: Remove macro
- `get_macro_list()`: List all macros
- `export_macro(name, path)`: Save macro to file
- `import_macro(path)`: Load macro from file

### Status Methods
- `get_recording_status()`: Current recording state
- `get_macro_info(name)`: Detailed macro information
- `is_recording`: Boolean recording status
- `is_playing`: Boolean playback status

This documentation provides a comprehensive guide to using the Macros module in QuantumDesk for automation and productivity enhancement.
