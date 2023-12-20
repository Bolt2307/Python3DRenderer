# Linux shell script to download python dependencies
echo "Downloading python3"
sudo apt install python3
echo "Downloading python dependencies..."
pip3 install pygame
pip3 install pillow
echo "Done."
