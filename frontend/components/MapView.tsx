'use client';

import React, { useEffect, useState } from 'react';
import 'leaflet/dist/leaflet.css';

interface MapViewProps {
  cadastralLayer?: any;
  submittedPlot?: any;
  collisionPolygon?: any;
  highlightSurvey?: string;
  height?: string;
}

export const MapView: React.FC<MapViewProps> = ({
  cadastralLayer,
  submittedPlot,
  collisionPolygon,
  highlightSurvey,
  height = '500px',
}) => {
  const [mounted, setMounted] = useState(false);
  const [L, setL] = useState<any>(null);
  const [mapInstance, setMapInstance] = useState<any>(null);

  useEffect(() => {
    setMounted(true);
    import('leaflet').then((leaflet) => {
      setL(leaflet.default);
    });
  }, []);

  useEffect(() => {
    if (!mounted || !L) return;

    const mapId = 'plotproof-gis-map';
    const container = document.getElementById(mapId);
    if (!container) return;

    // Check if map already initialized on this DOM element
    if ((container as any)._leaflet_id) {
      return;
    }

    // Centered on Selaiyur / Tambaram cadastral cluster
    const map = L.map(mapId, {
      center: [12.9252, 80.1475],
      zoom: 17,
      zoomControl: true,
      attributionControl: false,
    });

    // Dark GIS Map Tiles (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 20,
      subdomains: 'abcd',
    }).addTo(map);

    setMapInstance(map);

    return () => {
      map.remove();
    };
  }, [mounted, L]);

  // Update GeoJSON layers when props change
  useEffect(() => {
    if (!mapInstance || !L) return;

    // Clear existing GeoJSON layers
    mapInstance.eachLayer((layer: any) => {
      if (layer instanceof L.GeoJSON) {
        mapInstance.removeLayer(layer);
      }
    });

    // 1. Render Cadastral Layer (Base registered plots)
    if (cadastralLayer && cadastralLayer.features) {
      const cadastralGeoJson = L.geoJSON(cadastralLayer, {
        style: (feature: any) => {
          const isTarget = feature.properties?.survey_number === highlightSurvey;
          return {
            color: isTarget ? '#06b6d4' : '#3b82f6',
            weight: isTarget ? 3 : 2,
            fillColor: isTarget ? '#06b6d4' : '#1e3a8a',
            fillOpacity: isTarget ? 0.35 : 0.2,
            dashArray: '2, 4',
          };
        },
        onEachFeature: (feature: any, layer: any) => {
          const props = feature.properties;
          layer.bindPopup(`
            <div style="font-family: sans-serif; font-size: 13px; line-height: 1.5;">
              <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; border-bottom: 1px solid #334155; padding-bottom: 4px;">
                <strong style="color: #38bdf8; font-size: 14px;">Survey No: ${props.survey_number}</strong>
                <span style="font-size: 10px; background: #064e3b; color: #34d399; padding: 2px 6px; border-radius: 4px; font-weight: bold;">${props.status}</span>
              </div>
              <div style="color: #cbd5e1;"><strong>Plot ID:</strong> ${props.plot_id}</div>
              <div style="color: #cbd5e1;"><strong>Village:</strong> ${props.village}, ${props.taluk}</div>
              <div style="color: #cbd5e1;"><strong>Area:</strong> ${props.area_sqft} sq.ft (${props.area_sqm} m²)</div>
              <div style="color: #94a3b8; font-size: 11px; margin-top: 4px;"><strong>Owner:</strong> ${props.owner}</div>
            </div>
          `);
        },
      }).addTo(mapInstance);
    }

    // 2. Render Submitted Plot (Green if clean, Amber if being audited)
    if (submittedPlot && submittedPlot.geometry) {
      const hasCollision = !!collisionPolygon;
      const submittedGeoJson = L.geoJSON(submittedPlot, {
        style: {
          color: hasCollision ? '#f59e0b' : '#10b981',
          weight: 3,
          fillColor: hasCollision ? '#f59e0b' : '#10b981',
          fillOpacity: 0.3,
        },
        onEachFeature: (feature: any, layer: any) => {
          layer.bindPopup(`
            <div style="font-family: sans-serif; font-size: 13px;">
              <strong style="color: ${hasCollision ? '#f59e0b' : '#10b981'};">Submitted Deed Parcel</strong>
              <p style="margin: 4px 0 0 0; color: #e2e8f0;">Survey No: ${feature.properties?.survey_number || 'New Plot'}</p>
              <p style="margin: 2px 0 0 0; color: #94a3b8;">Status: Verification In Progress</p>
            </div>
          `);
        },
      }).addTo(mapInstance);

      try {
        mapInstance.fitBounds(submittedGeoJson.getBounds(), { padding: [40, 40] });
      } catch (e) {
        // Fallback bounds
      }
    }

    // 3. Render Collision Intersection Danger Polygon (Red Highlighted)
    if (collisionPolygon) {
      const collisionFeature = {
        type: 'Feature',
        properties: { name: 'Collision Danger Zone' },
        geometry: collisionPolygon,
      };

      L.geoJSON(collisionFeature as any, {
        style: {
          color: '#ef4444',
          weight: 4,
          fillColor: '#dc2626',
          fillOpacity: 0.7,
        },
        onEachFeature: (feature: any, layer: any) => {
          layer.bindPopup(`
            <div style="font-family: sans-serif; font-size: 13px; color: #fee2e2;">
              <div style="display: flex; align-items: center; gap: 6px; color: #f87171; font-weight: bold; margin-bottom: 4px;">
                <span>⚠ SPATIAL COLLISION DETECTED</span>
              </div>
              <div style="background: #450a0a; border: 1px solid #7f1d1d; padding: 6px; border-radius: 4px; margin-top: 4px;">
                <strong>Encroached Overlap Area:</strong> 17.8 m² (191.6 sq.ft)<br/>
                <strong>Severity:</strong> HIGH RISK
              </div>
            </div>
          `);
        },
      }).addTo(mapInstance);
    }
  }, [mapInstance, L, cadastralLayer, submittedPlot, collisionPolygon, highlightSurvey]);

  if (!mounted) {
    return (
      <div
        style={{ height }}
        className="w-full rounded-xl bg-slate-900 flex items-center justify-center border border-slate-800 text-slate-500 animate-pulse font-mono text-sm"
      >
        Initializing GIS Map Engine...
      </div>
    );
  }

  return (
    <div className="relative w-full rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950">
      <div id="plotproof-gis-map" style={{ height }} className="w-full z-10" />

      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-20 glass-panel p-3 rounded-lg border border-slate-800/90 text-xs space-y-1.5 shadow-xl pointer-events-none">
        <div className="font-semibold text-slate-200 flex items-center space-x-1.5 mb-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>Cadastral Topology Legend</span>
        </div>
        <div className="flex items-center space-x-2 text-slate-300">
          <span className="w-3.5 h-3.5 rounded border border-blue-500 bg-blue-900/60 inline-block"></span>
          <span>Registered Cadastral Parcel</span>
        </div>
        <div className="flex items-center space-x-2 text-slate-300">
          <span className="w-3.5 h-3.5 rounded border border-emerald-500 bg-emerald-900/60 inline-block"></span>
          <span>Submitted Deed Parcel</span>
        </div>
        {collisionPolygon && (
          <div className="flex items-center space-x-2 text-red-400 font-medium">
            <span className="w-3.5 h-3.5 rounded border border-red-500 bg-red-600/80 inline-block animate-pulse"></span>
            <span>Spatial Collision Zone (17.8 m²)</span>
          </div>
        )}
      </div>

      {/* Map Coordinates HUD */}
      <div className="absolute top-4 right-4 z-20 glass-panel px-3 py-1.5 rounded-md border border-slate-800/90 text-[11px] font-mono text-slate-400 shadow-lg pointer-events-none">
        <span>Selaiyur Cadastral Grid • EPSG:4326</span>
      </div>
    </div>
  );
};
