@echo off

echo =========================
echo Creating virtual environment
echo =========================

python -m venv venv

echo =========================
echo Activating environment
echo =========================

call venv\Scripts\activate

echo =========================
echo Installing packages
echo =========================

pip install --upgrade pip
pip install -r requirements.txt

echo =========================
echo Installation Complete
echo =========================

pause