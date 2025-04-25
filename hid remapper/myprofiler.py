import time
import gc
gc.enable()

def run_profiles(profile_class, N, *args, **kwargs):
    instance = profile_class(*args, **kwargs)
    timings = {}

    # Find all setup and profile functions
    setup_methods = {
        name[6:]: getattr(instance, name)
        for name in dir(instance)
        if name.startswith("setup_") and callable(getattr(instance, name))
    }
    profile_methods = {
        name[8:]: getattr(instance, name)
        for name in dir(instance)
        if name.startswith("profile_") and callable(getattr(instance, name))
    }

    # Match and run
    for key in setup_methods:
        if key in profile_methods:
            setup_func = setup_methods[key]
            profile_func = profile_methods[key]
            
            # Setup
            env = setup_func()

            # Profile multiple times
            total_time = 0.0
            for _ in range(N):
                gc.collect()
                start = time.monotonic()
                profile_func(env)
                end = time.monotonic()
                total_time += (end - start)
                gc.collect()
            timings[key] = total_time
        else:
            print(f"Warning: No matching profile function for setup_{key}")

    # Print the report
    print("\n\nProfile Report: ", profile_class.__name__, *args, **kwargs)
    for key, total_time in timings.items():
        avg_time = total_time / N
        print(f"{key}: Total Time = {total_time}s, Average Time = {avg_time}s")

class ProfileExample:
    def __init__(self, base=0):
        self.base = base

    def setup_addition(self):
        return 10

    def profile_addition(self, env):
        return env + self.base

    def setup_multiplication(self):
        return 5

    def profile_multiplication(self, env):
        return env * self.base
