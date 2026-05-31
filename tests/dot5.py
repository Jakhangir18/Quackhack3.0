import sys
sys.path.insert(0, __file__.rsplit("/tests", 1)[0])
from output.motors import buzz_dot, motors

try:
    buzz_dot(5)
finally:
    for m in motors.values():
        m.off()
        m.close()
