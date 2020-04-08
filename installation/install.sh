echo "Installing dependencies"
sudo apt-get update
sudo apt-get install -y git hping3
sudo apt-get install -yq python-pip
sudo apt-get install net-tools

echo "Installing mininet"
./install_mininet.sh

echo "Installing Ryu"
./install_ryu.sh