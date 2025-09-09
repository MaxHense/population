import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvent } from 'react-leaflet';
import type { LatLngExpression, LeafletMouseEvent } from 'leaflet';
import 'leaflet/dist/leaflet.css';

type MapWithMarkersProps = {
  center: LatLngExpression;
  zoom?: number;
  clearSignal: boolean;
};

function isLatLngObject(obj: any): obj is { lat: number; lng: number } {
  return obj && typeof obj.lat === 'number' && typeof obj.lng === 'number';
}

function areLatLngEqual(a: LatLngExpression, b: LatLngExpression) {
  if (Array.isArray(a) && Array.isArray(b)) {
    return a[0] === b[0] && a[1] === b[1];
  }
  if (isLatLngObject(a) && isLatLngObject(b)) {
    return a.lat === b.lat && a.lng === b.lng;
  }
  return false;
}

function ClickMarkers({ clearSignal }: { clearSignal: boolean }) {
  const [positions, setPositions] = useState<{ pos: LatLngExpression }[]>([]);

  useMapEvent('click', (e: LeafletMouseEvent) => {
    setPositions((prev) => {
      const updated = [...prev, { pos: e.latlng }];
      console.log(updated);
      return updated;
    });
  });

  useEffect(() => {
    if (clearSignal) {
      setPositions([]);
    }
  }, [clearSignal]);

  const handleMarkerClick = (clickedPos: LatLngExpression) => {
    setPositions((prev) => prev.filter(({ pos }) => !(areLatLngEqual(pos, clickedPos))));
  };

  return (
    <>
      {positions.map(({ pos }, idx) => (
        <Marker
          key={idx}
          position={pos}
          eventHandlers={{
            click: () => handleMarkerClick(pos),
          }}
        />
      ))}
    </>
  );
}

export function MapWithMarkers({ center, zoom = 6, clearSignal }: MapWithMarkersProps) {
  return (
    <MapContainer center={center} zoom={zoom} style={{ width: '100%', height: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickMarkers clearSignal={clearSignal} />
    </MapContainer>
  );
}