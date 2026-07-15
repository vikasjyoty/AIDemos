# Bedrock Chat Console UI

This project is a React + TypeScript UI for chatting with your LLM API (for example, an AWS endpoint).

## Features

- Light themed, professional chat interface
- Top navigation with branding and logo
- Dummy login screen before entering chat home
- Chat history with user/assistant message cards
- Browser speech-to-text (microphone input)
- Browser text-to-speech (read assistant replies)
- Voice activity animation while mic or TTS is active
- Basic error handling for login, speech, and API requests

## App Configuration

Update API and login settings in:

- `src/config.ts`

Fields:

- `appConfig.api.endpoint` - your API URL
- `appConfig.api.apiKey` - optional bearer/API key
- `appConfig.auth.username` - dummy login username
- `appConfig.auth.password` - dummy login password

## Run Locally

From `awsragdemo.client`:

1. `npm install`
2. `npm run dev`

Then open the local URL shown by Vite.

## Login (Dummy)

Use the credentials defined in `src/config.ts`.

Default values:

- Username: `demo`
- Password: `demo123`

## Expected API Request/Response

The UI sends:

- `POST` to configured endpoint
- JSON body:
  - `message: string`
  - `history: { role, content }[]`

The UI reads assistant text from response fields in this order:

1. `reply`
2. `message`
3. `output`

If none exist, a fallback message is shown.

## Browser Notes

- Speech-to-text uses browser Speech Recognition APIs.
- Text-to-speech uses `speechSynthesis`.
- For mic input, allow microphone permission when prompted.
