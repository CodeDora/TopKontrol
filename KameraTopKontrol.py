import cv2
import mediapipe as mp
import numpy as np

# Mediapipe el tespit modelini başlatmak için kullan
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Ekran genişliği ve yüksekliği ayarlamak için(camera)
screen_width, screen_height = 640, 480

# Topun başlangıç konumu ve hızı düzenlemek için gerekli kısım
ball_radius = 20
ball_x, ball_y = screen_width // 2, screen_height // 2
ball_speed_x, ball_speed_y = 0, 0
gravity = 1  # Yer çekimi değeri

# Başlangıçta el topu tutmuyor
hand_is_open = False

# Renk değiştirme için başlangıç renk
ball_color = (0, 255, 0)  # Başlangıçta yeşil renk olarak ayarla

# Başlangıçta topun boyutunu ayarla
ball_size = 20

# Başlangıçta bildirim metni
notification_text = ""

# Webcam başlat
cap = cv2.VideoCapture(0)
cap.set(3, screen_width)
cap.set(4, screen_height)

while True:
    # Kameradan bir kare al
    ret, frame = cap.read()

    # Frame'i ters çevir (eğer istiyorsanız)
    frame = cv2.flip(frame, 1)

    # Frame'i RGB'ye dönüştür (Mediapipe el tespiti için)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Mediapipe el tespitini uygula
    results = hands.process(rgb_frame)

    # El tespiti sonuçlarını işle
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # El açık mı kapalı mı kontrolü
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            hand_is_open = thumb_tip < index_tip

            # İşaret ve baş parmak pozisyonları
            thumb_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * screen_width)
            thumb_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * screen_height)
            index_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * screen_width)
            index_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * screen_height)

            # Topu tutma durumuna göre konum ve hızı güncelle
            if hand_is_open:
                ball_x, ball_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
                ball_speed_x = (index_x - thumb_x) // 10
                ball_speed_y = (index_y - thumb_y) // 10
            else:
                # El topu bıraktıysa, yer çekimini etkile
                ball_speed_y += gravity

    # Topun hareketini güncelle
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Kameranın sınırlarına çarptığında seken top
    if ball_x - ball_radius <= 0 or ball_x + ball_radius >= screen_width:
        ball_speed_x *= -1
    if ball_y - ball_radius <= 0 or ball_y + ball_radius >= screen_height:
        ball_speed_y *= -1

    # Topu çiz
    cv2.circle(frame, (ball_x, ball_y), ball_size, ball_color, -1)

    # Bildirim metni çiz
    cv2.putText(frame, notification_text, (screen_width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    # Frame'i göster
    cv2.imshow('Virtual Ball', frame)

    # Renk değiştirme tuşu (örneğin 'c' tuşuna basıldığında)
    if cv2.waitKey(1) & 0xFF == ord('c'):
        # Rastgele renk üret
        ball_color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
        notification_text = "Top rengi değisti!"
    # Boyut artırma tuşu (örneğin 'b' tuşuna basıldığında)
    if cv2.waitKey(1) & 0xFF == ord('b'):
        ball_size += 5
        notification_text = "Top buyudu!"
    # Boyut azaltma tuşu (örneğin 'k' tuşuna basıldığında)
    if cv2.waitKey(1) & 0xFF == ord('k'):
        ball_size = max(5, ball_size - 5)
        notification_text = "Top kuculdu!"
    # Çıkış için 'q' tuşuna basın
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
# Kaynakları serbest bırak
cap.release()
cv2.destroyAllWindows()
