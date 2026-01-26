import api from '@common/utils/axiosetup';

const PREVIEW_ENDPOINT = '/authentication/signature/template/preview/?fresh=1';

const toAbsoluteUrl = (url: string, baseUrl?: string) => {
  try {
    return new URL(url, baseUrl || window.location.origin).toString();
  } catch {
    return url;
  }
};

const withCacheBust = (url: string) => {
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}t=${Date.now()}`;
};

export const fetchSignaturePreviewUrl = async (): Promise<string> => {
  const response = await api.get(PREVIEW_ENDPOINT, { responseType: 'blob' });
  const contentType = (response.headers?.['content-type'] || '').toLowerCase();

  if (contentType.includes('application/json') || contentType.includes('text/')) {
    const text = await response.data.text();
    let payload: any = null;
    try {
      payload = JSON.parse(text);
    } catch {
      throw new Error('Signature preview unavailable');
    }
    if (payload?.template_url) {
      return withCacheBust(toAbsoluteUrl(payload.template_url, response.config.baseURL));
    }
    throw new Error(payload?.error || 'Signature preview unavailable');
  }

  const blob = response.data instanceof Blob
    ? response.data
    : new Blob([response.data], { type: contentType || 'image/png' });

  return URL.createObjectURL(blob);
};
