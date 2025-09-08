import { MapContainer, TileLayer, } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

function GermanyMap() {
    return (
        <div style={{ width: '100vw', height: '100vh' }}>
            <MapContainer
                center={[51.1657, 10.4515]}
                zoom={6}
                style={{ width: '100%', height: '100%' }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
            </MapContainer>
        </div>
    );
}

export default GermanyMap;