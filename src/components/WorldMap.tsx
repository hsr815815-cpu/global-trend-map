'use client';

import { useState, useCallback } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
  GeoFeature,
} from 'react-simple-maps';
import {
  TrendsData,
  CountryData,
  getMapFillColor,
  getCountryTemperature,
} from '@/lib/trend-utils';
import CountryPopup from './CountryPopup';

const GEO_URL =
  'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

const COUNTRY_CENTROIDS: Record<string, [number, number]> = {
  'US': [-95, 38], 'KR': [128, 36], 'JP': [138, 36], 'GB': [-2, 54],
  'DE': [10, 51], 'IN': [78, 22], 'BR': [-52, -10], 'FR': [2, 46],
  'AU': [133, -25], 'MX': [-102, 24], 'CA': [-95, 60], 'CN': [105, 35],
  'RU': [60, 60], 'IT': [12, 43], 'ES': [-4, 40], 'AR': [-64, -34],
  'ZA': [25, -29], 'NG': [8, 10], 'EG': [30, 27], 'TR': [35, 39],
  'SA': [45, 25], 'ID': [118, -2], 'PH': [122, 13], 'TH': [101, 15],
  'VN': [108, 16], 'PL': [20, 52], 'NL': [5, 52], 'SE': [18, 60],
  'NO': [10, 62], 'CH': [8, 47], 'AT': [14, 47], 'BE': [4, 51],
  'PT': [-8, 39], 'GR': [22, 39], 'CZ': [16, 50], 'HU': [19, 47],
  'RO': [25, 46], 'UA': [32, 49], 'MY': [110, 4], 'SG': [104, 1],
  'NZ': [172, -42], 'CO': [-74, 4], 'PE': [-76, -10], 'CL': [-71, -30],
  'IL': [35, 31], 'AE': [54, 24], 'QA': [51, 25], 'KW': [48, 29],
  'KE': [38, -1], 'ET': [40, 9], 'GH': [-1, 8],
  'DZ': [3, 28], 'MA': [-6, 32], 'PK': [70, 30], 'BD': [90, 24],
  'LK': [81, 8], 'MM': [96, 17], 'KH': [105, 12],
  'SK': [19, 48], 'FI': [26, 64], 'DK': [10, 56], 'IE': [-8, 53],
};

// ISO numeric → ISO alpha-2 mapping for major countries
const NUMERIC_TO_ALPHA2: Record<string, string> = {
  '840': 'US', '410': 'KR', '392': 'JP', '826': 'GB', '276': 'DE',
  '356': 'IN', '076': 'BR', '250': 'FR', '036': 'AU', '484': 'MX',
  '124': 'CA', '156': 'CN', '643': 'RU', '380': 'IT', '724': 'ES',
  '032': 'AR', '710': 'ZA', '566': 'NG', '818': 'EG', '792': 'TR',
  '682': 'SA', '360': 'ID', '608': 'PH', '764': 'TH', '704': 'VN',
  '616': 'PL', '528': 'NL', '752': 'SE', '578': 'NO', '756': 'CH',
  '040': 'AT', '056': 'BE', '620': 'PT', '300': 'GR', '203': 'CZ',
  '348': 'HU', '642': 'RO', '804': 'UA', '100': 'BG',
  '191': 'HR', '703': 'SK', '705': 'SI', '233': 'EE', '428': 'LV',
  '440': 'LT', '246': 'FI', '208': 'DK', '554': 'NZ', '458': 'MY',
  '702': 'SG', '144': 'LK', '050': 'BD', '586': 'PK', '404': 'KE',
  '231': 'ET', '288': 'GH', '012': 'DZ', '504': 'MA',
  '716': 'ZW', '800': 'UG', '834': 'TZ', '686': 'SN', '384': 'CI',
  '072': 'BW', '516': 'NA', '508': 'MZ', '024': 'AO', '180': 'CD',
  '204': 'BJ', '854': 'BF', '120': 'CM', '140': 'CF', '064': 'BT',
  '104': 'MM', '116': 'KH', '418': 'LA', '496': 'MN', '408': 'KP',
  '398': 'KZ', '860': 'UZ', '795': 'TM', '417': 'KG', '762': 'TJ',
  '031': 'AZ', '051': 'AM', '268': 'GE', '400': 'JO', '422': 'LB',
  '376': 'IL', '275': 'PS', '368': 'IQ', '364': 'IR', '760': 'SY',
  '887': 'YE', '512': 'OM', '784': 'AE', '634': 'QA', '048': 'BH',
  '414': 'KW', '096': 'BN', '626': 'TL', '090': 'SB', '598': 'PG',
  '242': 'FJ', '548': 'VU', '882': 'WS', '776': 'TO', '583': 'FM',
  '170': 'CO', '604': 'PE', '862': 'VE', '152': 'CL', '218': 'EC',
  '068': 'BO', '600': 'PY', '858': 'UY', '328': 'GY', '740': 'SR',
  '630': 'PR', '332': 'HT', '388': 'JM', '192': 'CU', '214': 'DO',
  '222': 'SV', '320': 'GT', '340': 'HN', '558': 'NI', '188': 'CR',
  '591': 'PA', '044': 'BS', '084': 'BZ',
};

