import json
import time
import asyncio
import aiohttp
import os

# Define the fields for the output CSV file
fields = ["STT", "Id", "TOAN", "VAN", "LI", "HOA", "NGOAI_NGU", "SU", "DIA", "SINH", "GIAO_DUC_CONG_DAN", "TIN_HOC", "TONGDIEM"]

def lay_diem(d):
    """
    Extracts relevant score data from a dictionary and formats it as a comma-separated string.
    Replaces scores of -1 with an empty string.
    """
    line = ",".join(str(d.get(field, "")) for field in fields)
    return line.replace("-1", "")

async def fetch_diem_thi(session, sbd: str, semaphore):
    """
    Asynchronously fetches exam scores for a given SBD (candidate number).
    Uses a semaphore to limit concurrent requests to avoid overwhelming the server.
    """
    url = f"https://s6.tuoitre.vn/api/diem-thi-thpt.htm?sbd={sbd}&year=2025"
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("total") == 1:
                        # Extract and format the data if a single result is found
                        return True, lay_diem(data["data"][0])
                if response.status == 429:
                    # Retry after a delay if a "Too Many Requests" error is received
                    await asyncio.sleep(1)
                    return await fetch_diem_thi(session, sbd, semaphore)
                # Handle cases where the data is not found or the status code is not 200
                return False, (f"Không tìm thấy {sbd}", response.status)
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            # Handle network errors or timeouts
            return False, (f"Lỗi: {ex}", -1)
        except json.JSONDecodeError as ex:
            # Handle JSON decoding errors
            return False, (f"Lỗi giải mã JSON: {ex}", -1)

async def main():
    """
    Main asynchronous function to manage the crawling process, including checkpointing
    and file writing.
    """
    checkpoint_file = "checkpoint.txt"
    start_index = 0
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as cp:
            try:
                start_index = int(cp.read().strip())
            except:
                start_index = 0

    sbd_list = [f"{2:02}{i:06}" for i in range(1, 124601)]
    sbd_to_fetch = sbd_list[start_index:]

    # Use append mode if the file already exists, otherwise write the header
    file_exists = os.path.exists("diemthi.csv")
    f = open("diemthi.csv", mode="a" if file_exists else "w", encoding="utf-8")
    if not file_exists:
        f.write(",".join(fields) + "\n")

    # Limit concurrent requests to prevent overwhelming the server
    semaphore = asyncio.Semaphore(100)
    
    # Create an aiohttp session to manage connections
    async with aiohttp.ClientSession() as session:
        # Create a list of tasks (coroutines) for each SBD
        tasks = [fetch_diem_thi(session, sbd, semaphore) for sbd in sbd_to_fetch]

        # Use asyncio.as_completed to process results as they finish
        for idx, task in enumerate(asyncio.as_completed(tasks), start=start_index):
            success, msg = await task
            if success:
                print(msg)
                f.write(msg + "\n")
                f.flush()  # Ensure data is written to disk immediately
            else:
                print(msg)

            # Save checkpoint every 100 records
            if (idx + 1) % 100 == 0:
                with open(checkpoint_file, "w") as cp:
                    cp.write(str(idx + 1))

    f.close()
    
    # Save final checkpoint
    with open(checkpoint_file, "w") as cp:
        cp.write(str(len(sbd_list)))

# Run the main asynchronous function
if __name__ == "__main__":
    asyncio.run(main())
