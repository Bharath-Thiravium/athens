import React from 'react';
import './DigitalSignature.css';

interface DigitalSignatureProps {
  signerName: string;
  employeeId?: string;
  designation?: string;
  department?: string;
  signedAt?: string; // ISO string
  companyLogoUrl?: string;
  signatureImageUrl?: string;
  signatureImageData?: string;
}

/**
 * Standardized Adobe-like signature block component
 * Used across all modules for consistent signature appearance
 */
const DigitalSignature: React.FC<DigitalSignatureProps> = ({
  signerName,
  employeeId,
  designation,
  department,
  signedAt,
  companyLogoUrl,
  signatureImageUrl,
  signatureImageData
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
      const dayPeriod = get('dayPeriod') || ''; // AM/PM (best effort)

      const core = `${day} ${month} ${year}, ${hour}:${minute} ${dayPeriod}`.trim();
      return core ? `${core} IST` : `${isoString} IST`;
    } catch {
      return isoString;
    }
  };

  // Get signature image source with precedence
  const getSignatureImageSrc = () => {
    if (signatureImageUrl) return signatureImageUrl;
    if (signatureImageData) {
      return signatureImageData.startsWith('data:') 
        ? signatureImageData 
        : `data:image/png;base64,${signatureImageData}`;
    }
    return null;
  };

  const signatureImageSrc = getSignatureImageSrc();

  return (
    <div className="digital-signature-container">
      <div className="signature-content">
        {/* Company logo watermark at 50% opacity */}
        {companyLogoUrl && (
          <img className="signature-logo-watermark" src={companyLogoUrl} alt="" />
        )}
        
        {/* Left partition - Identity */}
        <div className="signature-left-partition">
          <div className="signer-name">{signerName}</div>
          {employeeId && <div className="employee-id">ID: {employeeId}</div>}
          {designation && <div className="designation">{designation}</div>}
        </div>
        
        {/* Divider */}
        <div className="signature-divider"></div>
        
        {/* Right partition - Signing proof */}
        <div className="signature-right-partition">
          <div className="signed-by-text">Digitally signed by {signerName}</div>
          {department && <div className="department">{department}</div>}
          <div className="signed-at">{formatDateTime(signedAt)}</div>
        </div>
        
        {/* Signature image spanning both partitions */}
        {signatureImageSrc && (
          <div className="signature-image-area">
            <img src={signatureImageSrc} alt="Signature" className="signature-image" />
          </div>
        )}
      </div>
    </div>
  );
};

export default DigitalSignature;