interface PopupState {
  countryCode: string;
  countryData: CountryData;
  position: { x: number; y: number };
}

interface WorldMapProps {
  data: TrendsData;
}

export default function WorldMap({ data }: WorldMapProps) {
  const [popup, setPopup] = useState<PopupState | null>(null);
  const [hoveredCountry, setHoveredCountry] = useState<string | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [tooltipCountry, setTooltipCountry] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [center, setCenter] = useState<[number, number]>([0, 20]);

  const getAlpha2FromGeo = useCallback((geo: GeoFeature): string | null => {
    // Try ISO numeric first
    const numericId = geo.id || geo.properties?.['numeric-code'] || geo.properties?.iso_n3;
    if (numericId) {
      const alpha2 = NUMERIC_TO_ALPHA2[String(numericId).padStart(3, '0')];
      if (alpha2) return alpha2;
    }
    // Try ISO alpha-2
    const a2 = (geo.properties?.['iso_a2'] || geo.properties?.['ISO_A2']) as string | undefined;
    if (a2 && a2 !== '-99') return a2;
    // Try name lookup
    return null;
  }, []);

  const handleCountryClick = useCallback(
    (geo: GeoFeature, event: React.MouseEvent) => {
      const code = getAlpha2FromGeo(geo);
      if (!code) return;

      const countryData = data.countries[code];
      if (!countryData) return;

      setPopup({
        countryCode: code,
        countryData,
        position: { x: event.clientX, y: event.clientY },
      });
    },
    [data, getAlpha2FromGeo]
  );

  const handleMouseEnter = useCallback(
    (geo: GeoFeature, event: React.MouseEvent) => {
      const code = getAlpha2FromGeo(geo);
      setHoveredCountry(code);
      if (code) {
        const countryData = data.countries[code];
        const name = countryData?.name || (geo.properties?.name as string | undefined) || code;
        const temp = getCountryTemperature(data, code);
        setTooltipCountry(countryData ? `${countryData.flag} ${name} — ${temp}°T` : name);
        setTooltipPos({ x: event.clientX, y: event.clientY });
      }
    },
    [data, getAlpha2FromGeo]
  );

  const handleMouseLeave = useCallback(() => {
    setHoveredCountry(null);
    setTooltipCountry(null);
  }, []);

  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    setTooltipPos({ x: event.clientX, y: event.clientY });
  }, []);

  const getFillColor = useCallback(
    (geo: GeoFeature): string => {
      const code = getAlpha2FromGeo(geo);
      if (!code) return '#1a1a3a';

      const temp = getCountryTemperature(data, code);
      if (temp === 0) return '#1a1a3a';

      const isHovered = hoveredCountry === code;
      const baseColor = getMapFillColor(temp);

      if (isHovered) return '#818cf8';
      return baseColor;
    },
    [data, hoveredCountry, getAlpha2FromGeo]
  );

  const getStrokeColor = useCallback(
    (geo: GeoFeature): string => {
      const code = getAlpha2FromGeo(geo);
      if (code && hoveredCountry === code) return '#a78bfa';
      if (code && data.countries[code]) return '#2d2d5a';
      return '#1e1e3f';
    },
    [data, hoveredCountry, getAlpha2FromGeo]
  );

  const zoomIn = () => setZoom((z) => Math.min(z * 1.5, 8));
  const zoomOut = () => setZoom((z) => Math.max(z / 1.5, 1));
  const resetView = () => { setZoom(1); setCenter([0, 20]); };

  return (
    <div
      style={{
        height: '100%',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '16px',
        overflow: 'hidden',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
      }}
      onMouseMove={handleMouseMove}
    >
      {/* Map header */}
      <div className="panel-header" style={{ flexShrink: 0 }}>
        <span className="panel-title">World Trend Map</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Legend */}
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            {[
              { color: '#1e3a5f', label: 'Cool' },
              { color: '#1d4ed8', label: 'Warm' },
              { color: '#7c3aed', label: 'Hot' },
              { color: '#ea580c', label: 'Fire' },
            ].map((item) => (
              <div
                key={item.label}
                style={{ display: 'flex', alignItems: 'center', gap: '3px' }}
              >
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '2px',
                    background: item.color,
                  }}
                />
                <span style={{ fontSize: '9px', color: 'var(--text-muted)' }}>
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Map */}
      <div style={{ flex: 1, position: 'relative' }}>
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{
            scale: 140,
          }}
          style={{ width: '100%', height: '100%', background: 'transparent' }}
        >
          <ZoomableGroup
            zoom={zoom}
            center={center}
            onMoveEnd={({ coordinates, zoom: z }) => {
              setCenter(coordinates);
              setZoom(z);
            }}
            filterZoomEvent={() => {
              return true;
            }}
          >
            {/* Ocean background */}
            <rect x="-1000" y="-1000" width="3000" height="3000" fill="#08081a" />

            <Geographies geography={GEO_URL}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const fillColor = getFillColor(geo);
                  const strokeColor = getStrokeColor(geo);
                  const code = getAlpha2FromGeo(geo);
                  const hasData = code ? !!data.countries[code] : false;

                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      onClick={(e: React.MouseEvent) => handleCountryClick(geo, e)}
                      onMouseEnter={(e: React.MouseEvent) => handleMouseEnter(geo, e)}
                      onMouseLeave={handleMouseLeave}
                      style={{
                        default: {
                          fill: fillColor,
                          stroke: strokeColor,
                          strokeWidth: 0.5,
                          outline: 'none',
                          cursor: hasData ? 'pointer' : 'default',
                        },
                        hover: {
                          fill: hasData ? '#818cf8' : fillColor,
                          stroke: hasData ? '#a78bfa' : strokeColor,
                          strokeWidth: 0.8,
                          outline: 'none',
                          cursor: hasData ? 'pointer' : 'default',
                        },
                        pressed: {
                          fill: '#6366f1',
                          stroke: '#818cf8',
                          strokeWidth: 0.8,
                          outline: 'none',
                        },
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>

        {/* Zoom controls */}
        <div
          style={{
            position: 'absolute',
            bottom: '16px',
            right: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px',
            zIndex: 10,
          }}
        >
          {[
            { label: '+', action: zoomIn, title: 'Zoom in' },
            { label: '−', action: zoomOut, title: 'Zoom out' },
            { label: '⌂', action: resetView, title: 'Reset view' },
          ].map((btn) => (
            <button
              key={btn.label}
              onClick={btn.action}
              title={btn.title}
              style={{
                width: '30px',
                height: '30px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-normal)',
                borderRadius: '8px',
                color: 'var(--text-secondary)',
                fontSize: '14px',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {btn.label}
            </button>
          ))}
        </div>

        {/* Hot countries pulse indicator */}
        <div
          style={{
            position: 'absolute',
            bottom: '16px',
            left: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '11px',
            color: 'var(--text-muted)',
          }}
        >
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#ea580c',
              boxShadow: '0 0 8px #ea580c',
              animation: 'pulse-dot 2s ease-in-out infinite',
            }}
          />
          Click a country for details
        </div>

        {/* Scroll indicator */}
        <div className="scroll-indicator">
          <div className="scroll-indicator-arrow">↓</div>
          <span>Scroll for more</span>
        </div>
      </div>

      {/* Tooltip */}
      {tooltipCountry && (
        <div
          style={{
            position: 'fixed',
            left: tooltipPos.x + 12,
            top: tooltipPos.y - 36,
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-normal)',
            borderRadius: '8px',
            padding: '6px 10px',
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            pointerEvents: 'none',
            zIndex: 998,
            whiteSpace: 'nowrap',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
          }}
        >
          {tooltipCountry}
        </div>
      )}

      {/* Country popup */}
      {popup && (
        <CountryPopup
          countryCode={popup.countryCode}
          countryData={popup.countryData}
          position={popup.position}
          onClose={() => setPopup(null)}
        />
      )}
    </div>
  );
}
