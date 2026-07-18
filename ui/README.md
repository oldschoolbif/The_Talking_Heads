# The Talking Heads - React UI

A React.js-based user interface for The Talking Heads video generation system.

## Features

- 📄 **Script Selection**: Browse and select scripts from the examples/scripts folder
- ✏️ **Script Editor**: Edit scripts with formatting tags for expressions, gestures, and pauses
- 👥 **Persona Selection**: Select 1-5 personas with avatar previews and voice samples
- ⚙️ **Configuration**: Configure API choices, resolution, quality, and other settings
- 🎬 **Video Generation**: Generate videos with real-time progress tracking

## Setup

### Install Dependencies

```bash
cd ui
npm install
```

### Start Development Server

```bash
# Terminal 1: Start React dev server
npm start

# Terminal 2: Start Python API server
python server.py
```

The UI will be available at http://localhost:3000
The API will be available at http://localhost:5001

## Usage

1. **Select a Script**: Choose a script from the examples/scripts folder
2. **Edit Script**: Modify the script content and add formatting tags
3. **Select Personas**: Choose 1-5 personas for the video
4. **Configure Settings**: Set resolution, quality, and API options
5. **Generate Video**: Click "Generate Video" to start the process

## Script Format

Scripts use a simple format:

```
PERSONA: Dialogue text here
[expression:happy] [gesture:point] Optional tags
[pause:2] Pause tags create delays
```

### Available Tags

- **Expressions**: `[expression:happy]`, `[expression:neutral]`, `[expression:surprised]`
- **Gestures**: `[gesture:point]`, `[gesture:wave]`, `[gesture:emphasize]`
- **Pauses**: `[pause:2]`, `[pause:3]` (seconds)

## Configuration

The UI allows you to configure:

- **Avatar Engine**: HeyGen or D-ID
- **Resolution**: 720p (fast) or 1080p (quality)
- **Quality**: Fastest, Fast, Medium, High
- **Webhook**: Enable/disable webhooks for faster notifications
- **Output Format**: MP4 (default)
- **FPS**: 15-60 frames per second

## Development

### Project Structure

```
ui/
├── public/           # Static files
├── src/
│   ├── components/   # React components
│   ├── services/     # API service layer
│   ├── App.js        # Main app component
│   └── index.js      # Entry point
├── server.py         # Flask API server
└── package.json      # Node dependencies
```

### Building for Production

```bash
npm run build
```

The built files will be in the `build/` directory.

