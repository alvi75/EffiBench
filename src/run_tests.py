import subprocess

try:
    # Run your script (change `your_script.py` to your actual script filename)
    subprocess.run(["python", "2836.py"], check=True)
    print("\n✅ All tests passed successfully!")
except subprocess.CalledProcessError:
    print("\n❌ Some tests failed! Check the assertion errors in the output.")
