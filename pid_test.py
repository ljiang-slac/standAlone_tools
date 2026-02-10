import numpy as np
import matplotlib.pyplot as plt

def pid_control(Kp, Ki, Kd, setpoint, initial_temp, time_steps=2000, dt=0.1, max_u=200.0):
    temp = initial_temp
    integral = 0
    prev_error = 0
    times = np.arange(0, time_steps * dt, dt)
    temps = [temp]
    
    for t in range(1, time_steps):
        error = setpoint - temp
        integral += error * dt
        derivative = (error - prev_error) / dt
        u = Kp * error + Ki * integral + Kd * derivative
        u = max(0, min(max_u, u))  #
        temp += dt * (-temp + u)
        temps.append(temp)
        prev_error = error
    
    return times, np.array(temps)

# enter the parameters
initial_temp = float(input("Enter the start temperature (e.g., 20.0): "))
setpoint = float(input("Enter the setpoint (target temperature, e.g., 100.0): "))
num_tests = int(input("How many parameter sets do you want to test? (including the Base): "))

# collect parameters
params = {}
names = ['Base'] + [f'Test {i}' for i in range(1, num_tests)]
for i in range(num_tests):
    print(f"\nEnter parameters for {names[i]}:")
    Kp = float(input("Kp: "))
    Ki = float(input("Ki: "))
    Kd = float(input("Kd: "))
    params[names[i]] = (Kp, Ki, Kd)

# define the colors
colors = ['blue', 'green', 'red', 'orange', 'cyan', 'magenta', 'black', 'purple']

# 
results = {}
plt.figure(figsize=(12, 8))
for idx, (name, (Kp, Ki, Kd)) in enumerate(params.items()):
    times, temps = pid_control(Kp, Ki, Kd, setpoint, initial_temp)
    results[name] = (times, temps)
    color = colors[idx % len(colors)]
    plt.plot(times, temps, label=f'{name} (Kp={Kp}, Ki={Ki}, Kd={Kd})', color=color)

plt.axhline(y=setpoint, color='black', linestyle='--', label=f'Setpoint ({setpoint}°C)')
plt.title('PID Controller Temperature Response Comparison')
plt.xlabel('Time (seconds)')
plt.ylabel('Temperature (°C)')
plt.legend(loc='lower right')
plt.grid(True)
plt.show()  # 
# plt.savefig('pid_plot.png')  #

#
print("\nSample temperatures over time (every 10s, up to 90s):")
header = "Time(s)"
for name in names:
    header += f" | {name}"
print(header)
interval = 100  # Every 10 s
for i in range(0, 1000, interval):  # only print the table at the beginning 100 seconds
    t = results[names[0]][0][i]
    row = f"{t:.1f}"
    for name in names:
        row += f" | {results[name][1][i]:.1f}"
    print(row)

# 
print("\nFinal temperatures (at 199.9s):")
for name in names:
    print(f"{name}: {results[name][1][-1]:.1f}")
