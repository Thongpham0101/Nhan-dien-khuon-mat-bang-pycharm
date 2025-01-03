from flask import Flask, request, render_template, jsonify #Tạo ứng dụng web ảo trên Windows, Hệ thống sử dụng Flask để tạo API RESTful cho phép người dùng giao tiếp qua HTTP
import cv2 #Thư viện xử lí hình ảnh
import face_recognition #Thư viện nhận diện khuôn mặt
import os #Khởi tạo giao diện liên quan đến tệp thông tin...
import base64 #Mã hóa và giải mã dữ liệu chuẩn base64 (Nhị phân)
from datetime import datetime #Ngày tháng và giờ
import numpy as np #Xử lí mảng và tính toán
import re #Xử lí chuỗi
import shutil #Thao tác với hệ thống tệp: sao chép, đổi tên,...
from unidecode import unidecode #xử lí chữ
import pandas as pd #xử lí tệp excel
app = Flask(__name__)
# Mật khẩu của quản trị viên cho tính năng 1.2
ADMIN_PASSWORD = "N7@tnl"
# Đường dẫn tới kho nhận dạng khuôn mặt và thẻ sinh viên, đường dẫn ghi lại
lịch sử nhận diện
face_path = "C:/Users/LOQ/Documents/VisionFD/VFD01/library/Pic_face_ID"
card_path = "C:/Users/LOQ/Documents/VisionFD/VFD01/library/Pic_the_sv"
history_path = "C:/Users/LOQ/Documents/VisionFD/VFD01/lichsuquet.csv"
# Phần nhận diện khuôn mặt qua webcam
# Các danh sách lưu trữ hình ảnh khuôn mặt và thông tin sinh viên
face_images = []
card_images = []
class_names = []
mssvs = []
# Liệt kê các tệp trong thư mục và lọc đuôi tệp hình ảnh định dạng bắt buộc
face_list = [f for f in os.listdir(face_path) if f.lower().endswith(('.png',
'.jpg', '.jpeg'))]
card_list = [f for f in os.listdir(card_path) if f.lower().endswith(('.png',
'.jpg', '.jpeg'))]
# Lưu trữ hình ảnh khuôn mặt và thông tin được ghi trên file ảnh
for cl in face_list:
 cur_img = cv2.imread(f"{face_path}/{cl}") #Lệnh trích xuất
ảnh qua webcam
 if cur_img is not None:
 parts = os.path.splitext(cl)[0].rsplit('_', 1)
 if len(parts) == 2:
 name, mssv = parts
 face_images.append(cur_img)
 class_names.append(name)
 mssvs.append(mssv)
 else:
 print(f"Bỏ qua tệp không đúng định dạng: {cl}") #Sai định dạng
đặt tên ảnh là bỏ qua (VD: TÊNSV_MSSV.đuôi ảnh) đã có sẵn trong CSDL
print(f"Số khuôm mặt đã xử lí: {len(face_images)}")
# Hàm check file hợp lệ: Kiểm tra file có định dạng tên hợp lệ (chứa tên và
MSSV) khi lưu vào CSDL
def is_valid_file(filename):
 parts = os.path.splitext(filename)[0].rsplit('_', 1)
 return len(parts) == 2
# Hàm tìm và tách khuôn mặt đồng thời xử lí ảnh
def crop_face(image):
 face_locations = face_recognition.face_locations(image)
 if face_locations: #tọa độ khuôn mặt
 y1, x2, y2, x1 = face_locations[0]
 return image[y1:y2, x1:x2]
 return None
# Phần xử lí ảnh từ thẻ sinh viên (Tương tự như nhận diện qua webcam ở trên)
card_faces = []
card_names = []
card_mssvs = []
for cl in card_list:
 cur_img = cv2.imread(f"{card_path}/{cl}") #Lệnh
trích xuất ảnh từ thẻ sinh viên
 if cur_img is not None:
 if is_valid_file(cl):
 parts = os.path.splitext(cl)[0].rsplit('_', 1)
 name, mssv = parts
 face_img = crop_face(cur_img)
 if face_img is not None:
 card_faces.append(face_img)
 card_names.append(name)
 card_mssvs.append(mssv)
 else:
 print(f"Không tìm thấy khuôn mặt trong tệp: {cl}")
 else:
 print(f"Bỏ qua tệp không đúng định dạng: {cl}")
print(f"Số khuôn mặt trên ảnh thẻ đã xử lí: {len(card_faces)}")
# Chuyển đổi hình ảnh khuôn mặt thành các vecto mã hóa
def encode_images(images):
 encode_list = []
 for img in images:
 img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #Chuyển
