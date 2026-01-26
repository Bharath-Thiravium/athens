import React, { forwardRef } from 'react';
import './DigitalSignatureBlock.css';

interface DigitalSignatureBlockProps {
  signerName: string;
  employeeId?: string;
  designation?: string;
  department?: string;
  companyName?: string;
  companyLogoUrl?: string;
  signedAt?: string;
  verificationToken?: string;
  signatureImageUrl?: string;
  signatureImageData?: string;
  isPreview?: boolean;
  className?: string;
}

const DigitalSignatureBlock = forwardRef<HTMLDivElement, DigitalSignatureBlockProps>((
  {
    signerName,
    employeeId,
    designation,
    department,
    companyName,
    companyLogoUrl,
    signedAt,
    verificationToken,
    signatureImageUrl,
    signatureImageData,
    isPreview = false,
    className = ''
  },
  ref
) => {

  const formatDateTime = (isoString?: string) => {
    if (!isoString) return '[TO_BE_FILLED]';
    if (isPreview) return '[PREVIEW]';
    
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
        timeZone: 'Asia/Kolkata'
      }) + ' IST';
    } catch {
      return '[INVALID_DATE]';
    }
  };

  // Determine signature image source with precedence
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
    <div className={`ds-card ${className}`} ref={ref}>
      {/* Watermark layer - absolutely positioned, removed from layout flow */}
      {companyLogoUrl && (
        <div className="ds-watermark-layer" aria-hidden="true">
          <img 
            className="ds-watermark"
            src={companyLogoUrl} 
            alt=""
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        </div>
      )}

      {/* Main content row - defines the box size */}
      <div className="ds-row">
        <div className="ds-col ds-left">
          <div className="ds-name">{signerName}</div>
          {employeeId && (
            <div className="ds-id">ID: {employeeId}</div>
          )}
          {designation && (
            <div className="ds-desig">{designation}</div>
          )}
        </div>

        <div className="ds-divider"></div>

        <div className="ds-col ds-right">
          <div className="ds-signedby">Digitally signed by</div>
          <div className="ds-signedby">{signerName}</div>
          {department && (
            <div className="ds-dept">{department}</div>
          )}
          {companyName && (
            <div className="ds-dept">{companyName}</div>
          )}
          <div className="ds-date">Date: {formatDateTime(signedAt)}</div>
          {verificationToken && verificationToken !== 'PREVIEW' && (
            <div className="ds-token">Token: {verificationToken}</div>
          )}
        </div>
      </div>

      {/* Handwritten signature row */}
      {signatureImageSrc && (
        <div className="ds-hand-row">
          <img 
            className="ds-hand-img"
            src={signatureImageSrc}
            alt="Handwritten Signature"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        </div>
      )}
    </div>
  );
});

export default DigitalSignatureBlock;