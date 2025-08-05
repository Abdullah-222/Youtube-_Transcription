# YouTube AI Assistant Extension

A Chrome extension that allows you to ask questions about YouTube videos using AI. The extension integrates with your backend transcription tool to provide intelligent responses about video content.

## Features

- **Automatic Video Detection**: Automatically detects YouTube videos and extracts video information
- **AI-Powered Q&A**: Ask questions about video content and get intelligent responses
- **Chat Interface**: Clean, modern chat interface for interacting with the AI
- **Conversation History**: Saves chat history per video for context-aware conversations
- **Real-time Analysis**: Analyze videos with a single click
- **Cross-tab Support**: Works across multiple YouTube tabs

## Installation

### Prerequisites

1. **Backend Server**: Make sure your backend server is running on `http://localhost:8000`
2. **Chrome Browser**: This extension works with Chrome and Chromium-based browsers

### Installation Steps

1. **Download/Clone**: Get the extension files from this repository
2. **Open Chrome Extensions**: Go to `chrome://extensions/` in your browser
3. **Enable Developer Mode**: Toggle the "Developer mode" switch in the top right
4. **Load Extension**: Click "Load unpacked" and select the `extension` folder
5. **Verify Installation**: You should see the "YouTube AI Assistant" extension in your extensions list

## Usage

### Basic Usage

1. **Navigate to YouTube**: Go to any YouTube video page
2. **Open Extension**: Click the extension icon in your browser toolbar
3. **Start Chatting**: Type your question about the video and press Enter
4. **Analyze Video**: Click "Analyze Current Video" for a comprehensive summary

### Features

- **Ask Questions**: Type any question about the video content
- **Video Analysis**: Get automatic summaries and insights
- **Chat History**: Previous conversations are saved and restored
- **Clear Chat**: Reset conversation history for the current video

### Supported YouTube URLs

The extension works with various YouTube URL formats:
- Standard watch URLs: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short URLs: `https://youtu.be/VIDEO_ID`
- Embedded URLs: `https://www.youtube.com/embed/VIDEO_ID`

## Technical Details

### Architecture

- **Manifest V3**: Uses the latest Chrome extension manifest version
- **Content Scripts**: Injects into YouTube pages to extract video information
- **Background Script**: Manages communication between popup and content scripts
- **Popup Interface**: Modern chat interface for user interaction
- **API Integration**: Connects to your FastAPI backend for AI processing

### File Structure

```
extension/
├── manifest.json              # Extension configuration
├── background/
│   └── background.js         # Background service worker
├── content-scripts/
│   ├── youtube-content.js    # YouTube page interaction
│   └── shared/
│       └── api-client.js     # Backend API client
├── popup/
│   ├── popup.html           # Popup interface
│   ├── popup.css            # Styling
│   └── popup.js             # Popup functionality
├── icons/
│   └── icon16.png           # Extension icon
└── test-extension.html      # Testing page
```

### API Endpoints

The extension communicates with your backend through these endpoints:

- `POST /extension/analyze`: Send video URL and question for AI processing
- `GET /health`: Health check for backend connectivity

### Permissions

- `activeTab`: Access to the current tab for video information
- `storage`: Save chat history and video data
- `scripting`: Inject content scripts into YouTube pages
- `host_permissions`: Access to YouTube and localhost for backend communication

## Troubleshooting

### Common Issues

1. **Extension Not Working on YouTube**
   - Make sure you're on a YouTube video page (not homepage)
   - Refresh the page and try again
   - Check browser console for errors

2. **Backend Connection Failed**
   - Verify your backend server is running on `http://localhost:8000`
   - Check the `/health` endpoint is accessible
   - Ensure CORS is properly configured

3. **Video Not Detected**
   - Navigate to a YouTube video page (URL should contain `/watch?v=`)
   - Refresh the page and wait a few seconds
   - Check if the video has a valid ID

4. **Chat History Not Saving**
   - Check browser storage permissions
   - Try clearing browser data and reinstalling extension

### Debug Mode

1. **Open Developer Tools**: Right-click the extension popup and select "Inspect"
2. **Check Console**: Look for error messages and debug information
3. **Test API**: Use the test page (`test-extension.html`) to verify connections

### Testing

Use the included test page to verify functionality:

1. Open `test-extension.html` in your browser
2. Run the automated tests
3. Check all components are working correctly

## Development

### Making Changes

1. **Edit Files**: Modify the extension files as needed
2. **Reload Extension**: Go to `chrome://extensions/` and click the refresh icon
3. **Test Changes**: Test the updated functionality

### Backend Integration

The extension expects your backend to have these features:

- FastAPI server running on `localhost:8000`
- `/extension/analyze` endpoint accepting POST requests
- `/health` endpoint for connectivity checks
- CORS configured to allow extension requests

### Customization

- **Styling**: Modify `popup/popup.css` for visual changes
- **API URL**: Change the base URL in `api-client.js` for different backends
- **Permissions**: Update `manifest.json` for additional permissions
- **Features**: Extend functionality by modifying the JavaScript files

## Security Notes

- The extension only accesses YouTube pages and your localhost backend
- No data is sent to external servers (except your backend)
- Chat history is stored locally in browser storage
- API keys and sensitive data should be kept on the backend

## Support

If you encounter issues:

1. Check the browser console for error messages
2. Verify your backend server is running and accessible
3. Test with the included test page
4. Check that you're on a valid YouTube video page

## License

This extension is part of your Transcription Tool project and follows the same license terms. 