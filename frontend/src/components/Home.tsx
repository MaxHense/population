import { useState } from 'react';
import germany from '../assets/germany.svg';

function Home() {
    const [current, setCurrent] = useState(0);

    const handleGermanyClick = () => {
        alert('Germany clicked!');
        // You can add your custom logic here
    };

    const slides = [
        {
            content: (
                <button
                    onClick={handleGermanyClick}
                    style={{
                        width: '100vw',
                        height: '100vh',
                        padding: 0,
                        margin: 0,
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        display: 'block',
                    }}
                    aria-label="Germany"
                >
                    <img
                        src={germany}
                        alt="Germany"
                        style={{
                            width: '100vw',
                            height: '100vh',
                            objectFit: 'contain',
                            display: 'block',
                            margin: 0,
                            padding: 100,
                            background: 'transparent',
                        }}
                    />
                </button>
            ),
        },
        {
            content: (
                <div style={{ fontSize: 32, fontWeight: 'bold', color: '#000' }}>
                    Coming soon...
                </div>
            ),
        },
    ];

    const goLeft = () => setCurrent((prev) => (prev === 0 ? slides.length - 1 : prev - 1));
    const goRight = () => setCurrent((prev) => (prev === slides.length - 1 ? 0 : prev + 1));

    return (
        <div className="fixed inset-0 flex flex-col items-center justify-center min-h-screen min-w-screen bg-transparent py-8">
            <div className="relative flex items-center justify-center w-full h-full">
                <button
                    onClick={goLeft}
                    className="absolute left-8 top-1/2 -translate-y-1/2 bg-black/60 text-white rounded-full w-12 h-12 flex items-center justify-center z-10"
                    aria-label="Previous"
                >
                    &#8592;
                </button>
                <div className="flex items-center justify-center w-full h-full">
                    {slides[current].content}
                </div>
                <button
                    onClick={goRight}
                    className="absolute right-8 top-1/2 -translate-y-1/2 bg-black/60 text-white rounded-full w-12 h-12 flex items-center justify-center z-10"
                    aria-label="Next"
                >
                    &#8594;
                </button>
            </div>
            <div className="mt-8 flex gap-4 z-10">
                {slides.map((_, idx) => (
                    <span
                        key={idx}
                        className={`w-4 h-4 rounded-full border-2 border-white ${idx === current ? 'bg-white' : 'bg-transparent'}`}
                    />
                ))}
            </div>
        </div>
    );
}

export default Home;