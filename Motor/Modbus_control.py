from pymodbus.client import ModbusSerialClient
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading

class MotorController:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, device_id=100):
        """
        모터 컨트롤러 초기화
        :param port: USB 포트 경로 (예: /dev/ttyUSB0)
        :param baudrate: 통신 속도 (기본값: 115200)
        :param device_id: Device ID
        """
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1
        )
        self.device_id = device_id
        self.lock = threading.Lock()

    def connect(self):
        """MODBUS-RTU 연결"""
        return self.client.connect()

    def close(self):
        """연결 종료"""
        self.client.close()

    def read_register(self, address, count=1):
        """
        레지스터 읽기
        :param address: 시작 레지스터 주소
        :param count: 읽을 레지스터 개수
        :return: 읽은 데이터 리스트
        """
        try:
            with self.lock:
                response = self.client.read_holding_registers(address=address, count=count, slave=self.device_id)
            if response and not response.isError():
                return response.registers
            else:
                print(f"[Error] Failed to read register at {hex(address)}")
                return None
        except Exception as e:
            print(f"[Exception] Exception while reading register: {e}")
            return None

    def write_register(self, address, value):
        """
        레지스터 쓰기
        :param address: 대상 레지스터 주소
        :param value: 쓰기 값
        :return: 성공 여부
        """
        try:
            with self.lock:
                response = self.client.write_register(address=address, value=value, slave=self.device_id)
            if response and not response.isError():
                return True
            else:
                print(f"[Error] Failed to write register at {hex(address)}")
                return False
        except Exception as e:
            print(f"[Exception] Exception while writing register: {e}")
            return False

    # 속도 설정
    def set_speed(self, speed):
        if 0 <= speed <= 1000 or speed >= 1001:
            return self.write_register(0x0001, speed)
        else:
            print("[Error] Invalid speed value. Must be 0-1000 or >=1001")
            return False

    # CW/CCW 설정
    def set_cw_ccw(self, direction):
        if direction in [0, 1]:
            return self.write_register(0x0002, direction)
        else:
            print("[Error] Invalid direction. Must be 0 (CW) or 1 (CCW)")
            return False

    # 모터 시작/정지 설정
    def set_enable(self, enable):
        if enable in [0, 1]:
            return self.write_register(0x0003, enable)
        else:
            print("[Error] Invalid enable value. Must be 0 (Stop) or 1 (Start)")
            return False

    # 브레이크 설정
    def set_brake(self, brake):
        if brake in [0, 1]:
            return self.write_register(0x0004, brake)
        else:
            print("[Error] Invalid brake value. Must be 0 (OFF) or 1 (ON)")
            return False

    # 현재 속도 읽기
    def get_current_speed(self):
        return self.read_register(0x0007)

    # 현재 CW/CCW 값 읽기
    def get_current_cw_ccw(self):
        return self.read_register(0x0008)

    # 현재 모터 상태 읽기
    def get_motor_fault(self):
        return self.read_register(0x0017)

    # 현재 전류 읽기
    def get_current(self):
        return self.read_register(0x000B)  # Assuming 0x000B is current

    # 현재 RPM 읽기
    def get_current_RPM(self):
        return self.read_register(0x0015)

def motor_control(motor, run_event, direction_lock, current_direction, startup_delay=5):
    """
    모터를 설정하고 모니터링하여 RPM이 0일 경우 방향을 반전시키는 함수
    :param motor: MotorController 인스턴스
    :param run_event: 종료 이벤트
    :param direction_lock: 방향 변경 시 사용되는 락
    :param current_direction: 현재 방향을 저장하는 리스트
    :param startup_delay: 모터 시작 후 RPM 모니터링 시작까지의 지연 시간 (초)
    """
    while not run_event.is_set():
        # 브레이크 해제
        print("[Control] Disabling brake")
        if motor.set_brake(0):
            print("[Control] Brake disabled")
        else:
            print("[Control] Failed to disable brake")
        time.sleep(0.5)
        
        # 속도 설정 (고정값 100)
        speed_value = 100  # 고정 속도
        if motor.set_speed(speed_value):
            print(f"[Control] Speed set to {speed_value}")
            speed = motor.read_register(0x0001)
            print(f"[Control] Speed register value: {speed}")
        else:
            print("[Control] Failed to set speed")
        
        time.sleep(0.5)
        
        # CW/CCW 설정
        with direction_lock:
            direction = current_direction[0]
        if motor.set_cw_ccw(direction):
            print(f"[Control] Direction set to {'CW' if direction == 0 else 'CCW'}")
        else:
            print("[Control] Failed to set direction")
        
        time.sleep(0.5)
        
        # 모터 시작
        if motor.set_enable(1):
            print("[Control] Motor started")
        else:
            print("[Control] Failed to start motor")
        
        # 모터 동작 중 상태 확인
        start_time = time.time()
        print(f"[Control] Waiting {startup_delay} seconds before monitoring RPM")
        time.sleep(startup_delay)
        print("[Control] Starting RPM monitoring")

        try:
            while not run_event.is_set():
                # 현재 RPM 및 상태 확인
                current_rpm = motor.get_current_RPM()
                if current_rpm:
                    rpm_value = current_rpm[0]
                    print(f"[Control] Current RPM: {rpm_value}")
                    
                    if rpm_value == 0:
                        print("[Control] RPM is 0. Reversing direction.")
                        # 모터 정지
                        print("[Control] Stopping motor to change direction")
                        if motor.set_enable(0): # brake ?
                            print("[Control] Motor stopped")
                        else:
                            print("[Control] Failed to stop motor")
                        time.sleep(0.2)
                        
                        # 방향 반전
                        with direction_lock:
                            new_direction = 1 - current_direction[0]
                            current_direction[0] = new_direction
                            print(f"[Control] Reversing direction to {'CW' if new_direction == 0 else 'CCW'}")
                        
                        # 방향 반전 후 모터 재시작
                        print("[Control] Restarting motor with new direction")
                        if motor.set_enable(1):
                            print("[Control] Motor re-enabled")
                        else:
                            print("[Control] Failed to re-enable motor")
                        
                        # 루프 재시작
                        break

                fault_status = motor.get_motor_fault()
                if fault_status:
                    print(f"[Control] Motor fault status: {'Normal' if fault_status[0] == 0 else 'Fault'}")
                time.sleep(1)
        except Exception as e:
            print(f"[Control] Exception in motor_control: {e}")
        
        # 모터 정지
        print("[Control] Stopping motor")
        if motor.set_enable(0):
            print("[Control] Motor stopped")
        else:
            print("[Control] Failed to stop motor")
        
        # 브레이크 활성화
        print("[Control] Engaging brake")
        if motor.set_brake(1):
            print("[Control] Brake engaged")
        else:
            print("[Control] Failed to engage brake")
        
        # 잠시 대기 후 루프 재시작
        time.sleep(1)

