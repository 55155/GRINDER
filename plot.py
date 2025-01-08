import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ====== 사용자가 직접 맞춰야 할 변수들 ======
PORT = 'COM10'        # Windows 예: COM3 / Mac, Linux 예: '/dev/ttyUSB0', '/dev/ttyACM0' 등
BAUD_RATE = 115200     # 115200
REFRESH_INTERVAL = 100  # 그래프 업데이트 주기 (ms)

# ====== 전역 변수 ======
# 그래프에 보여줄 데이터를 담을 리스트
x_data = []
y1_data = []
y2_data = []
y3_data = []
# 시리얼 객체 열기
ser = serial.Serial(PORT, BAUD_RATE, timeout=1) # PORT , BAUD_RATE, timeout
start_time = time.time()

# ====== 애니메이션 업데이트 함수 ======
def update(frame):
    """
    Matplotlib의 FuncAnimation이 주기적으로 호출하는 함수
    새 데이터를 읽고, 그래프를 갱신한다.
    """

    # 시리얼에서 한 줄 읽기
    line = ser.readline().decode('utf-8').strip()

    # 예: "123,456"
    if line: # line 이 들어왔으면, 
        # 쉼표 분리
        parts = line.split(',') # ,을 기준으로 두 구간 분리 
        if len(parts) == 3: # length가 2이면, 
            try:
                val1 = float(parts[0])
                val2 = float(parts[1])
                val3 = float(parts[2])
            except ValueError:
                # float 변환이 안될 때, timestep 하나 건너 뛰기
                return

            # 실제 시간 계산
            current_time = time.time() - start_time
            # 시간축으로 x_data를 늘린다. (카운트업 or 실제 시간 등)
            # 여기서는 단순히 len(x_data)로 증가시킴
            x_data.append( current_time ) # 10ms 
            y1_data.append(val1)
            y2_data.append(val2)
            y3_data.append(val3)

            # 그래프가 너무 길어지면 앞쪽 데이터를 제거할 수도 있음
            if len(x_data) > 200:  # 200개까지만 저장 // 200 개의 점들까지만 정리
                x_data.pop(0)
                y1_data.pop(0)
                y2_data.pop(0)
                y3_data.pop(0) # 0 번째 data 제거하면서 200개 유지

            # 라인 데이터 업데이트
            line1.set_data(x_data, y1_data)
            line2.set_data(x_data, y2_data)
            line3.set_data(x_data, y3_data)

            # x축, y축 범위 재조정
            ax.relim()
            ax.autoscale_view()

    return line1, line2, line3

# ====== 메인 프로그램 ======
# 그림/축/라인 초기화
fig, ax = plt.subplots()

line1, = ax.plot([], [], 'r-', label="Hall A")
line2, = ax.plot([], [], 'b-', label="Hall B")
line3, = ax.plot([], [], 'g-', label="Hall C")

# 범례 표시
ax.legend(loc='upper left')
ax.set_xlabel("Time (s)")   # X축 레이블을 'Time (seconds)'로
ax.set_ylabel("Value")      # Y축 레이블 (원하는 대로 설정 가능)

# 애니메이션
ani = FuncAnimation(fig, update, interval=REFRESH_INTERVAL, blit=True)

try:
    plt.show()
except KeyboardInterrupt:
    pass
finally:
    ser.close()
