# Tài Liệu Kỹ Thuật Backend - Hệ Thống Đăng Nhập Nhận Diện Khuôn Mặt

Mô tả chi tiết về kiến trúc, luồng hoạt động, và các thành phần kỹ thuật của Backend (FastAPI).

## 1. Công Nghệ Sử Dụng (Tech Stack)

*   **Ngôn Ngữ:** Python 3.10+
*   **Framework:** FastAPI (Web framework hiệu năng cao, bất đồng bộ)
*   **AI/Computer Vision:**
    *   **DeepFace:** Thư viện phân tích khuôn mặt (sử dụng model VGG-Face để trích xuất đặc trưng).
    *   **OpenCV (`opencv-python`):** Xử lý hình ảnh.
    *   **NumPy:** Tính toán vector/khoảng cách.
*   **Database:** MongoDB (lưu trữ NoSQL).
*   **Database Driver:** `motor` (Driver bất đồng bộ cho MongoDB).
*   **Server:** Uvicorn (ASGI server).

## 2. Cấu Trúc Dự Án

```
backend/
├── main.py           # Entry point, định nghĩa API endpoints và vòng đời ứng dụng
├── database.py       # Quản lý kết nối Database (MongoDB)
├── models.py         # Định nghĩa Data Models (Pydantic schemas)
├── utils.py          # Các hàm xử lý core logic: xử lý ảnh, AI model, tính toán
└── requirements.txt  # Danh sách thư viện phụ thuộc
```

## 3. Luồng Hoạt Động (Core Logic)

Hệ thống hoạt động dựa trên cơ chế so sánh embedding (vector đặc trưng) của khuôn mặt.

### A. Khái Niệm Chính

*   **Face Embedding:** Một vector số học (list of floats) đại diện cho các đặc điểm duy nhất của một khuôn mặt. Model **VGG-Face** chuyển đổi hình ảnh khuôn mặt thành vector 2622 hoặc 4096 chiều (tùy phiên bản).
*   **Khoảng Cách Euclidean (L2 Distance):** Dùng để đo sự sai khác giữa 2 vector. Khoảng cách càng nhỏ => 2 khuôn mặt càng giống nhau.
*   **Threshold (Ngưỡng):** Giá trị giới hạn để quyết định "Khớp" hay "Không khớp". Trong hệ thống này, ngưỡng được đặt là **0.55** (phù hợp với VGG-Face + L2 Distance).

### B. Các Hàm Quan Trọng (`utils.py`)

#### `base64_to_cv2(str)`
*   Nhận chuỗi Base64 từ Frontend.
*   Giải mã thành mảng NumPy -> Chuyển thành ảnh OpenCV (BGR).

#### `get_face_embedding(img)`
*   Sử dụng `DeepFace.represent(..., model_name="VGG-Face")`.
*   Phát hiện khuôn mặt trong ảnh và trả về vector đặc trưng (Embedding).
*   Nếu không tìm thấy mặt -> Trả về `None` (hoặc báo lỗi).

#### `calculate_distance(emb1, emb2)`
*   Tính khoảng cách L2 giữa 2 vector: `sqrt(sum((a - b)^2))` qua `numpy.linalg.norm`.

## 4. API Endpoints (`main.py`)

### 1. Register API (`POST /register`)
Dùng để đăng ký người dùng mới.

*   **Input:** `user_id` (string), `image` (Base64 string).
*   **Quy Trình:**
    1.  Kiểm tra `user_id` đã tồn tại trong DB chưa. Nếu có -> Lỗi 400.
    2.  Decode ảnh Base64 sang ảnh OpenCV.
    3.  Trích xuất Face Embedding từ ảnh (sử dụng `get_face_embedding`).
    4.  Nếu không tìm thấy mặt -> Lỗi 400.
    5.  Lưu document vào MongoDB collection `users`.
        *   Cấu trúc lưu: `{ "user_id": "...", "face_embedding": [...], "created_at": ... }`
*   **Response:** `success: True`, `message`.

### 2. Login/Verify API (`POST /verify`)
Dùng để xác thực người dùng khi đăng nhập.

*   **Input:** `image` (Base64 string).
*   **Quy Trình:**
    1.  Decode ảnh Base64 -> OpenCV.
    2.  Trích xuất Face Embedding từ ảnh đầu vào (gọi là `input_embedding`).
    3.  **Tìm kiếm 1:N (One-to-Many):**
        *   Lấy danh sách tất cả user từ Database (hiện tại đang duyệt loop, có thể tối ưu bằng Vector Search trong tương lai).
        *   Với mỗi user trong DB, lấy `stored_embedding`.
        *   Tính khoảng cách (`utils.calculate_distance`) giữa `input_embedding` và `stored_embedding`.
    4.  Tìm user có khoảng cách nhỏ nhất (`min_distance`).
    5.  **Kiểm tra Ngưỡng (Threshold Check):**
        *   Nếu `min_distance < 0.55` -> Đăng nhập thành công.
        *   Ngược lại -> Thất bại (Không nhận ra khuôn mặt).
*   **Response:** `success: True/False`, `data: { "user_id": ..., "distance": ... }`.

### 3. Health Check (`GET /`)
Kiểm tra server có đang chạy không.

## 5. Cơ Sở Dữ Liệu (Database)

*   **Database Name:** `testAI`
*   **Collection:** `users`
*   **Schema:**

```json
{
  "_id": ObjectId("..."),
  "user_id": "user123",            // Unique Index
  "face_embedding": [0.12, -0.05, ...],  // Vector đặc trưng
  "created_at": ISODate("...")
}
```

## 6. Lưu ý quan trọng

*   Hệ thống hiện tại thực hiện so sánh tuyến tính (**Linear Scan**) trong Python. Với dữ liệu lớn (>1000 users), nên chuyển sang sử dụng **Vector Database** (như MongoDB Atlas Vector Search, Qdrant, Milvus) để tăng tốc độ tìm kiếm.
*   Ngưỡng **0.55** có thể cần tinh chỉnh tùy thuộc vào điều kiện ánh sáng và chất lượng camera thực tế.
