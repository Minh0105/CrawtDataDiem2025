# CrawlDataDiem2025

## Mô tả
Script này dùng để crawl điểm thi THPT quốc gia từ API và lưu vào file CSV.

## Yêu cầu
- Python 3.7 trở lên
- Thư viện: `requests`

## Cài đặt thư viện
Mở terminal/cmd tại thư mục chứa file `main.py` và chạy:
```sh
pip install requests
```

## Cách chạy
1. Mở terminal/cmd tại thư mục chứa file `main.py`.
2. Chạy lệnh sau:
```sh
python main.py
```

## Kết quả
- File kết quả sẽ được lưu là `diemthi.csv` trong cùng thư mục.
- Bạn có thể mở file này bằng Excel hoặc bất kỳ phần mềm đọc CSV nào.

## Tùy chỉnh
- Để thay đổi mã tỉnh hoặc số lượng SBD, sửa dòng sau trong file `main.py`:
  ```python
  sbd_list = [f"{2:02}{i:06}" for i in range(1, 100 + 1)]
  ```
  - Thay số `2` bằng mã tỉnh bạn muốn.
  - Thay `100` bằng số lượng SBD cần crawl.
