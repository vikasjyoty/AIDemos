import { useEffect, useMemo, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { appConfig } from './config';
import './App.css';

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
}

interface BrowserSpeechRecognitionEvent {
    results: {
        [key: number]: {
            [key: number]: {
                transcript: string;
            };
            isFinal: boolean;
            length: number;
        };
        length: number;
    };
}

interface BrowserSpeechRecognition {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    onresult: ((event: BrowserSpeechRecognitionEvent) => void) | null;
    onend: (() => void) | null;
    onerror: ((event: { error: string }) => void) | null;
    start: () => void;
    stop: () => void;
}

type BrowserSpeechRecognitionConstructor = new () => BrowserSpeechRecognition;

const authStorageKey = 'aws-rag-demo-authenticated';

interface IconProps {
    name: 'login' | 'logout' | 'send' | 'mic' | 'speaker';
}

function Icon({ name }: IconProps) {
    const paths: Record<IconProps['name'], string> = {
        login: 'M10 2a8 8 0 1 0 8 8h-2a6 6 0 1 1-6-6V2Zm2.3 4.3 1.4-1.4L18.8 10l-5.1 5.1-1.4-1.4 2.7-2.7H8v-2h7l-2.7-2.7Z',
        logout: 'M10 2a8 8 0 1 1 0 16V16a6 6 0 1 0 0-12V2Zm3.7 4.3L12.3 7.7 15 10H8v2h7l-2.7 2.3 1.4 1.4 5.1-5.1-5.1-5.1Z',
        send: 'M2 10 18 3l-4.4 14-3.6-4.1-4.1-3.6L2 10Zm5.4-.6 2.9 2.5 2.2-6.9-5.1 4.4Z',
        mic: 'M10 13a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v4a3 3 0 0 0 3 3Zm-5-3a5 5 0 1 0 10 0h2a7 7 0 0 1-6 6.9V20H9v-3.1A7 7 0 0 1 3 10h2Z',
        speaker: 'M3 8h3.5L11 4v12l-4.5-4H3V8Zm11.4-3.4 1.4-1.4A9 9 0 0 1 19 10a9 9 0 0 1-3.2 6.8l-1.4-1.4A7 7 0 0 0 17 10a7 7 0 0 0-2.6-5.4Zm-2.8 2.8L13 6a5 5 0 0 1 0 8l-1.4-1.4a3 3 0 0 0 0-5.2Z',
    };

    return (
        <svg className="icon" viewBox="0 0 20 20" aria-hidden="true" focusable="false">
            <path d={paths[name]} />
        </svg>
    );
}

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [authError, setAuthError] = useState('');

    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isSending, setIsSending] = useState(false);
    const [error, setError] = useState('');
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);

    const speechRecognitionRef = useRef<BrowserSpeechRecognition | null>(null);

    const speechRecognitionCtor = useMemo(() => {
        const speechWindow = window as Window & {
            webkitSpeechRecognition?: BrowserSpeechRecognitionConstructor;
            SpeechRecognition?: BrowserSpeechRecognitionConstructor;
        };

        return speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
    }, []);

    const speechToTextSupported = speechRecognitionCtor !== undefined;
    const textToSpeechSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

    useEffect(() => {
        document.title = appConfig.appTitle;
        const isLoggedIn = sessionStorage.getItem(authStorageKey) === 'true';
        if (isLoggedIn) {
            setIsAuthenticated(true);
        }
    }, []);

    useEffect(() => {
        return () => {
            speechRecognitionRef.current?.stop();
            if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
        };
    }, []);

    const latestAssistantMessage = [...messages].reverse().find(message => message.role === 'assistant');

    return (
        <div className="app-shell">
            <nav className="top-nav">
                <div className="brand-block">
                    <div className="brand-row">
                        <img className="brand-logo" src="/favicon.svg" alt="App logo" />
                        <h1 className="brand-title">{appConfig.appTitle}</h1>
                    </div>
                    <p className="brand-subtitle">AWS LLM Chat Assistant</p>
                </div>
                <div className="nav-actions">
                    {isAuthenticated ? (
                        <button type="button" onClick={handleLogout}>
                            <Icon name="logout" />
                            Logout
                        </button>
                    ) : (
                        <span className="nav-badge">Please sign in</span>
                    )}
                </div>
            </nav>

            <main className="content-area">
                {!isAuthenticated ? (
                    <section className="login-panel" aria-label="Dummy login">
                        <img className="login-logo" src="/favicon.svg" alt="Bedrock Chat logo" />
                        <h2>Welcome</h2>
                        <p className="panel-description">Use the demo credentials to continue.</p>

                        {authError && <p className="error-text">{authError}</p>}

                        <form className="auth-form" onSubmit={handleLogin}>
                            <label>
                                Username
                                <input
                                    type="text"
                                    value={username}
                                    onChange={event => setUsername(event.target.value)}
                                    autoComplete="username"
                                    placeholder="Enter username"
                                />
                            </label>

                            <label>
                                Password
                                <input
                                    type="password"
                                    value={password}
                                    onChange={event => setPassword(event.target.value)}
                                    autoComplete="current-password"
                                    placeholder="Enter password"
                                />
                            </label>

                            <button type="submit">
                                <Icon name="login" />
                                Sign In
                            </button>
                        </form>

                        <p className="login-hint">
                            Demo user: <strong>{appConfig.auth.username}</strong> / <strong>{appConfig.auth.password}</strong>
                        </p>
                    </section>
                ) : (
                    <section className="chat-panel" aria-label="Chat home page">
                        <header className="chat-header">
                            <h2>Home</h2>
                            <p className="panel-description">
                                Connected to configured endpoint. Start your conversation.
                            </p>
                        </header>

                        <div className="message-list" role="log" aria-live="polite">
                            {messages.length === 0 && (
                                <p className="empty-state">Start chatting. Your messages will appear here.</p>
                            )}

                            {messages.map(message => (
                                <article key={message.id} className={`message ${message.role}`}>
                                    <header>
                                        <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
                                        <time>{new Date(message.timestamp).toLocaleTimeString()}</time>
                                    </header>
                                    <p>{message.content}</p>
                                    {message.role === 'assistant' && textToSpeechSupported && (
                                        <button
                                            type="button"
                                            className="mini-action"
                                            onClick={() => speakMessage(message.content)}
                                        >
                                            Speak
                                        </button>
                                    )}
                                </article>
                            ))}
                        </div>

                        {error && <p className="error-text">{error}</p>}

                        <form className="composer" onSubmit={handleSend}>
                            <textarea
                                value={input}
                                onChange={event => setInput(event.target.value)}
                                placeholder="Type your message..."
                                rows={3}
                            />

                            <div className="composer-actions">
                                <button type="submit" disabled={isSending || !input.trim()}>
                                    <Icon name="send" />
                                    {isSending ? 'Sending...' : 'Send'}
                                </button>

                                <button
                                    type="button"
                                    className={isListening ? 'is-active listening' : ''}
                                    disabled={!speechToTextSupported || isSending}
                                    onClick={toggleSpeechToText}
                                >
                                    <Icon name="mic" />
                                    {isListening ? 'Stop Mic' : 'Use Mic'}
                                </button>

                                <button
                                    type="button"
                                    className={isSpeaking ? 'is-active speaking' : ''}
                                    disabled={!textToSpeechSupported || latestAssistantMessage === undefined}
                                    onClick={() => {
                                        if (latestAssistantMessage) {
                                            speakMessage(latestAssistantMessage.content);
                                        }
                                    }}
                                >
                                    <Icon name="speaker" />
                                    Read Latest Reply
                                </button>
                            </div>

                            {(isListening || isSpeaking) && (
                                <div className="voice-status" aria-live="polite">
                                    {isListening && (
                                        <div className="status-chip listening">
                                            <span className="bars" aria-hidden="true">
                                                <span />
                                                <span />
                                                <span />
                                            </span>
                                            Mic is active...
                                        </div>
                                    )}
                                    {isSpeaking && (
                                        <div className="status-chip speaking">
                                            <span className="bars" aria-hidden="true">
                                                <span />
                                                <span />
                                                <span />
                                            </span>
                                            Voice playback is active...
                                        </div>
                                    )}
                                </div>
                            )}
                        </form>
                    </section>
                )}
            </main>
        </div>
    );

    function handleLogin(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setAuthError('');

        if (!username.trim() || !password.trim()) {
            setAuthError('Please enter username and password.');
            return;
        }

        if (username !== appConfig.auth.username || password !== appConfig.auth.password) {
            setAuthError('Invalid credentials. Try the demo login hint.');
            return;
        }

        sessionStorage.setItem(authStorageKey, 'true');
        setIsAuthenticated(true);
        setUsername('');
        setPassword('');
    }

    function handleLogout() {
        sessionStorage.removeItem(authStorageKey);
        setIsAuthenticated(false);
        setMessages([]);
        setInput('');
        setError('');
        setIsListening(false);
        setIsSpeaking(false);
        speechRecognitionRef.current?.stop();
        if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    }

    function addMessage(role: ChatMessage['role'], content: string) {
        const message: ChatMessage = {
            id: crypto.randomUUID(),
            role,
            content,
            timestamp: Date.now(),
        };

        setMessages(previous => [...previous, message]);
    }

    async function handleSend(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        const prompt = input.trim();
        if (!prompt) {
            return;
        }

        setError('');
        setInput('');
        addMessage('user', prompt);

        const endpoint = appConfig.api.endpoint.trim();
        const apiToken = appConfig.api.apiKey.trim();

        if (!endpoint.trim()) {
            setError('Endpoint is missing. Update src/config.ts with your AWS API URL.');
            addMessage('assistant', 'I cannot send this request because endpoint configuration is missing.');
            return;
        }

        setIsSending(true);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(apiToken.trim() ? { Authorization: `Bearer ${apiToken.trim()}` } : {}),
                },
                body: JSON.stringify({
                    message: prompt,
                    history: messages.map(message => ({ role: message.role, content: message.content })),
                }),
            });

            if (!response.ok) {
                let details = '';
                try {
                    const errorPayload = await response.json();
                    details =
                        (typeof errorPayload.message === 'string' && errorPayload.message) ||
                        (typeof errorPayload.error === 'string' && errorPayload.error) ||
                        '';
                } catch {
                    details = '';
                }

                const statusDetails = details ? `: ${details}` : '';
                throw new Error(`Request failed (${response.status})${statusDetails}`);
            }

            const payload = await response.json();
            const assistantText =
                (typeof payload.reply === 'string' && payload.reply) ||
                (typeof payload.message === 'string' && payload.message) ||
                (typeof payload.output === 'string' && payload.output) ||
                'Response received. Map your API response field to display it here.';

            addMessage('assistant', assistantText);
        } catch (requestError) {
            const errorMessage =
                requestError instanceof Error
                    ? requestError.message
                    : 'Failed to reach endpoint. Confirm CORS, URL, and credentials.';

            setError(errorMessage);
            addMessage('assistant', 'I could not connect to the configured endpoint.');
        } finally {
            setIsSending(false);
        }
    }

    function toggleSpeechToText() {
        if (!speechToTextSupported) {
            setError('Speech-to-text is not supported in this browser.');
            return;
        }

        if (isListening) {
            speechRecognitionRef.current?.stop();
            setIsListening(false);
            return;
        }

        const recognition = new speechRecognitionCtor();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = event => {
            let transcript = '';
            for (let i = 0; i < event.results.length; i += 1) {
                const result = event.results[i];
                transcript += result[0].transcript;
            }
            setInput(transcript.trim());
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        recognition.onerror = () => {
            setIsListening(false);
            setError('Microphone input failed. Check browser permissions.');
        };

        recognition.start();
        speechRecognitionRef.current = recognition;
        setIsListening(true);
    }

    function speakMessage(text: string) {
        if (!textToSpeechSupported || !text) {
            return;
        }

        setIsSpeaking(false);
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.onstart = () => {
            setIsSpeaking(true);
        };
        utterance.onend = () => {
            setIsSpeaking(false);
        };
        utterance.onerror = () => {
            setIsSpeaking(false);
            setError('Text-to-speech playback failed in this browser.');
        };
        window.speechSynthesis.speak(utterance);
    }
}

export default App;