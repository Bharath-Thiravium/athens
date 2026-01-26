import React, { useEffect, useMemo, useState } from 'react';
import { App, Button, Spin, Typography } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import dayjs from 'dayjs';
import { getPermit, getPermitIsolation, getPermitTbt } from '../api';
import * as Types from '../types';
import PrintDocumentTemplate from '../../../components/PrintDocumentTemplate';
import { getDocumentConfig } from '../../../constants/documentConfig';
import './PTWStandardPrint.css';

const { Title, Text } = Typography;

const PTWStandardPrint: React.FC = () => {
  const { message } = App.useApp();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [permit, setPermit] = useState<Types.Permit | null>(null);
  const [tbt, setTbt] = useState<Types.PermitToolboxTalkResponse | null>(null);
  const [isolation, setIsolation] = useState<Types.PermitIsolationResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      if (!id) return;
      setLoading(true);
      try {
        const permitResponse = await getPermit(parseInt(id));
        setPermit(permitResponse.data);

        try {
          const tbtResponse = await getPermitTbt(parseInt(id));
          setTbt(tbtResponse.data);
        } catch {
          setTbt(null);
        }

        try {
          const isolationResponse = await getPermitIsolation(parseInt(id));
          setIsolation(isolationResponse.data);
        } catch {
          setIsolation(null);
        }
      } catch (error: any) {
        message.error('Failed to load permit for print');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [id, message]);

  const documentInfo = useMemo(() => {
    if (!permit) return null;
    const category = permit.permit_type_details?.category || '';
    const configKey = category.includes('electrical') ? 'ELECTRICAL_WORK' : 'HOT_WORK';
    const docConfig = getDocumentConfig('PTW', configKey) || getDocumentConfig('PTW', 'HOT_WORK');
    if (!docConfig) return null;
    return {
      ...docConfig,
      pageNumber: '01 of 01'
    };
  }, [permit]);

  if (loading) {
    return (
      <div className="ptw-print-loading">
        <Spin size="large" />
      </div>
    );
  }

  if (!permit || !documentInfo) {
    return (
      <div className="ptw-print-error">
        <Text>Permit not found.</Text>
        <Button type="link" onClick={() => navigate('/dashboard/ptw')}>Back to permits</Button>
      </div>
    );
  }

  const formatDateOnly = (value?: string | null) => {
    if (!value) return '—';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '—';
    return date.toLocaleDateString('en-GB'); // DD/MM/YYYY format
  };

  const formatDateTime = (value?: string | null) => (
    value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '—'
  );

  const displayName = (user: any) => {
    if (!user) return '—';
    if (user.full_name) return user.full_name;
    const parts = [user.name, user.surname].filter(Boolean);
    if (parts.length > 0) return parts.join(' ');
    return user.username || user.email || '—';
  };

  const resolveSignatureSrc = (signatureData?: string | null) => {
    if (!signatureData) return null;
    const trimmed = signatureData.trim();
    
    // Handle data URL format (base64)
    if (trimmed.startsWith('data:image/png;base64,')) {
      try {
        // Extract base64 part and decode JSON
        const base64Data = trimmed.substring('data:image/png;base64,'.length);
        const decoded = atob(base64Data);
        const jsonData = JSON.parse(decoded);
        
        // If it's a JSON with template_url, use that
        if (jsonData.template_url) {
          return jsonData.template_url;
        }
      } catch (e) {
        // If JSON parsing fails, treat as regular data URL
      }
      return trimmed;
    }
    
    // Handle HTTP URLs
    if (trimmed.startsWith('http')) return trimmed;
    
    // Handle media paths
    if (trimmed.startsWith('/media/')) {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
      return `${baseUrl}${trimmed}`;
    }
    
    // Handle SVG content
    if (trimmed.startsWith('<svg')) {
      return `data:image/svg+xml;utf8,${encodeURIComponent(trimmed)}`;
    }
    
    // Assume base64 without prefix
    return `data:image/png;base64,${trimmed}`;
  };

  const isPrecomposedCard = (signatureData?: string | null) => {
    if (!signatureData) return false;
    const trimmed = signatureData.trim();
    
    if (trimmed.startsWith('data:image/png;base64,')) {
      try {
        const base64Data = trimmed.substring('data:image/png;base64,'.length);
        const decoded = atob(base64Data);
        const jsonData = JSON.parse(decoded);
        return !!jsonData.template_url; // Has template_url = precomposed card
      } catch (e) {
        // If JSON parsing fails, check if it's a large PNG (likely precomposed)
        return trimmed.length > 1000; // Large base64 = likely precomposed card
      }
    }
    
    return false;
  };

  const findSignatureByType = (signatures: any, type: string) => {
    if (!signatures) return null;
    
    // Check signatures_by_type first (preferred)
    if (signatures[type]) {
      const candidate = signatures[type];
      if (!candidate.signature_type || candidate.signature_type === type) {
        return candidate;
      }
    }
    
    // Fallback to searching signatures array
    if (Array.isArray(signatures)) {
      return signatures.find((sig: any) => sig.signature_type === type) || null;
    }
    
    return null;
  };

  const getSignatureRenderMode = (sig?: Types.DigitalSignature | null) => {
    if (!sig?.signature_render_mode) return 'card';
    return sig.signature_render_mode;
  };

  const checklistItems = (() => {
    const raw = permit.safety_checklist;
    if (Array.isArray(raw)) {
      return raw.map((item) => (typeof item === 'string' ? item : item?.label || item?.key || item?.text)).filter(Boolean);
    }
    if (raw && typeof raw === 'object') {
      return Object.entries(raw).map(([key, value]) => ({ key, checked: Boolean(value) }));
    }
    return [];
  })();

  const hazardList = Array.isArray(permit.identified_hazards)
    ? permit.identified_hazards.map((hazard) => hazard.hazard_details?.name || hazard.hazard_details?.hazard_id || 'Hazard')
    : [];
  const parameterHazards = Array.isArray(permit.permit_parameters?.risk_factors)
    ? permit.permit_parameters?.risk_factors
    : [];
  const hazards = Array.from(new Set([...hazardList, ...parameterHazards])).filter(Boolean);

  const controlMeasures = permit.control_measures
    ? permit.control_measures.split('\n').filter(Boolean)
    : [];

  const mandatoryPpe = permit.permit_type_details?.mandatory_ppe || [];
  const selectedPpe = Array.isArray(permit.ppe_requirements) ? permit.ppe_requirements : [];
  const allPpe = Array.from(new Set([...mandatoryPpe, ...selectedPpe]));

  const tbtAttendanceByWorker = new Map(
    (tbt?.attendance || []).map((entry) => [entry.permit_worker, entry])
  );

  const signatureMap = permit.signatures_by_type || {};
  const signatureLogo =
    signatureMap.requestor?.company_logo_url ||
    signatureMap.verifier?.company_logo_url ||
    signatureMap.approver?.company_logo_url;

  return (
    <div className="ptw-standard-print">
      <div className="ptw-print-actions no-print">
        <Button type="default" onClick={() => navigate(`/dashboard/ptw/view/${permit.id}`)}>
          Back to Permit
        </Button>
        <Button type="primary" onClick={() => window.print()}>
          Print
        </Button>
      </div>

      <PrintDocumentTemplate
        documentInfo={documentInfo}
        title="PERMIT TO WORK"
        subtitle={permit.permit_type_details?.name || 'Permit'}
        classification={documentInfo.classification}
        companyLogo={signatureLogo}
      >
        <section className="ptw-section">
          <Title level={4}>A. Permit Details</Title>
          <div className="ptw-grid">
            <div><strong>Permit No:</strong> {permit.permit_number}</div>
            <div><strong>Status:</strong> {permit.status}</div>
            <div><strong>Project:</strong> {permit.project?.projectName || permit.project?.name || '—'}</div>
            <div><strong>Location:</strong> {permit.location}</div>
            <div><strong>GPS:</strong> {permit.gps_coordinates || '—'}</div>
            <div><strong>Planned Start:</strong> {formatDateTime(permit.planned_start_time)}</div>
            <div><strong>Planned End:</strong> {formatDateTime(permit.planned_end_time)}</div>
            <div><strong>Actual Start:</strong> {formatDateTime(permit.actual_start_time)}</div>
            <div><strong>Actual End:</strong> {formatDateTime(permit.actual_end_time)}</div>
            <div><strong>Validity (hrs):</strong> {permit.permit_parameters?.validity_hours || permit.permit_type_details?.validity_hours || '—'}</div>
            <div><strong>Extensions:</strong> {Array.isArray(permit.extensions) ? permit.extensions.length : 0}</div>
          </div>
        </section>

        <section className="ptw-section">
          <Title level={4}>B. Work Description</Title>
          <div className="ptw-subsection"><strong>Title:</strong> {permit.title || '—'}</div>
          <div className="ptw-block">{permit.description || '—'}</div>
          <div className="ptw-subsection">
            <strong>Work Procedure:</strong> {permit.work_procedure ? 'Attached' : '—'}
          </div>
          <div className="ptw-subsection">
            <strong>Method Statement:</strong> {permit.method_statement ? 'Attached' : '—'}
          </div>
          <div className="ptw-subsection">
            <strong>Risk Assessment Document:</strong> {permit.risk_assessment_doc ? 'Attached' : '—'}
          </div>
        </section>

        <section className="ptw-section">
          <Title level={4}>C. Hazards & Risk Assessment</Title>
          <div className="ptw-subsection">
            <strong>Hazards:</strong> {hazards.length > 0 ? hazards.join(', ') : '—'}
          </div>
          <div className="ptw-grid">
            <div><strong>Probability:</strong> {permit.probability}</div>
            <div><strong>Severity:</strong> {permit.severity}</div>
            <div><strong>Risk Score:</strong> {permit.risk_score}</div>
            <div><strong>Risk Level:</strong> {permit.risk_level}</div>
          </div>
          <div className="ptw-subsection">
            <strong>Risk Assessment Ref:</strong> {permit.risk_assessment_id || '—'}
          </div>
        </section>

        <section className="ptw-section">
          <Title level={4}>D. Controls / Safety Measures</Title>
          <div className="ptw-list">
            {controlMeasures.length > 0 ? controlMeasures.map((item, index) => (
              <div key={`${item}-${index}`}>• {item}</div>
            )) : <div>—</div>}
          </div>
          <div className="ptw-subsection"><strong>Special Instructions:</strong> {permit.special_instructions || '—'}</div>
          <div className="ptw-subsection"><strong>Emergency Procedures:</strong> {(permit.permit_parameters?.emergency_procedures || permit.emergency_procedures || '—') as any}</div>
          <div className="ptw-subsection"><strong>Housekeeping / Signage:</strong> Verified</div>
        </section>

        <section className="ptw-section">
          <Title level={4}>E. PPE Requirements</Title>
          <div className="ptw-ppe-grid">
            {allPpe.length > 0 ? allPpe.map((ppe) => (
              <div key={ppe} className="ptw-checkbox-item">
                <span className={`ptw-checkbox ${selectedPpe.includes(ppe) ? 'checked' : ''}`}></span>
                <span>{ppe}</span>
              </div>
            )) : <div>—</div>}
          </div>
        </section>

        {(permit.permit_type_details?.requires_gas_testing || (permit.gas_readings || []).length > 0) && (
          <section className="ptw-section">
            <Title level={4}>F. Gas Testing</Title>
            <table className="ptw-table">
              <thead>
                <tr>
                  <th>Gas</th>
                  <th>Reading</th>
                  <th>Unit</th>
                  <th>Status</th>
                  <th>Tested By</th>
                  <th>Tested At</th>
                </tr>
              </thead>
              <tbody>
                {(permit.gas_readings || []).length > 0 ? permit.gas_readings.map((reading) => (
                  <tr key={reading.id}>
                    <td>{reading.gas_type}</td>
                    <td>{reading.reading}</td>
                    <td>{reading.unit}</td>
                    <td>{reading.status}</td>
                    <td>{displayName(reading.tested_by_details)}</td>
                    <td>{formatDateTime(reading.tested_at)}</td>
                  </tr>
                )) : (
                  <tr><td colSpan={6}>No readings recorded</td></tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        {(permit.permit_type_details?.requires_structured_isolation || (isolation?.points || []).length > 0) && (
          <section className="ptw-section">
            <Title level={4}>G. Isolation Register</Title>
            <table className="ptw-table">
              <thead>
                <tr>
                  <th>Point</th>
                  <th>Location</th>
                  <th>Lock Count</th>
                  <th>Isolated By</th>
                  <th>Verified By</th>
                  <th>De-isolated By</th>
                </tr>
              </thead>
              <tbody>
                {(isolation?.points || []).length > 0 ? isolation?.points.map((point) => (
                  <tr key={point.id}>
                    <td>{point.point_details?.point_code || point.custom_point_name}</td>
                    <td>{point.point_details?.location || point.custom_point_details || '—'}</td>
                    <td>{point.lock_count ?? '—'}</td>
                    <td>{displayName(point.isolated_by_details)}</td>
                    <td>{displayName(point.verified_by_details)}</td>
                    <td>{displayName(point.deisolated_by_details)}</td>
                  </tr>
                )) : (
                  <tr><td colSpan={6}>No isolation points recorded</td></tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        <section className="ptw-section">
          <Title level={4}>H. Work Team & Toolbox Talk</Title>
          <div className="ptw-subsection">
            <strong>TBT Title:</strong> {tbt?.tbt?.title || '—'}
          </div>
          <div className="ptw-grid">
            <div><strong>Conducted At:</strong> {formatDateTime(tbt?.tbt?.conducted_at || null)}</div>
            <div><strong>Conducted By:</strong> {displayName(tbt?.tbt?.conducted_by_details)}</div>
            <div><strong>Link:</strong> {tbt?.tbt?.url || '—'}</div>
          </div>
          <div className="ptw-subsection"><strong>Notes:</strong> {tbt?.tbt?.notes || '—'}</div>
          <table className="ptw-table">
            <thead>
              <tr>
                <th>S.No</th>
                <th>Name</th>
                <th>Designation</th>
                <th>Company</th>
                <th>Signature</th>
                <th>TBT Ack</th>
                <th>Ack Time</th>
              </tr>
            </thead>
            <tbody>
              {(permit.assigned_workers || []).length > 0 ? permit.assigned_workers.map((worker, index) => {
                const attendance = tbtAttendanceByWorker.get(worker.id);
                const workerDetails = worker.worker_details || {};
                return (
                  <tr key={worker.id}>
                    <td>{index + 1}</td>
                    <td>{`${workerDetails.name || ''} ${workerDetails.surname || ''}`.trim() || '—'}</td>
                    <td>{workerDetails.designation || '—'}</td>
                    <td>{workerDetails.department || '—'}</td>
                    <td className="ptw-signature-cell">________________</td>
                    <td>{attendance?.acknowledged ? 'Yes' : 'No'}</td>
                    <td>{attendance?.acknowledged_at ? formatDateTime(attendance.acknowledged_at) : '—'}</td>
                  </tr>
                );
              }) : (
                <tr><td colSpan={7}>No workers assigned</td></tr>
              )}
            </tbody>
          </table>
        </section>

        <section className="ptw-section">
          <Title level={4}>I. Workflow Timeline</Title>
          <div className="ptw-grid">
            <div><strong>Submitted:</strong> {formatDateTime(permit.submitted_at)}</div>
            <div><strong>Verified:</strong> {formatDateTime(permit.verified_at)}</div>
            <div><strong>Approved:</strong> {formatDateTime(permit.approved_at)}</div>
            <div><strong>Activated:</strong> {formatDateTime(permit.actual_start_time)}</div>
            <div><strong>Completed:</strong> {formatDateTime(permit.actual_end_time)}</div>
          </div>
        </section>

        <section className="ptw-section ptw-signature-section">
          <Title level={4}>J. Digital Signatures</Title>
          <div className="ptw-signature-grid">
            {[
              { label: 'Requestor', type: 'requestor', fallback: permit.created_by_details },
              { label: 'Verifier', type: 'verifier', fallback: permit.verifier_details },
              { label: 'Approver', type: 'approver', fallback: permit.approved_by_details }
            ].map((entry) => {
              const sig = findSignatureByType(signatureMap, entry.type);
              
              if (!sig) {
                return (
                  <div key={entry.type} className="ptw-signature-card">
                    <div className="ptw-signature-label">{entry.label}</div>
                    <div className="ptw-signature-image-container">
                      <div className="ptw-adobe-signature-block">
                        <div className="ptw-signature-partitions">
                          <div className="ptw-signature-left">
                            <div className="ptw-signer-name">{entry.label}</div>
                            <div className="ptw-designation">Not signed</div>
                          </div>
                          <div className="ptw-signature-divider"></div>
                          <div className="ptw-signature-right">
                            <div className="ptw-signed-by">Awaiting signature</div>
                            <div className="ptw-signed-at">Date: —</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              }

              // Extract signature details safely
              const signerName = typeof sig.signer_name === 'string' ? sig.signer_name : 
                                (sig.signatory_details?.full_name || sig.signatory_details?.username || 'Unknown');
              const designation = typeof sig.designation === 'string' ? sig.designation : '';
              const employeeId = typeof sig.employee_id === 'string' ? sig.employee_id : '';
              const signedDate = formatDateOnly(sig.signed_at);
              const signatureImageSrc = resolveSignatureSrc(sig.signature_data);
              const isPrecomposed = isPrecomposedCard(sig.signature_data);
              const renderMode = isPrecomposed ? 'card' : getSignatureRenderMode(sig);
              
              return (
                <div key={entry.type} className="ptw-signature-card">
                  <div className="ptw-signature-label">{entry.label}</div>
                  {renderMode === 'card' ? (
                    <div className="ptw-signature-card-only">
                      {signatureImageSrc ? (
                        <img
                          src={signatureImageSrc}
                          alt={`${entry.label} signature card`}
                          className="ptw-signature-card-image"
                        />
                      ) : (
                        <div className="ptw-signature-placeholder">Signature on file</div>
                      )}
                    </div>
                  ) : (
                    <div className="ptw-signature-image-container">
                      <div className="ptw-adobe-signature-block">
                        <div className="ptw-signature-partitions">
                          <div className="ptw-signature-left">
                            <div className="ptw-signer-name">{signerName}</div>
                            {employeeId && <div className="ptw-employee-id">ID: {employeeId}</div>}
                            {designation && <div className="ptw-designation">{designation}</div>}
                          </div>
                          <div className="ptw-signature-divider"></div>
                          <div className="ptw-signature-right">
                            <div className="ptw-signed-by">Digitally signed by {signerName}</div>
                            <div className="ptw-signed-at">Date: {signedDate}</div>
                          </div>
                        </div>
                        {signatureImageSrc && (
                          <div className="ptw-signature-image-overlay">
                            <img 
                              src={signatureImageSrc} 
                              alt={`${entry.label} signature`} 
                              className="ptw-signature-template-image"
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>

        <section className="ptw-section">
          <Title level={4}>Safety Checklist Summary</Title>
          <div className="ptw-checklist">
            {Array.isArray(checklistItems) && checklistItems.length > 0 && typeof checklistItems[0] === 'string' ? (
              (checklistItems as string[]).map((item) => (
                <div key={item} className="ptw-checkbox-item">
                  <span className="ptw-checkbox checked"></span>
                  <span>{item}</span>
                </div>
              ))
            ) : (
              (checklistItems as { key: string; checked: boolean }[]).map((item) => (
                <div key={item.key} className="ptw-checkbox-item">
                  <span className={`ptw-checkbox ${item.checked ? 'checked' : ''}`}></span>
                  <span>{item.key}</span>
                </div>
              ))
            )}
            {checklistItems.length === 0 && <div>—</div>}
          </div>
        </section>
      </PrintDocumentTemplate>
    </div>
  );
};

export default PTWStandardPrint;
