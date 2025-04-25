from mytest import run_tests
from event_utils import EventQueue, EventDeque, TestEventQueue, ProfileEventQueue
from myprofiler import run_profiles, ProfileExample

run_tests(TestEventQueue, EventQueue)
run_tests(TestEventQueue, EventDeque)

run_profiles(ProfileEventQueue, 20, EventQueue, 100) # always faster
run_profiles(ProfileEventQueue, 20, EventDeque, 100)