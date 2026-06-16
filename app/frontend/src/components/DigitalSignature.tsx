import React from 'react';
import './DigitalSignature.css';

interface DigitalSignatureProps {
  signerName: string;
  employeeId?: string;
  designation?: string;
  department?: string;
  signedAt?: string; // ISO string
  companyLogoUrl?: string;
  signaturePayload?: any; // JSON strokes
  mode?: 'view' | 'placeholder';
}

/**
 * Digital Signature Standard v1 (JSON-only)
 * Adobe-like signature block with JSON stroke rendering
 * NEVER renders <img> for signatures - only SVG from JSON strokes
 */
const DigitalSignature: React.FC<DigitalSignatureProps> = ({
  signerName,
  employeeId,
  designation,
  department,
  signedAt,
  companyLogoUrl,
  signaturePayload,
  mode = 'view'
}) => {
  const formatDateTime = (isoString?: string) => {
    if (!isoString) return 'N/A';

    try {
      const date = new Date(isoString);
      if (Number.isNaN(date.getTime())) return isoString;

      const formatter = new Intl.DateTimeFormat('en-IN', {
        timeZone: 'Asia/Kolkata',
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });

      const parts = formatter.formatToParts(date);
      const get = (type: Intl.DateTimeFormatPartTypes) =>
        parts.find(p => p.type === type)?.value ?? '';

      const day = get('day');
      const month = get('month');
      const year = get('year');
      const hour = get('hour');
      const minute = get('minute');
      const dayPeriod = get('dayPeriod') || '';

      const core = `${day} ${month} ${year}, ${hour}:${minute} ${dayPeriod}`.trim();
      return core ? `${core} IST` : `${isoString} IST`;
    } catch {
      return isoString;
    }
  };

  // Render signature strokes from JSON into SVG
  const renderSignatureStrokes = () => {
    if (!signaturePayload || !signaturePayload.strokes || !Array.isArray(signaturePayload.strokes)) {
      return null;
    }

    const { width = 300, height = 100, strokes } = signaturePayload;
    const viewBoxWidth = Math.max(width, 300);
    const viewBoxHeight = Math.max(height, 100);

    return (
      <svg 
        className="signature-strokes" 
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        preserveAspectRatio="xMidYMid meet"
      >
        {strokes.map((stroke: any, index: number) => {
          if (!stroke.points || !Array.isArray(stroke.points)) return null;
          
          const pathData = stroke.points.reduce((path: string, point: any, i: number) => {
            const x = point.x || 0;
            const y = point.y || 0;
            return path + (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
          }, '');

          return (
            <path
              key={index}
              d={pathData}
              stroke={stroke.color || '#000'}
              strokeWidth={stroke.width || 2}
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          );
        })}
      </svg>
    );
  };

  if (mode === 'placeholder') {
    return (
      <div className="ds-card">
        <div className="ds-watermark-layer">
          {companyLogoUrl && (
            <img className="ds-watermark" src={companyLogoUrl} alt="" />
          )}
        </div>
        <div className="ds-content" style={{ zIndex: 1 }}>
          <div className="ds-left-partition">
            <div className="ds-signer-name">{signerName}</div>
            <div className="ds-designation">Awaiting signature</div>
          </div>
          <div className="ds-divider"></div>
          <div className="ds-right-partition">
            <div className="ds-signed-by">Awaiting signature</div>
            <div className="ds-signed-at">Date: —</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ds-card">
      <div className="ds-watermark-layer">
        {companyLogoUrl && (
          <img className="ds-watermark" src={companyLogoUrl} alt="" />
        )}
      </div>
      <div className="ds-content" style={{ zIndex: 1 }}>
        {/* Left partition - Identity */}
        <div className="ds-left-partition">
          <div className="ds-signer-name">{signerName}</div>
          {employeeId && <div className="ds-employee-id">ID: {employeeId}</div>}
          {designation && <div className="ds-designation">{designation}</div>}
        </div>
        
        {/* Divider */}
        <div className="ds-divider"></div>
        
        {/* Right partition - Signing proof */}
        <div className="ds-right-partition">
          <div className="ds-signed-by">Digitally signed by {signerName}</div>
          {department && <div className="ds-department">{department}</div>}
          <div className="ds-signed-at">{formatDateTime(signedAt)}</div>
        </div>
        
        {/* Signature strokes area */}
        {signaturePayload && (
          <div className="ds-signature-area">
            {renderSignatureStrokes()}
          </div>
        )}
      </div>
    </div>
  );
};

export default DigitalSignature;