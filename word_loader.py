import random
from pathlib import Path

def load_words(file_name):
    # Xác định đường dẫn đến thư mục chứa file này
    project_folder = Path(__file__).resolve().parent
    file_path = project_folder / file_name

    words = []

    # Mở file với mã hóa UTF-8
    with open(file_path, "r", encoding="utf-8-sig") as file:
        for line in file:
            line = line.strip() #xóa bỏ ký tự trống trước và sau

            # Bỏ qua dòng trống
            if not line:
                continue

            # Tách từ tiếng Trung và nghĩa tiếng Việt
            parts = line.split("\t", maxsplit=1)

            if len(parts) != 2:
                print("Dòng dữ liệu không hợp lệ:", line)
                continue

            chinese = parts[0].strip()

            meanings = [
                meaning.strip()
                for meaning in parts[1].split(";")
                if meaning.strip()
            ]

            if chinese and meanings:
                words.append({
                    "chinese": chinese,
                    "meanings": meanings
                })

    return words


if __name__ == "__main__":
    word_list = load_words("data/HSK5_words.txt")

    print("Tổng số từ:", len(word_list))

    if word_list:
        word = random.choice(word_list)

        print("Từ tiếng Trung:", word["chinese"])
        print("Các nghĩa tiếng Việt:", word["meanings"])
