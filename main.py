import json, time, threading, requests

fields = ["STT", "Id", "TOAN", "VAN", "LI", "HOA", "NGOAI_NGU", "SU", "DIA", "SINH", "GIAO_DUC_CONG_DAN", "TIN_HOC", "TONGDIEM"]

def lay_diem(d):
    line = ",".join(str(d.get(field, "")) for field in fields)
    return line.replace("-1", "")

def run_thread(func, param_list, workers=100):
    def call(param, index, results):
        data = func(param)
        results[index] = data

    for i in range(0, len(param_list), workers):
        sub_list = param_list[i:i+workers]
        threads = []
        results = [None for _ in range(workers)]
        for index in range(len(sub_list)):
            param = sub_list[index]
            t = threading.Thread(target=call, args=(param, index, results))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        for item in results:
            if item is not None:
                yield item

def fetch_diem_thi(sbd: str) -> tuple:
    url = f"https://s6.tuoitre.vn/api/diem-thi-thpt.htm?sbd={sbd}&year=2025"
    r = None
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.text.strip():
            d = r.json()
            if d.get("total") == 1:
                return True, lay_diem(d["data"][0])
        if r.status_code == 429:
            time.sleep(1)
            return fetch_diem_thi(sbd)
        return False, (f"Không tìm thấy {sbd}", r.status_code)
    except Exception as ex:
        return False, (f"Lỗi: {ex}", getattr(r, "status_code", -1))

f = open("diemthi.csv", mode="w", encoding="utf-8")
f.write(",".join(fields) + "\n") 

sbd_list = [f"{2:02}{i:06}" for i in range(1, 100 + 1)]

for r in run_thread(fetch_diem_thi, sbd_list, workers=100):
    if r is None:
        continue
    success, msg = r
    if success:
        print(msg)
        f.write(msg + "\n")
    else:
        print(msg)
f.close()