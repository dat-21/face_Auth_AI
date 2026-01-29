# Facial Recognition Concepts

## 1. Face Embedding
A **Face Embedding** is a numerical representation of a face. Instead of storing the actual image (pixels), we pass the image through a Deep Neural Network (like ResNet or a Transformer model trained on faces) to extract features.

The output is a vector (a list of numbers), typically of size 128 (dlib/face_recognition) or 512/1024 (DeepFace/ArcFace).

**Example:**
Face A -> `[0.12, -0.45, 0.88, ...]` (128 dimensions)

**Key Properties:**
- **Invariance:** Pictures of the same person with distinguishing lighting or angles should produce *similar* vectors.
- **Discriminativeness:** Pictures of different people should produce *distinct* vectors.

Our system uses the `face_recognition` library (based on dlib), which outputs a 128-dimensional vector.

## 2. Vector Comparison (Euclidean Distance)
To check if two faces belong to the same person, we calculate the mathematical distance between their embeddings.

**Euclidean Distance Formula:**
$$ d(A, B) = \sqrt{\sum_{i=1}^{n} (A_i - B_i)^2} $$

- **Lower Distance (`0.0` to `0.4`)**: The faces are very similar (Likely the same person).
- **Higher Distance (`0.6` to `1.0+`)**: The faces are different.

## 3. Threshold Selection
The **Threshold** is the cutoff point to decide "Match" or "No Match".

- **Threshold = 0.6**: Recommended default for `dlib`.
  - Distance < 0.6 -> **Match**
  - Distance > 0.6 -> **No Match**

**Trade-offs:**
- **Lower Threshold (e.g., 0.5)**: Stricter. Fewer False Positives (accepting an imposter), but more False Negatives (rejecting the real user).
- **Higher Threshold (e.g., 0.7)**: Lenient. More False Positives, fewer False Negatives.

For this login system, we will use **0.55 or 0.6** as a balanced starting point.
