import { useState, useEffect } from 'react'
import './App.css'
import WebcamCapture from './components/WebcamCapture'
import { registerUser, verifyUser } from './api'

function App() {
    const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
    const [userId, setUserId] = useState('');
    const [capturedImage, setCapturedImage] = useState<string | null>(null);
    const [status, setStatus] = useState('');
    const [loading, setLoading] = useState(false);
    const [deviceInfo, setDeviceInfo] = useState<string>('');

    useEffect(() => {
        const getDevices = async () => {
            try {
                // Request permission first or assume it's granted by Webcam component? 
                // Enumerating without permission often gives empty labels.
                // We'll rely on the user granting permission when the webcam starts.
                // So maybe run this when capturing or just poll.
                // Simple approach: Try to enumerate. If labels empty, maybe retry later?
                // Actually, WebcamCapture loads immediately. 
                // Let's just try to get it.

                // Note: enumerateDevices() might return empty labels if permission not yet granted.
                // Ideally we hook into when Webcam is ready, but WebcamCapture component doesn't expose that event up easily.
                // We'll try to fetch it after a short delay or just call it.
                const devices = await navigator.mediaDevices.enumerateDevices();
                const videoDevices = devices.filter(device => device.kind === 'videoinput');
                if (videoDevices.length > 0) {
                    // Just grab the first one or formatted list
                    const labels = videoDevices.map(d => d.label || 'Unknown Camera').join(', ');
                    setDeviceInfo(`${labels} | ${navigator.userAgent}`);
                } else {
                    setDeviceInfo(navigator.userAgent);
                }
            } catch (e) {
                console.error("Error getting devices", e);
                setDeviceInfo(navigator.userAgent);
            }
        };

        // Call it.
        getDevices();
    }, []);

    const handleCapture = (image: string | null) => {
        setCapturedImage(image);
        setStatus('');
    };

    const handleRegister = async () => {
        if (!userId || !capturedImage) {
            setStatus('Please enter User ID and capture a photo.');
            return;
        }
        setLoading(true);
        try {
            const res = await registerUser(userId, capturedImage, deviceInfo);
            setStatus(`Success: ${res.message}`);
        } catch (err: any) {
            setStatus(`Error: ${err.detail || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleLogin = async () => {
        if (!capturedImage) {
            setStatus('Please capture a photo first.');
            return;
        }
        setLoading(true);
        try {
            const res = await verifyUser(capturedImage);
            if (res.success) {
                setStatus(`Welcome back! User: ${res.data.user_id} (Dist: ${res.data.distance.toFixed(4)})`);
            } else {
                setStatus(`Login Failed: ${res.message}`);
            }
        } catch (err: any) {
            setStatus(`Error: ${err.detail || err.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Facial Recognition Auth</h1>

            <div className="tabs" style={{ marginBottom: '20px' }}>
                <button
                    onClick={() => { setActiveTab('login'); setStatus(''); setCapturedImage(null); }}
                    style={{ ...tabStyle, backgroundColor: activeTab === 'login' ? '#007bff' : '#ccc' }}
                >
                    Login
                </button>
                <button
                    onClick={() => { setActiveTab('register'); setStatus(''); setCapturedImage(null); }}
                    style={{ ...tabStyle, backgroundColor: activeTab === 'register' ? '#007bff' : '#ccc' }}
                >
                    Register
                </button>
            </div>

            <div className="content">
                {activeTab === 'register' && (
                    <div style={{ marginBottom: '15px' }}>
                        <input
                            type="text"
                            placeholder="Enter User ID"
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                            style={inputStyle}
                        />
                    </div>
                )}

                <WebcamCapture onCapture={handleCapture} />

                <div style={{ marginTop: '20px' }}>
                    {activeTab === 'register' ? (
                        <button
                            onClick={handleRegister}
                            disabled={loading || !capturedImage}
                            style={{ ...actionBtnStyle, opacity: (loading || !capturedImage) ? 0.6 : 1 }}
                        >
                            {loading ? 'Registering...' : 'Register User'}
                        </button>
                    ) : (
                        <button
                            onClick={handleLogin}
                            disabled={loading || !capturedImage}
                            style={{ ...actionBtnStyle, opacity: (loading || !capturedImage) ? 0.6 : 1 }}
                        >
                            {loading ? 'Verifying...' : 'Login'}
                        </button>
                    )}
                </div>

                {status && (
                    <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
                        <strong>{status}</strong>
                    </div>
                )}
            </div>
        </div>
    )
}

const tabStyle: React.CSSProperties = {
    padding: '10px 20px',
    marginRight: '10px',
    border: 'none',
    borderRadius: '4px',
    color: 'white',
    cursor: 'pointer',
    fontSize: '16px'
};

const inputStyle: React.CSSProperties = {
    padding: '10px',
    fontSize: '16px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    width: '300px'
};

const actionBtnStyle: React.CSSProperties = {
    padding: '12px 24px',
    fontSize: '18px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer'
};

export default App
