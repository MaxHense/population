import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvent } from 'react-leaflet';
import type { LatLngExpression, LeafletMouseEvent } from 'leaflet';
import 'leaflet/dist/leaflet.css';

const center: LatLngExpression = [51.255583, 10.352611];

function ClickMarkers({ clearSignal }: { clearSignal: boolean }) {
  const [positions, setPositions] = useState<LatLngExpression[]>([]);

  useMapEvent('click', (e: LeafletMouseEvent) => {
    setPositions((prev) => {
      const updated = [...prev, e.latlng];
      console.log(updated);
      return updated;
    });
  });

  useEffect(() => {
    if (clearSignal) {
      setPositions([]);
    }
  }, [clearSignal]);

  return (
    <>
      {positions.map((pos, idx) => (
        <Marker key={idx} position={pos} />
      ))}
    </>
  );
}

import { useState as useReactState } from 'react';

function GermanyMap() {
  const [clearSignal, setClearSignal] = useReactState(false);

  const handleClear = () => {
    setClearSignal(true);
    // Reset clearSignal to false after clearing so it can be triggered again
    setTimeout(() => setClearSignal(false), 0);
  };

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <button
        onClick={handleClear}
        style={{
          position: 'absolute',
          zIndex: 1000,
          top: 20,
          right: 20,
          padding: '8px 16px',
          background: '#fff',
          border: '1px solid #ccc',
          borderRadius: 4,
          cursor: 'pointer',
        }}
      >
        Clear Markers
      </button>
      <MapContainer center={center} zoom={6} style={{ width: '100%', height: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ClickMarkers clearSignal={clearSignal} />
      </MapContainer>
    </div>
  );
}

export default GermanyMap;