def plot_rpm(motor, run_event, run_time=20):
    """
    실시간으로 모터의 RPM을 플로팅하는 함수
    :param motor: MotorController 인스턴스
    :param run_event: 종료 이벤트
    :param run_time: 플로팅을 지속할 시간 (초)
    """
    x_data = []
    y_data = []
    start_time = time.time()

    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'b-', label="RPM")
    ax.set_xlim(0, run_time)
    ax.set_ylim(0, 5000)  # 예상 RPM 범위에 맞게 조정
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("RPM")
    ax.set_title("Real-Time Motor RPM")
    ax.legend(loc='upper left')

    def update(frame):
        if run_event.is_set():
            plt.close()
            return line,
        current_time = time.time() - start_time
        if current_time > run_time:
            ax.set_xlim(current_time - run_time, current_time)
        else:
            ax.set_xlim(0, run_time)
        
        current_register = motor.get_current_RPM()
        if current_register:
            rpm_value = current_register[0]
            x_data.append(current_time)
            y_data.append(rpm_value)
            ax.relim()
            ax.autoscale_view()
            line.set_data(x_data, y_data)
            print(f"[Plot] Time: {current_time:.2f}s, RPM: {rpm_value}")
        return line,

    # FuncAnimation must run in main thread
    ani = FuncAnimation(fig, update, interval=1000, blit=False)
    plt.show()

    # Set run_event to stop motor_control thread
    run_event.set()

if __name__ == "__main__":
    motor = MotorController(port="/dev/ttyUSB0")  # 포트 경로를 실제 환경에 맞게 수정하세요

    if motor.connect():
        print("[Main] MODBUS-RTU 연결 성공!")
        
        run_time = 20  # 모터 동작 및 플로팅 시간 (초)
        run_event = threading.Event()
        direction_lock = threading.Lock()
        current_direction = [0]  # 초기 방향: 0 (CW)

        # 모터 제어를 별도의 스레드에서 실행
        motor_thread = threading.Thread(target=motor_control, args=(motor, run_event, direction_lock, current_direction))
        motor_thread.start()
        
        try:
            # 메인 스레드에서 실시간 RPM 플로팅 시작
            plot_rpm(motor, run_event, run_time)
        except KeyboardInterrupt:
            print("[Main] Interrupted by user.")
            run_event.set()
        
        # 모터 제어 스레드가 종료될 때까지 대기
        motor_thread.join()
        
        # 연결 종료
        motor.close()
        print("[Main] MODBUS-RTU 연결 종료")
    else:
        print("[Main] MODBUS-RTU 연결 실패")

"""
# 이동 평균 필터 아이디어 설명

# 현재 코드는 RPM이 0일 경우 즉시 방향을 반전시킵니다.
# 하지만 때때로 RPM이 일시적으로 0일 수 있어, 지속적인 0 상태를 확인하는 것이 중요합니다.
# 이를 위해 이동 평균 필터를 사용할 수 있습니다.

# 예를 들어, 최근 N개의 RPM 값을 저장하는 deque를 사용하여 이동 평균을 계산합니다.
# 만약 이 이동 평균이 특정 임계값(예: 0 이하)이라면, 방향을 반전시킵니다.
# 이렇게 하면 RPM이 일시적으로 낮아져도 방향 반전이 발생하지 않고, 
# 지속적으로 RPM이 낮을 때만 반전됩니다.

# 코드 예시:
# from collections import deque

# rpm_buffer = deque(maxlen=2)  # 최근 2초 동안의 RPM 값을 저장

# while not run_event.is_set():
#     current_rpm = motor.get_current_RPM()
#     if current_rpm:
#         rpm_value = current_rpm[0]
#         rpm_buffer.append(rpm_value)
#         if len(rpm_buffer) == rpm_buffer.maxlen:
#             avg_rpm = sum(rpm_buffer) / len(rpm_buffer)
#             if avg_rpm == 0:
#                 # 방향 반전 로직 실행
#                 pass
#     time.sleep(1)
"""
