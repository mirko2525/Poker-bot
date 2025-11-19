from pathlib import Path
import glob

import cv2
import numpy as np


class HeroBackRecognizer:
    def __init__(
        self,
        templates_dir: Path,
        threshold_strong: float = 0.80,
        threshold_soft: float = 0.65,
    ) -> None:
        self.templates_dir = Path(templates_dir)
        self.threshold_strong = threshold_strong
        self.threshold_soft = threshold_soft
        self.templates = self._load_templates()

        if not self.templates:
            raise RuntimeError(f"Nessun template trovato in {self.templates_dir}")

        # tutte le immagini hanno stessa size grazie allo script
        first = next(iter(self.templates.values()))
        # OpenCV shape: (H, W) -> template_size: (W, H)
        self.template_size = (first.shape[1], first.shape[0])

    def _load_templates(self) -> dict:
        templates: dict = {}
        for path in glob.glob(str(self.templates_dir / "*.png")):
            code = Path(path).stem  # "Kd", "7h", ...
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            templates[code] = img
        return templates

    def preprocess(self, gray_img: np.ndarray) -> np.ndarray:
        img = cv2.resize(gray_img, self.template_size, interpolation=cv2.INTER_AREA)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        return img

    def recognize(self, gray_img: np.ndarray):
        """Ritorna (code, score, conf) dove conf ∈ {"strong","weak","none"}."""
        if gray_img is None or gray_img.size == 0:
            return None, 0.0, "none"

        patch = self.preprocess(gray_img)

        best_code = None
        best_score = -1.0

        for code, tmpl in self.templates.items():
            res = cv2.matchTemplate(patch, tmpl, cv2.TM_CCOEFF_NORMED)
            score = float(res.max())
            if score > best_score:
                best_score = score
                best_code = code

        if best_score >= self.threshold_strong:
            conf = "strong"
        elif best_score >= self.threshold_soft:
            conf = "weak"
        else:
            return None, best_score, "none"

        return best_code, best_score, conf