đổi màu sang RGB đảm bảo độ chính xác khi xử lí đồng thời mã hóa
 encodings = face_recognition.face_encodings(img)
 if encodings:
 encode_list.append(encodings[0])
 print("Mã hóa khuôn mặt thành công.")
 else:
 print("Không tìm thấy khuôn mặt trong hình ảnh.")
 return encode_list
# Các danh sách chứa vector mã hóa của khuôn mặt từ CSDL và từ thẻ sinh viên
encode_list_known = encode_images(face_images)
encode_list_cards = encode_images(card_faces)
print(f"Mã hóa thành công: {len(encode_list_known)} khuôn mặt từ CSDL.")
print(f"Mã hóa thành công: {len(encode_list_cards)} khuôn mặt từ thẻ sinh
viên trong CSDL.")
# Hàm đọc và ghi đồng thời lưu hình ảnh vào thư mục "Pic_face_ID"
def save_image(face_image, name, mssv):
 name = remove_diacritics(name)
 filename = f"{name}_{mssv}.png"
 filepath = os.path.join(face_path, filename) # Đảm bảo lưu vào thư mục
Pic_face_ID
 cv2.imwrite(filepath, face_image)
 print(f"Đã lưu ảnh nhận diện: {filepath}")
# Hàm chuyển chữ có dấu thành chữ không dấu
def remove_diacritics(input_str):
 return unidecode(input_str)
# Hàm ghi nhận điểm danh lịch sử thêm khuôn mặt vào hệ thống qua webcam (1)
def mark_attendance(name, mssv):
 try:
 with open("thamdu.csv", "a", encoding="utf-8") as f: # Thêm mã hóa
UTF-8
 now = datetime.now()
 dtstring = now.strftime("%H:%M:%S")
 f.writelines(f"\n{name},{mssv},{dtstring}")
 except Exception as e:
 print(f"Lỗi khi ghi vào tệp thamdu.csv: {e}")
#Hàm ghi lại lịch sử quét gương mặt điểm danh (Áp dụng cho cả 2 tính năng)
def log_recognition_history(name, mssv, method):
 with open(history_path, "a") as f:
 now = datetime.now()
 dtstring = now.strftime("%Y-%m-%d %H:%M:%S")
 f.write(f"{name},{mssv},{dtstring},{method}\n")
 print(f"Logged recognition: {name}, {mssv}, {dtstring}, {method}")
# Sao chép các ảnh từ thư mục card_path đến CARD_IMAGES_DIR (Tính năng 2)
CARD_IMAGES_DIR = "static/card_images"
if not os.path.exists(CARD_IMAGES_DIR): #Kiểm tra sự tồn tại của
thư mục và điều chuyển ảnh từ TMG đến TM xử lí
 os.makedirs(CARD_IMAGES_DIR)
for filename in os.listdir(card_path):
 if filename.endswith(".jpg") or filename.endswith(".png"):
#Kiểm tra đuôi hợp lệ
 shutil.copy(os.path.join(card_path, filename),
os.path.join(CARD_IMAGES_DIR, filename))
@app.route('/') #Chuyển sang dạng HTML dashboard hiển thị giao diện
def index():
 return render_template('index.html')
@app.route('/add_face')
def add_face():
 return render_template('add_face.html')
@app.route('/history')
def guide():
 return render_template('history.html')
@app.route('/get_csv_data/<filename>')
def get_csv_data(filename):
 csv_directory = os.path.dirname(os.path.abspath(__file__))
 file_path = os.path.join(csv_directory, filename + '.csv')
 try:
 if os.path.isfile(file_path):
 df = pd.read_csv(file_path, on_bad_lines='skip') # Sử dụng tham
số này để bỏ qua các dòng có lỗi
 csv_data = df.to_dict(orient='records')
 columns = df.columns.tolist()
 return jsonify(columns=columns, data=csv_data)
 else:
 error_message = f"File {filename}.csv not found at
{csv_directory}"
 print(error_message)
 return jsonify(error=error_message), 404
 except Exception as e:
 error_message = f"Error while processing file: {str(e)}"
 print(error_message)
 return jsonify(error=error_message), 500
@app.route('/info')
def info():
 return render_template('info.html')
@app.route('/set_mode', methods=['GET']) #Khởi tạo các chế độ
người dùng lựa chọn
def set_mode():
 mode = request.args.get('mode')
 if mode == 'recognize':
 return jsonify({"message": "Chế độ: Nhận diện khuôn mặt có sẵn từ
CSDL"}) #Tính năng 1
 elif mode == 'addNew':
 return jsonify({"message": "Chế độ: Thêm mới khuôn mặt qua webcam vào
CSDL"}) #Tính năng 1.2
 elif mode == 'recognizeWithCard':
 return jsonify({"message": "Chế độ: Nhận diện khuôn mặt với thẻ sinh
viên từ CSDL"}) #Tính năng 2
 return jsonify({"message": "Chế độ không hợp lệ"})
# Các hàm xử lí ảnh và nhận diện khuôn mặt (Tính năng 1)
def decode_base64_image(data_url):
 try:
 image_data = re.sub('^data:image/.+;base64,', '', data_url)
#Sử dụng biểu thức chính quy để loại bỏ tiền tố data:image/...;base64, để chỉ
lấy phần dữ liệu base64 của ảnh
 image_data = base64.b64decode(image_data)
#Dùng hàm base64.b64decode để chuyển dữ liệu từ dạng base64 sang dữ liệu nhị
phân.
 nparr = np.frombuffer(image_data, np.uint8)
#Tạo mảng numpy từ dữ liệu nhị phân, với kiểu dữ liệu là np.uint8
 img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#Sử dụng OpenCV để giải mã mảng numpy thành ảnh với định dạng màu BGR
 return img
 except Exception as e:
 print(f"Lỗi giải mã hình ảnh base64: {e}")
 return None #Có lỗi xảy ra trong quá
trình giải mã, in ra lỗi và trả về None
@app.route('/recognize_faces', methods=['POST'])
def recognize_faces():
 data = request.get_json()
 image_data = data.get('image')
 frame = decode_base64_image(image_data) #Nhận dữ liệu JSON
từ yêu cầu POST, lấy dữ liệu ảnh và giải mã bằng hàm decode_base64_image
 if frame is None:
 return jsonify({"status": "failed", "message": "Error decoding
image."})
 framS = cv2.resize(frame, (0, 0), None, fx=0.5, fy=0.5)
#Chỉnh kích thước ảnh xuống 50% và chuyển đổi từ định dạng BGR sang RGB.
 framS = cv2.cvtColor(framS, cv2.COLOR_BGR2RGB)
 face_cur_frame = face_recognition.face_locations(framS, model='hog')
#Tìm vị trí khuôn mặt trong ảnh và mã hóa thành vecto
 encode_cur_frame = face_recognition.face_encodings(framS)
 #Nếu không có hoặc có nhiều hơn một khuôn mặt trong ảnh, trả về thông báo
lỗi
 if len(encode_cur_frame) != 1:
 return jsonify({"status": "failed", "message": "CẢNH BÁO: Khuôn mặt
bị cản trở hoặc đang quá nhiều khuôn mặt trong webcam!"})
 recognized_name = None
 recognized_mssv = None
 encode_face = encode_cur_frame[0]
 face_loc = face_cur_frame[0]
 matches = face_recognition.compare_faces(encode_list_known, encode_face,
tolerance=0.3) #Độ chính xác của hệ thống nhận diện
 face_dis = face_recognition.face_distance(encode_list_known, encode_face)
 #Thuật toán xử lí mặt
 if True in matches:
 match_index = np.argmin(face_dis)
 y1, x2, y2, x1 = [v * 2 for v in face_loc] #Nhân các tọa độ vị
trí khuôn mặt với 2 để khôi phục kích thước gốc
 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) #vẽ
hcn xung quanh mặt
 name = class_names[match_index].upper()
 mssv = mssvs[match_index]
 cv2.putText(frame, f"{name} - {mssv}", (x1, y2 + 30),
cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2) #Hiển thị thông tin người
quét
 recognized_name = name
 recognized_mssv = mssv
 print(f"Đã nhận diện: {name}, MSSV: {mssv}")
 mark_attendance(name, mssv)
 log_recognition_history(name, mssv, "face")
 return jsonify({"status": "success", "message": f"Đã nhận diện:
{recognized_name}, MSSV: {recognized_mssv}", "redirect_url":
"https://forms.gle/Hvc976LJdcQwRFXD8"})
 else:
 print("Không tìm thấy khuôn mặt nào tương ứng.")
 return jsonify({"status": "failed", "message": "CẢNH BÁO: Không nhận
diện được khuôn mặt nào, vui lòng thử lại!"})
#Các hàm xử lí thêm mới khuôn mặt (Tính năng 1.2)
@app.route('/add_new_face', methods=['POST'])
def add_new_face():
 try:
 data = request.get_json()
 password = data.get('password')
 if password != ADMIN_PASSWORD:
 return jsonify({"message": "Mật khẩu không đúng. Truy cập bị từ
chối!"}), 403
 image_data = data.get('image')
 name = data.get('name')
 mssv = data.get('mssv')
 if not name or not mssv:
 return jsonify({"message": "Tên và MSSV không được để trống. Vui
lòng nhập đầy đủ thông tin!"}), 400
 # Kiểm tra xem MSSV có bị trùng không
 if mssv in mssvs:
 return jsonify({"message": "MSSV này đã tồn tại trong CSDL, vui
lòng nhập MSSV khác!"}), 400
 frame = decode_base64_image(image_data)
 if frame is None:
 return jsonify({"message": "Không thể giải mã hình ảnh. Vui lòng
thử lại."}), 400
 framS = cv2.resize(frame, (0, 0), None, fx=0.5, fy=0.5)
 framS = cv2.cvtColor(framS, cv2.COLOR_BGR2RGB)
 face_cur_frame = face_recognition.face_locations(framS)
 encode_cur_frame = face_recognition.face_encodings(framS)
 if not encode_cur_frame:
 return jsonify({"message": "Không tìm thấy khuôn mặt nào để thêm
vào CSDL, vui lòng thử lại!"}), 400
 face_loc = face_cur_frame[0]
 y1, x2, y2, x1 = [v * 2 for v in face_loc]
 face_width = x2 - x1
 face_height = y2 - y1
 # Kiểm tra độ rõ ràng của khuôn mặt
 if face_width < 100 or face_height < 100: # Tăng ngưỡng kiểm tra độ
rõ ràng
 return jsonify({"message": "Khuôn mặt không rõ ràng hoặc bị cản
trở. Vui lòng thử lại!"}), 400
 encode_face = encode_cur_frame[0]
 matches = face_recognition.compare_faces(encode_list_known,
encode_face, tolerance=0.4)
 if True in matches:
 return jsonify({"message": "Khuôn mặt này đã tồn tại trong CSDL,
vui lòng thao tác xóa trong CSDL nếu muốn thêm mới lại!"}), 400
 face_image = frame[y1:y2, x1:x2]
 save_image(face_image, name, mssv)
 print("Ảnh đã được lưu")
 # Lưu thông tin vào tệp thamdu.csv khi quét thành công
 with open("thamdu.csv", "a", encoding="utf-8") as f: # Thêm mã hóa
UTF-8
 now = datetime.now()
 dtstring = now.strftime("%H:%M:%S")
 f.write(f"{name},{mssv},{dtstring}\n")
 # Thêm khuôn mặt mới vào danh sách nhận diện CSDL
 face_images.append(frame)
 class_names.append(name)
 mssvs.append(mssv)
 encode_list_known.append(encode_face)
 return jsonify({"message": "Khuôn mặt của bạn đã được thêm vào
CSDL!"})
 except Exception as e:
 print(f"Lỗi: {e}")
 return jsonify({"message": f"Đã xảy ra lỗi: {e}"}), 500
#Các hàm xử lí nhận dạng qua thẻ sinh viên (Tính năng 2)
@app.route('/recognize_with_card', methods=['POST'])
def recognize_with_card():
 data = request.get_json()
 image_data = data.get('image')
 frame = decode_base64_image(image_data)
 if frame is None:
 return jsonify({"message": "CẢNH BÁO: Không thể giải mã hình ảnh. Vui
lòng thử lại!"}), 400
 framS = cv2.resize(frame, (0, 0), None, fx=0.5, fy=0.5)
 framS = cv2.cvtColor(framS, cv2.COLOR_BGR2RGB)
 face_cur_frame = face_recognition.face_locations(framS, model='hog')
 encode_cur_frame = face_recognition.face_encodings(framS)
 if len(encode_cur_frame) != 1:
 return jsonify({"message": "Khuôn mặt bị cản trở hoặc đang quá nhiều
khuôn mặt trong webcam!"})
 encode_face = encode_cur_frame[0]
 face_loc = face_cur_frame[0]
 matches = face_recognition.compare_faces(encode_list_cards, encode_face,
tolerance=0.5)
 face_dis = face_recognition.face_distance(encode_list_cards, encode_face)
 print("Face distances:", face_dis)
 if True in matches:
 match_index = np.argmin(face_dis)
 name = card_names[match_index]
 mssv = card_mssvs[match_index]
 recognized_name = name.upper()
 recognized_mssv = mssv
 print(f"Đã nhận diện: {recognized_name}, MSSV: {recognized_mssv}")
 card_image_url = f"/static/card_images/{card_list[match_index]}"
 redirect_url = "https://forms.gle/Hvc976LJdcQwRFXD8" # Đường dẫn
chuyển hướng khi nhận diện thành công
 log_recognition_history(name, mssv, "card")
 return jsonify({
 "status": "success",
 "message": f"Đã nhận diện: {recognized_name}, MSSV:
{recognized_mssv}",
 "name": recognized_name,
 "mssv": recognized_mssv,
 "card_image_url": card_image_url,
 "redirect_url": redirect_url # Thêm trường redirect_url vào phản
hồi
 })
 else:
 print("Không tìm thấy khuôn mặt nào tương ứng trong thư viện thẻ sinh
viên.")
 return jsonify({"message": "Không nhận diện được khuôn mặt nào tương ứng
trong thư viện thẻ sinh viên."})
if __name__ == '__main__':
 app.run(debug=True)
