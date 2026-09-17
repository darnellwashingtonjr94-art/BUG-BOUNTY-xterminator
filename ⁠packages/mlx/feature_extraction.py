import numpy as np

class HeaderFeatureExtractor:
    """Transforms HTTP headers into numerical features for anomaly detection."""
    
    SECURITY_HEADERS = {
        'strict-transport-security',
        'x-frame-options',
        'x-content-type-options',
        'content-security-policy',
        'x-xss-protection'
    }

    @classmethod
    def extract_features(cls, headers: dict) -> np.ndarray:
        # Normalize header keys to lowercase
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        # Feature 1: Total number of headers (Anomalous APIs often have very few or very many)
        header_count = len(normalized_headers)
        
        # Feature 2: Missing security headers (0.0 to 1.0 score of how many are missing)
        present_security_headers = sum(
            1 for h in cls.SECURITY_HEADERS if h in normalized_headers
        )
        security_risk_score = 1.0 - (present_security_headers / len(cls.SECURITY_HEADERS))
        
        # Feature 3: Content-Length presence and magnitude
        content_length = int(normalized_headers.get('content-length', 0))
        # Log scale the content length to normalize massive payloads
        cl_magnitude = np.log1p(content_length)
        
        # Feature 4: Presence of custom X- headers (often indicates internal routing)
        custom_headers = sum(1 for k in normalized_headers.keys() if k.startswith('x-') 
                             and k not in cls.SECURITY_HEADERS)

        return np.array([[
            header_count, 
            security_risk_score, 
            cl_magnitude, 
            custom_headers
        ]])
