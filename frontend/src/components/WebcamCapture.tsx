import React, { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';

const videoConstraints = {
    width: 720,
    height: 480,
    facingMode: "user"
};

interface WebcamCaptureProps {
    onCapture: (image: string | null) => void;
}

const WebcamCapture: React.FC<WebcamCaptureProps> = ({ onCapture }) => {
    const webcamRef = useRef<Webcam>(null);
    const [image, setImage] = useState<string | null>(null);

    const capture = useCallback(() => {
        const imageSrc = webcamRef.current?.getScreenshot();
        if (imageSrc) {
            setImage(imageSrc);
            onCapture(imageSrc);
        }
    }, [webcamRef, onCapture]);

    const retake = () => {
        setImage(null);
        onCapture(null);
    };

    return (
        <div className="webcam-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ border: '2px solid #333', borderRadius: '8px', overflow: 'hidden', marginBottom: '10px' }}>
                {image ? (
                    <img src={image} alt="Captured" />
                ) : (
                    <Webcam
                        audio={false}
                        height={480}
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        width={720}
                        videoConstraints={videoConstraints}
                    />
                )}
            </div>
            <div>
                {image ? (
                    <button onClick={retake} style={btnStyle}>Retake Photo</button>
                ) : (
                    <button onClick={capture} style={btnStyle}>Capture Photo</button>
                )}
            </div>
        </div>
    );
};

const btnStyle: React.CSSProperties = {
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    marginTop: '10px'
};

export default WebcamCapture;
