import React from 'react';
import './PrintDocumentTemplate.css';

interface DocumentInfo {
  documentName: string;
  documentNumber: string;
  formatNumber: string;
  pageNumber: string;
  issueNumber: string;
  revisionNumber: string;
  issueDate: string;
  revisionDate: string;
  approvedBy?: string;
  reviewedBy?: string;
}

interface PrintDocumentTemplateProps {
  documentInfo: DocumentInfo;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  companyLogo?: string;
  companyName?: string;
  companyTagline?: string;
  classification?: 'CONFIDENTIAL' | 'INTERNAL' | 'PUBLIC';
}

const PrintDocumentTemplate: React.FC<PrintDocumentTemplateProps> = ({
  documentInfo,
  title,
  subtitle,
  children,
  companyLogo,
  companyName = "PROZEAL GREEN ENERGY PVT LTD",
  companyTagline = "An initiative towards a cleaner tomorrow",
  classification = 'INTERNAL'
}) => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || '';
  const baseFromApi = apiBase ? apiBase.replace(/\/api\/?.*$/, '') : '';
  const logoCandidates = [
    companyLogo,
    baseFromApi ? `${baseFromApi}/media/company_logos/PROZEAL_GREEN_ENERGY_TM_LOGO.png` : '/media/company_logos/PROZEAL_GREEN_ENERGY_TM_LOGO.png',
    baseFromApi ? `${baseFromApi}/media/company_logos/Prozeal_Logo.png` : '/media/company_logos/Prozeal_Logo.png',
    baseFromApi ? `${baseFromApi}/logo.png` : '/logo.png'
  ].filter(Boolean) as string[];
  const logoSrc = logoCandidates[0];

  return (
    <div className="print-document">
      {/* Print Header */}
      <div className="print-header">
        <table className="header-table">
          <tr>
            <td className="logo-section">
              <img
                src={logoSrc}
                alt="Company Logo"
                className="company-logo"
                onError={(event) => {
                  const target = event.currentTarget as HTMLImageElement;
                  const currentIndex = Number(target.dataset.logoIndex || '0');
                  const nextIndex = currentIndex + 1;
                  if (nextIndex < logoCandidates.length) {
                    target.dataset.logoIndex = String(nextIndex);
                    target.src = logoCandidates[nextIndex];
                  } else {
                    target.style.display = 'none';
                  }
                }}
                data-logo-index="0"
              />
            </td>
            <td className="company-section">
              <div className="company-name">{companyName}</div>
              <div className="company-tagline">{companyTagline}</div>
              <div className="document-title">{title}</div>
              {subtitle && <div className="document-subtitle">{subtitle}</div>}
            </td>
            <td className="info-section">
              <table className="document-info-table">
                <tr><td className="info-label">Doc No.:</td><td className="info-value">{documentInfo.documentNumber}</td></tr>
                <tr><td className="info-label">Rev.:</td><td className="info-value">{documentInfo.revisionNumber}</td></tr>
                <tr><td className="info-label">Date:</td><td className="info-value">{documentInfo.issueDate}</td></tr>
                <tr><td className="info-label">Page:</td><td className="info-value">{documentInfo.pageNumber}</td></tr>
              </table>
            </td>
          </tr>
        </table>
        
        {/* Classification Banner */}
        <div className={`classification-banner ${classification.toLowerCase()}`}>
          {classification}
        </div>
      </div>

      {/* Document Content */}
      <div className="print-content">
        {children}
      </div>

      {/* Print Footer */}
      <div className="print-footer">
        <div className="footer-left">
          <span className="document-number">{documentInfo.documentNumber}</span>
          <span className="revision">Rev. {documentInfo.revisionNumber}</span>
        </div>
        <div className="footer-center">
          Page {documentInfo.pageNumber}
        </div>
        <div className="footer-right">
          <span className="issue-date">{documentInfo.issueDate}</span>
        </div>
      </div>
    </div>
  );
};

export default PrintDocumentTemplate;
