import requests
import asyncio
import telegram
import time
import random
from collections import deque

# Konfigurasi Bot Telegram
TOKEN = "ganti token" # token mu
CHAT_ID = "-1002402121526" # id group atau usergroup @groupmu

# URL API
API_URL = "https://didihub20.com/api/main/lottery/rounds?page=1&count=20&type=2"

# Tabel Kompensasi (taruhan progresif jika kalah)
KOMPEN_TABLE = [1000, 3000, 6000, 16000, 32000, 80000, 160000, 350000, 800000, 
                1700000, 4000000, 8000000, 18000000, 50000000]

# Riwayat prediksi (Maksimal 20)
history = deque(maxlen=20)

# Menyimpan periode terakhir yang sudah dikirim
last_sent_period = None
current_bet_index = 0  # Index untuk tabel kompensasi (mulai dari 1000)
current_bet_amount = KOMPEN_TABLE[current_bet_index]  # Taruhan awal

# Fungsi untuk mengambil data dari API
def get_lottery_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()["items"]
        else:
            print("Gagal mengambil data dari API.")
            return []
    except Exception as e:
        print(f"Error saat mengambil data API: {e}")
        return []

# Fungsi untuk menentukan prediksi secara acak
def generate_random_prediction():
    return random.choice(["Besar", "Kecil"])

# Fungsi untuk mengecek apakah taruhan menang atau kalah
def check_win_loss(prediction, last_result):
    result_type = "Kecil" if 0 <= last_result <= 4 else "Besar"
    status = "WIN✅IN" if prediction == result_type else "MIN"
    return status, last_result, result_type

# Fungsi untuk mengirim pesan ke Telegram
async def send_telegram_message(message):
    bot = telegram.Bot(token=TOKEN)
    async with bot:
        await bot.send_message(chat_id=CHAT_ID, text=message)

# Fungsi utama (looping terus menerus)
async def main():
    global last_sent_period, current_bet_index, current_bet_amount

    while True:
        data = get_lottery_data()
        
        if data:
            last_period = int(data[0]["period"])  # Periode terakhir dalam data
            last_result = data[0]["number"]  # Hasil angka periode terakhir
            next_period = last_period + 1  # Periode berikutnya
            
            # Jika periode baru, lakukan prediksi dan evaluasi hasil sebelumnya
            if last_period != last_sent_period:
                prediction = generate_random_prediction()
                status, result_number, result_type = check_win_loss(prediction, last_result)

                # **Simpan nilai taruhan sebelum diperbarui**
                bet_amount = current_bet_amount  

                # Update taruhan untuk periode berikutnya
                if status == "WIN✅":
                    current_bet_index = 0  # Reset taruhan ke 1000 jika menang WIN✅
                else:
                    current_bet_index = min(current_bet_index + 1, len(KOMPEN_TABLE) - 1)  # Naikkan level taruhan
                
                # Update nilai taruhan yang akan digunakan di periode berikutnya
                current_bet_amount = KOMPEN_TABLE[current_bet_index]  

                # Simpan ke riwayat dengan taruhan yang benar
                history.append(f"{last_period} {prediction} {bet_amount} {status} hasil {result_number} {result_type}")

                # Debugging: Cetak di layar untuk cek menang/kalah
                print("\n==== DEBUG INFO ====")
                print(f"Periode: {last_period}")
                print(f"Prediksi: {prediction}")
                print(f"Taruhan: {bet_amount}")  # **Sekarang taruhan selalu sesuai dengan kompensasi**
                print(f"Hasil: {result_number} ({result_type})")
                print(f"Status: {status}")
                print("====================\n")

                # Format pesan riwayat prediksi
                history_message = "Riwayat prediksi DIDIHUB\n" + "\n".join(history)

                # Kirim ke Telegram
                await send_telegram_message(history_message)

                # Kirim prediksi baru dengan taruhan yang diperbarui
                prediction_message = f"Prediksi sekarang: {next_period} {prediction} {current_bet_amount}"
                print(prediction_message)  # Cetak di layar juga
                await send_telegram_message(prediction_message)

                last_sent_period = last_period  # Simpan periode terakhir yang dikirim

        await asyncio.sleep(5)  # Cek API setiap 5 detik

# Jalankan program
asyncio.run(main())
